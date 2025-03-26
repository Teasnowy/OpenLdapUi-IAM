import logging

from .check import rule_account
from ..data_format import res_format
from .passwd import encrypt_string
from . import login_jwt
from . import check
from ..db.db_select import *
from ..db.exec_ql import *
from .ldap_login import ldap_user_login
from .user_data_build import build_payload
import re


def entry(data_request):
    """
    登录入口
    :param data_request: 请求数据, 应包含: 登录类型sign_type, 用户名user_account, 密码user_password,
                        手机号tel, 短信验证码code_tel_input, 用户类型user_type
    """

    # 解析传入的信息
    try:
        sign_type = data_request["sign_type"]
        user_type = data_request["user_type"]
        user_account = data_request["user_account"]
        user_password = data_request["user_password"]
        ou_name = None
        # 如果是ldap用户, 则需要选择分组
        if user_type == 'ldap':
            ou_name = data_request["ou_name"]
        # tel = data_request["tel"]
        # code_tel_input = data_request["code_tel_input"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 初步校验
    if not user_password:
        raise ZeroDivisionError("密码怎么是空的")

    # 判断登录次数是否超过配置
    check.check_auth_num(user_type, user_account)

    # 根据不同的类型判断登录信息
    if sign_type == "passwd" and user_type == 'local':
        check.user_info_local(check_type="login", user_account=user_account, password=user_password)
        # 如果是本地用户密码登录, 此时通过用户名比对数据库中加密后的密码
        payload, res_jwt, user_photo_base64 = login_passwd_local(user_account, user_password)

    elif sign_type == "passwd" and user_type == 'ldap':
        check.user_info_local(check_type="login", user_account=user_account, password=user_password)
        # 如果是ldap用户登录
        logging.info("ldap登录")
        payload, res_jwt, user_photo_base64 = ldap_user_login(user_account, user_password, ou_name)

    else:
        raise ZeroDivisionError("不支持的登录类型")

    # 定义给前端返回的数据
    data_result = {
        "res_jwt": res_jwt,
        "user_info": payload,
        "user_photo_base64": user_photo_base64
    }

    # 清空尝试登录的次数
    check.check_auth_num(user_type, user_account, clean_up=True)
    return data_result


def login_passwd_local(user_account, user_password):
    """
    本地用户账号密码登录
    :param user_account: 账号
    :param user_password: 密码
    :return:
    """

    # 初始化数据库连接池
    ms = MysqlPool()
    # 加密前端此时传来的密码
    # password_encrypt_web = encrypt_string(user_account, user_password)
    # 放弃加密, 直接使用前端做单向加密
    password_encrypt_web = user_password

    # 这里不进行复杂的取数了, 仅校验密码
    # sql_select_template = """
    #     select
    #         u.*,
    #         GROUP_CONCAT(DISTINCT ug.group_id ORDER BY ug.group_id SEPARATOR ',') AS groups,
    #         GROUP_CONCAT(DISTINCT ru.role_id ORDER BY ru.role_id SEPARATOR ',') AS roles
    #     from
    #         sw_user u
    #         left join sw_roleuser ru on u.account = ru.account
    #         left join sw_usergroup ug on u.account = ug.account
    #     where
    #         u.account = %(user_account)s
    #         and u.password = %(password_encrypt_web)s
    #         and u.befrom = 'local'
    #     GROUP BY u.account;
    # """
    sql_select_template = """
        select * from sw_user u 
        where 
            u.account = %(user_account)s 
            and u.password = %(password_encrypt_web)s
            and u.befrom = 'local'
            ;
    """
    sql_select_data = {"user_account": user_account, "password_encrypt_web": password_encrypt_web}
    # logging.info(sql_select_data)
    res_user_info = ms.fetch_one(sql_select_template, sql_select_data)
    # 如果查到的结果不为空, 则说明密码正确
    if res_user_info:
        # res_user_info = ms.fetch_all(sql_select_template, sql_select_data)[0]

        # 判断用户是否被冻结
        status =  res_user_info["status"]
        if status != 'on':
            raise ZeroDivisionError("勇者被施加了冻结状态, 先别工作了吧")
        #
        # # logging.info(res_user_info)
        # # 生成用户的简要信息, 用于jwt的payload
        # payload = {
        #     "id": res_user_info["user_id"],
        #     "account": res_user_info["account"],
        #     "displayname": res_user_info["displayname"],
        #     "rank": res_user_info["rank"],
        #     "role_id": re.split(',', res_user_info["roles"] or "") if res_user_info["roles"] else [],
        #     "groups": re.split(',', res_user_info["groups"] or "") if res_user_info["groups"] else [],
        #     "email": res_user_info["email"],
        #     "tel": res_user_info["tel"],
        #     "befrom": res_user_info["befrom"],
        # }

        payload = build_payload(user_account)

        # 生成token
        jwt_str = login_jwt.create(payload)
        logging.info(f"本地用户: {user_account} 使用密码登录成功")

        # 获取头像
        sql_select_photo_tem = "select photo_base64 from sw_photo where photo_id = %(photo_id)s"
        sql_select_photo_data = {"photo_id": res_user_info["photo_id"]}
        user_photo_base64 = ""
        user_photo_db = ms.fetch_one(sql_select_photo_tem, sql_select_photo_data)
        if user_photo_db:
            user_photo_base64 = user_photo_db["photo_base64"]

        # 更新用户最后登录时间
        sql_update_template = """
            update sw_user set date_latest_login = now() where account = %(user_account)s and befrom = 'local';
        """
        sql_update_data = {"user_account": user_account}
        ms.transaction(sql_update_template, sql_update_data)
        return payload, jwt_str, user_photo_base64

    else:
        raise ZeroDivisionError("用户名或密码不对")


def login_code():
    pass


def get_init(data_request):
    """
    获取登录注册相关的配置
    :param data_request: 随意, 字典类型就可以
    :return:
    """
    # 解析传入的信息
    try:
        pass
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 初始化键值数据库
    dc = kvdb()
    cf = dc.read()
    # 获取登录验证相关配置
    cf_auth = cf['auth']
    # 注册是否强制验证手机号
    if cf_auth['must_tel'] == 'yes':
        must_tel = True
    else:
        must_tel = False
    # 注册是否强制验证邮箱
    if cf_auth['must_email'] == 'yes':
        must_email = True
    else:
        must_email = False
    # 是否允许ldap用户自主修改密码
    if cf_auth['forget_passwd_ldap'] == 'yes':
        forget_passwd_ldap = True
    else:
        forget_passwd_ldap = False
    # 获取登录页壁纸接口
    if "image_auth" in cf_auth:
        image_auth = cf_auth["image_auth"]
    else:
        image_auth = ""

    list_ou_name = []
    # 如果开启ldap才获取数据
    ldap_status = False
    # ldap用户能否修改自己的资料
    ldap_modify_oneself = False
    cf_ldap = cf['ldap']
    if cf_ldap['status'] == 'on':
        if cf_ldap['modify_oneself'] == 'yes':
            ldap_modify_oneself = True
        ldap_status = True
        # 初始化数据库
        mp = MysqlPool()
        # 定义获取ldap组的sql
        sql_select_ous = """
            select ou_name from sw_ldap_ous;
        """
        list_res_db_ous = mp.fetch_all(sql_select_ous)
        # 提取所有组名
        for ous in list_res_db_ous:
            list_ou_name.append(ous['ou_name'])

    # 定义返回信息
    data_result = {
        "must_tel": must_tel,
        "must_email": must_email,
        "list_ous": list_ou_name,
        "ldap_status": ldap_status,
        "forget_passwd_ldap": forget_passwd_ldap,
        "ldap_modify_oneself": ldap_modify_oneself,
        "image_auth": image_auth,
    }

    return data_result


def logout(data_req):
    """
    用户注销
    :param data_req: 需要传入用户名account
    :return:
    """

    # 解析传入的信息
    try:
        account = data_req["account"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 校验入参格式
    rule_account(account)
    # 判断校验注销的人是否是自己
    try:
        payload = login_jwt.get_info()
        account_jwt = payload["account"]
        if account_jwt != account:
            return res_format(err=f"你不是{account}", code=10002)
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err=f"你不是{account}", code=10002)

    kv = kvdb()

    # 清除redis中的key
    key_jwt = f"jwt_{account}"
    kv.delete(key_jwt)

