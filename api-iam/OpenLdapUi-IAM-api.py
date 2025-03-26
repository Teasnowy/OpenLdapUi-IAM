from flask import Flask, request
import argparse
import json
import os
import logging
from lib.db.db_select import kvdb
from lib.db.exec_ql import MysqlPool
from lib.config.config_server import get_config, get_config_once
from lib.crontab.crontab import BackgroundScheduler, put_routes
# 引用自定义路由
from lib.routes.user_auth import routes_user_auth
from lib.routes.ldap import routes_ldap
from lib.routes.setting import routes_setting
from lib.routes.ldap_servers import ldap_servers


app = Flask(__name__)
# 注册蓝图
app.register_blueprint(routes_user_auth)
app.register_blueprint(routes_ldap)
app.register_blueprint(routes_setting)
app.register_blueprint(ldap_servers)


@app.route('/ipput', endpoint="获取来访地址")
def index():
    # 获取来访地址
    ip = request.remote_addr
    with open('/app/ipupdate/data', 'w') as tmp:
        tmp.write(ip)
    return ip + '\n'


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s:%(filename)s:%(funcName)s:%(thread)d:%(lineno)d %(message)s",
        encoding='utf-8'
    )

    # 获取脚本所在路径
    # dir_app = os.path.dirname(sys.argv[0])
    dir_app = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description='提供给k8s微服务间的实验镜像')
    parser.add_argument('-s', type=str, required=False, help='服务名称', default="devops-api")
    parser.add_argument('-p', type=int, required=False, help='监听端口号', default=997)
    parser.add_argument('-m', type=str, required=False, choices=["local", "nacos"],
                        help='配置模式, 支持本地local和远程nacos', default="local")
    parser.add_argument('-f', type=str, required=False,
                        help='指定的配置文件, 注意: 当-m为nacos时, 此文件内除nacos之外的配置都将无效',
                        default=f"{dir_app}/config/global.yaml")
    parser.add_argument('-d', type=str, required=False, choices=["redis", "diskcache"],
                        help='指定的键值数据库, 注意: 当-d为redis时, 需要配置文件(或nacos)内具有redis配置',
                        default="diskcache")
    input_args = parser.parse_args()

    servername = input_args.s
    port = input_args.p
    config_mode = input_args.m
    config_filename_global = input_args.f
    db_mode = input_args.d

    # 如果配置了环境变量, 则config_mode和db_mode以环境变量优先级最高
    if os.environ.get("UIIAM_CONFIG_MODE"):
        config_mode = os.environ.get("UIIAM_CONFIG_MODE")
        logging.info(f"检测到系统环境变量UIIAM_CONFIG_MODE, 启用了{config_mode}为配置主体")
    if os.environ.get("UIIAM_DB_MODE"):
        db_mode = os.environ.get("UIIAM_DB_MODE")
        logging.info(f"检测到系统环境变量UIIAM_DB_MODE, 启用了{db_mode}为配置主体")

    logging.info(f"启用了{config_mode}为配置主体")
    logging.info(f"启用了{db_mode}为键值数据库")

    # 进入脚本所在路径
    os.chdir(dir_app)

    # 删除db下的缓存
    path_db = f"{dir_app}/db"
    if os.path.isdir(path_db):
        for filename in os.listdir(path_db):
            file_path = os.path.join(path_db, filename)
            # 如果是文件而不是目录，则删除
            if os.path.isfile(file_path):
                os.remove(file_path)
                logging.info(f"删除{path_db}缓存数据: {file_path}")

    # 读取配置, 用来加载键值数据库
    cf_tmp = get_config_once(config_filename_global, config_mode)
    # 初始化内置键值数据库
    if db_mode == 'redis':
        kv = kvdb(db_type=db_mode, conf=cf_tmp["redis"])
    else:
        kv = kvdb(db_type=db_mode)

    # 将配置文件绝对路径传入缓存
    kv.set(k="config_filename_global", v=config_filename_global)
    # 将用户选择的配置模式写入缓存
    kv.set(k="config_mode", v=config_mode)

    # 定时任务的第一次执行
    # 第一次读取并上传配置
    get_config()

    # 第一次获取全局配置
    cf = kv.read()
    # 获取主数据库配置
    cf_database = cf["database"]
    # 优先采用系统环境变量的数据库信息
    if os.environ.get("MYSQL_HOST"):
        logging.info("检测到系统环境变量MYSQL_HOST")
        cf_database["host"] = os.environ.get("MYSQL_HOST")
    if os.environ.get("MYSQL_PORT"):
        logging.info("检测到系统环境变量MYSQL_PORT")
        cf_database["port"] = int(os.environ.get("MYSQL_PORT"))
    if os.environ.get("MYSQL_USER"):
        logging.info("检测到系统环境变量MYSQL_USER")
        cf_database["user"] = os.environ.get("MYSQL_USER")
    if os.environ.get("MYSQL_PASSWORD"):
        logging.info("检测到系统环境变量MYSQL_PASSWORD")
        cf_database["password"] = os.environ.get("MYSQL_PASSWORD")
    if os.environ.get("MYSQL_DB"):
        logging.info("检测到系统环境变量MYSQL_DB")
        cf_database["db"] = os.environ.get("MYSQL_DB")
    if os.environ.get("MYSQL_CHARSET"):
        logging.info("检测到系统环境变量MYSQL_CHARSET")
        cf_database["charset"] = os.environ.get("MYSQL_CHARSET")
    if os.environ.get("MYSQL_MAXCONNECTIONS"):
        logging.info("检测到系统环境变量MYSQL_MAXCONNECTIONS")
        cf_database["maxconnections"] = os.environ.get("MYSQL_MAXCONNECTIONS")


    # 初始化数据库连接池
    MysqlPool().create(**cf_database)

    # 定义定时任务
    dict_cron_defs = {
        "获取全局配置": {
            "info": "",
            "def": get_config,
            "seconds": 60,
            "args": {},
        },
    }
    # 创建定时任务实例
    sc = BackgroundScheduler(timezone='Asia/Shanghai')

    logging.info("加载所有基础定时任务")
    for job_name, job_conf in dict_cron_defs.items():
        sc.add_job(
            func=job_conf["def"], trigger='interval', id=job_name, name=job_name,
            kwargs=job_conf["args"], seconds=job_conf["seconds"]
        )
    # 发起所有任务
    sc.start()

    # 测试
    # k = 'num_auth_local_dcj'
    # logging.info(kv.check(k))
    # kv.incr(1, k, expire=10)
    # time.sleep(2)
    # logging.info(kv.read(k, expire_time=True))
    # time.sleep(3)
    # logging.info(kv.check(k))
    # kv.incr(1, k, touch=True)
    # logging.info(kv.read(k, expire_time=True))

    # 将本程序所有URL信息上传数据库
    put_routes(app)
    # for r in list_routes:
    #     rs = f"Endpoint: {r['endpoint']}, URL: {r['url']}, Methods: {', '.join(r['methods'])}"
    #     print(rs)

    app.run(host="0.0.0.0", port=port)




