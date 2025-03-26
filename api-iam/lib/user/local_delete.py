from ..data_format import res_format
from ..db.exec_ql import *
import logging


def entry(data_request):
    """
    删除本地用户的入口
    :param data_request: 请求数据, 应包含: 用户名user_account, 用户类型user_type
    """

    # 解析传入的信息
    try:
        # user_type = data_request["user_type"]
        user_account = data_request["user_account"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 初始化数据库
    mp = MysqlPool()
    # 拼装删除sql
    sql_delete_tem = """
        delete from sw_user where user_type = 'local' and user_account = %(user_account)s
    """
    sql_delete_data = {"user_account": user_account}
    # 执行删除
    mp.transaction(sql_delete_tem, sql_delete_data)
    logging.info(f"已删除{user_type}用户: {user_account}")