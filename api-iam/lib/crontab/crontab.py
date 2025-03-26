from ..singleton import singleton
from ..data_format import res_format
from apscheduler.schedulers.background import BackgroundScheduler as APBackgroundScheduler
from ..db.exec_ql import MysqlPool
import re
import logging


@singleton
class BackgroundScheduler:
    """
    重新封装的apscheduler任务系统, 做成了单实例
    """
    def __init__(self, timezone='Asia/Shanghai'):
        # 创建APScheduler的背景调度器实例
        self.scheduler = APBackgroundScheduler(timezone=timezone)

    # 这里依然要重写__new__, 是为了添加*args, **kw, 不然使用了装饰器后不能传参了
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance

    def start(self):
        self.scheduler.start()

    def add_job(self, func, trigger, **kwargs):
        self.scheduler.add_job(func, trigger, **kwargs)

    def get_jobs(self):
        return self.scheduler.get_jobs()

    def shutdown(self):
        self.scheduler.shutdown()


def crontab_jobs(data):
    """
    后续操作定时任务的入口
    :param data:
    :return:
    """
    # sc = kvdb().read("object_apsc")
    sc = BackgroundScheduler()
    # 提取操作类型
    modify_type = data["type"]

    # 各种操作类型的分支
    if modify_type == "check":
        # 如果是查看所有任务
        res = job_get(sc)

    else:
        return res_format(err="操作类型不支持")

    return res_format(res)


def job_get(sc):
    """
    获取后台所有任务的运行状态
    :param sc:
    :return:
    """
    list_jobs = []
    for i in sc.get_jobs():
        next_runtime_tmp = i.next_run_time
        if i.next_run_time:
            next_runtime_strftime = next_runtime_tmp.strftime('%Y-%m-%d %H:%M:%S')
        else:
            next_runtime_strftime = None
        dict_job = {
            "next_run_time": next_runtime_tmp,
            "next_run_time_strftime": next_runtime_strftime,
            "name": i.name,
            "id": i.id,
            "args": i.args,
            "func": i.func.__name__,
            "trigger": str(i.trigger)
        }
        list_jobs.append(dict_job)
    return list_jobs


def put_routes(app):
    """
    获取所有flask监听的url信息, 并写入数据库 (要求所有接口的endpoint不能重名, endpoint是主键)
    :param app: flask的主方法, 如: app = Flask(__name__), Flask()是单实例的
    :return:
    """
    routes = {}
    for rule in app.url_map.iter_rules():
        # print(vars(rule))
        url = rule.rule
        endpoint = re.split(r'\.', rule.endpoint)[-1]
        if endpoint in routes.keys():
            raise ZeroDivisionError(f"接口{url}与{routes[endpoint]['url']}都为{endpoint}, 这是不可以的")
        routes[endpoint] = {
            # URL
            "url": url,
            # URL 对应的备注(定义url时定义的endpoint), 默认为视图函数的名称, 这里以点号为分隔取最后一段, 去掉可能存在的蓝图名字
            "endpoint": endpoint,
            # 支持的 HTTP 方法
            "methods": list(rule.methods)
        }

    # 初始化数据库
    mp = MysqlPool()
    # 清空接口配置表
    mp.transaction("truncate table sw_interface;")
    logging.info("已清空接口详情表")

    # 定义sql数据部分
    sql_insert_data = {}
    # 拼接sql模板
    n = 1
    sql_insert_tem_values = []
    for v in routes.values():
        sql_insert_tem_values.append(f"\n\t\t\t(null, %(endpoint_{n})s, %(url_{n})s, %(methods_{n})s, now(), now())")
        sql_insert_data[f"endpoint_{n}"] = v["endpoint"]
        sql_insert_data[f"url_{n}"] = v["url"]
        sql_insert_data[f"methods_{n}"] = ','.join(v["methods"])
        n += 1
    sql_insert_tem = f"""
        insert into sw_interface 
            (interface_id, api_endpoint, api_url, api_methods, date_create, date_update) 
        values {','.join(sql_insert_tem_values)};
    """
    # print(sql_insert_tem)
    # print(sql_insert_data)
    mp.transaction(sql_insert_tem, sql_insert_data)

    # 清空角色关联表中已经不存在的interface
    sql_delete_tem = "delete from sw_roleinterface where api_url not in %(list_apis)s"
    sql_delete_data = {
        "list_apis": [v["url"] for k,v in routes.items()]
    }
    mp.transaction(sql_delete_tem, sql_delete_data)

    logging.info("已上传所有接口详情至数据库")


def get_routes(data_req):
    """
    返回后端接口的信息
    :param data_req:
    :return:
    """

    # 初始化数据库连接池
    mp = MysqlPool()

    sql_select_tem = """
            select i.interface_id,i.api_url,i.api_endpoint,i.api_methods,i.date_create, i.date_update from sw_interface i;
        """

    # 查询并返回结果
    list_res_db = mp.fetch_all(sql_select_tem)

    data_res = {}
    for i in list_res_db:
        data_res[i["api_url"]] = i

    return data_res