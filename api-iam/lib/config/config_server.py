from ..db.db_select import *
from .nacosconf import *
import logging
from ruamel.yaml import YAML


# 获取全局的配置
def get_config():
    """
    获取配置的定时任务, 读取的对象是内存键值数据库中的config_filename_global键
    :return:
    """

    # 初始化内置键值数据库
    kv = kvdb()
    # 获取全局配置文件的绝对路径
    config_filename_global = kv.read("config_filename_global")
    # 获取用户选择的配置模式
    config_mode = kv.read("config_mode")

    # 初始化yaml方法
    pyyaml = YAML(typ='rt')

    # 读取全局配置文件的内容
    try:
        with open(config_filename_global, 'r', encoding='utf-8') as ca_tmp:
            config_content_global = pyyaml.load(ca_tmp)
        # 上传本地配置文件的内容
        kv.set(k="config_content_global", v=config_content_global)
    except Exception as el:
        logging.error(f"获取配置{config_filename_global}时遇到意外的问题")
        logging.exception(el)

    # 根据用户选择的配置模式决定去哪读取配置
    if config_mode == "local":
        # 本地文件模式
        try:
            # 如果是本地, 那么再将本地配置上传至kvdb默认的key名中去
            kv.set(config_content_global)
            logging.info(f"已将本地全局配置文件: {config_filename_global} 上传至内置键值数据库")
        except Exception as el:
            logging.error(f"上传配置{kv.default_config_name}时遇到意外的问题")
            logging.exception(el)
        # 其他配置文件, 逻辑同nacos
        if config_content_global["local"]["config_other_map"]:
            for other_key, other_filename in config_content_global["local"]["config_other_map"].items():
                try:
                    # 注意, 这里指定了将yaml转为json格式, 所以配置文件中必须为yaml
                    # 解析返回的配置文件, 将yaml解析为json
                    with open(other_filename, 'r', encoding='utf-8') as ca_tmp:
                        other_json = pyyaml.load(ca_tmp)
                    logging.info(f'读取到本地的配置文件{other_filename}并上传至内部数据库')
                    # 上传全局配置
                    kvdb().set(k=other_key, v=other_json)
                except Exception as el:
                    logging.error(f"上传配置{other_filename}时遇到意外的问题")
                    logging.exception(el)

    elif config_mode == "nacos":
        # 从配置文件中读取nacos配置
        nacos_config = config_content_global["nacos"]
        # 初始化nacos链接
        cn = cnacos(
            host=nacos_config["host"],
            tenant=nacos_config["tenant"],
            port=nacos_config["port"],
            path=nacos_config["path"],
            user=nacos_config["username"],
            password=nacos_config["password"],
        )
        # 从nacos获取全局配置
        try:
            config_json = cn.getconf(dataid=nacos_config["dataid_global"], to_type='json')
            kvdb().set(config_json)
            # logging.info(f"获取到的全局配置: {config_json}")
            logging.info(f"已将nacos全局配置文件: {nacos_config['tenant']}/{nacos_config['dataid_global']} 上传至内置键值数据库")
        except Exception as el:
            logging.error(f"上传配置{kv.default_config_name}时遇到意外的问题")
            logging.exception(el)

        # 获取定义的其他配置文件
        if nacos_config["dataid_other_map"]:
            for other_key, other_dataid in nacos_config["dataid_other_map"].items():
                try:
                    # 注意, 这里指定了将yaml转为json格式, 所以配置文件中必须为yaml
                    other_json = cn.getconf(dataid=other_dataid, to_type='json')
                    kvdb().set(k=other_key, v=other_json)
                    logging.info(f'读取到nacos的配置文件{nacos_config["tenant"]}/{other_dataid}并上传至内部数据库')
                except Exception as el:
                    logging.error(f"获取配置{other_dataid}时遇到意外的问题")
                    logging.exception(el)

    # 其他特殊处理

    # 将微服务列表转为前端易读的格式
    # 转换成机器易读的格式, 另存一份, 以服务名为key, 环境名为value
    try:
        microservices_all = kv.read('config_microservices', default={})
        microservices_service = {}
        for sys_name_en, sys_info in microservices_all.items():
            for service_name in sys_info["services"]:
                service_info = {
                    "sys_name_en": sys_name_en,
                    "sys_name_cn": sys_info["name_cn"]
                }
                microservices_service[service_name] = service_info
        # 这个key存储微服务配置的易读版
        kvdb().set(microservices_service, k="config_microservices_readable")
    except Exception as el:
        logging.error(f"获取冷日志微服务列表时遇到意外的问题")
        logging.exception(el)


def get_config_once(config_filename_global, config_mode):
    """
    只获取一次主配置文件内容, 不与键值数据库交互
    :param config_filename_global: 主配置文件绝对路径
    :param config_mode: 配置模式"local"|"nacos"
    :return:
    """

    # 初始化yaml方法
    pyyaml = YAML(typ='rt')

    # 读取本地主配置文件的内容
    with open(config_filename_global, 'r', encoding='utf-8') as ca_tmp:
        config_content_global = pyyaml.load(ca_tmp)

    # 根据用户选择的配置模式决定去哪读取配置
    if config_mode == "local":
        # 本地文件模式就直接返回
        return config_content_global

    elif config_mode == "nacos":
        # 如果是nacos模式, 则从配置文件中读取nacos配置
        nacos_config = config_content_global["nacos"]
        # 初始化nacos链接
        cn = cnacos(
            host=nacos_config["host"],
            tenant=nacos_config["tenant"],
            port=nacos_config["port"],
            path=nacos_config["path"],
            user=nacos_config["username"],
            password=nacos_config["password"],
        )
        # 从nacos获取全局配置
        config_json = cn.getconf(dataid=nacos_config["dataid_global"], to_type='json')
        return config_json
    else:
        raise ZeroDivisionError(f"不支持的配置模式: {config_mode}")