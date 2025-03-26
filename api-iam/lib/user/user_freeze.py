from ..data_format import res_format
from ..db.exec_ql import *
import logging


def freeze(data_request):
    """
    冻结本地用户的入口
    :param data_request: 请求数据, 应包含: 用户名user_account, 用户类型user_type
    """

    # 解析传入的信息
    try:
        user_type = data_request["user_type"]
        user_account = data_request["user_account"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 初始化数据库
    mp = MysqlPool()
    # 拼装冻结sql
    sql_update_tem = """
        update sw_user set status = 'off' where user_type = %(user_type)s and user_account = %(user_account)s
    """
    sql_update_data = {"user_account": user_account, "user_type": user_type}
    # 执行删除
    mp.transaction(sql_update_tem, sql_update_data)
    logging.info(f"已冻结{user_type}用户: {user_account}")


def unfreeze(data_request):
    """
    解冻本地用户的入口
    :param data_request: 请求数据, 应包含: 用户名user_account, 用户类型user_type
    """

    # 解析传入的信息
    try:
        user_type = data_request["user_type"]
        user_account = data_request["user_account"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 初始化数据库
    mp = MysqlPool()
    # 拼装冻结sql
    sql_update_tem = """
        update sw_user set status = 'on' where user_type = %(user_type)s and user_account = %(user_account)s
    """
    sql_update_data = {"user_account": user_account, "user_type": user_type}
    # 执行删除
    mp.transaction(sql_update_tem, sql_update_data)
    logging.info(f"已冻结{user_type}用户: {user_account}")