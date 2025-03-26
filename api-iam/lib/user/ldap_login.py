from ..db.ldap_general import ldap_try_bind, decorator_ldap
from ..db.exec_ql import MysqlPool
from . import login_jwt
from .user_data_build import build_payload
import logging


@decorator_ldap
def ldap_user_login(user_account, user_password, ou_name):
    """
    ldap用户登录入口
    :param user_account: ldap用户的账号
    :param user_password: ldap用户的密码
    :param ou_name: ldap用户分组名(搜索方案名)
    :return:
    """

    # 初始化数据库
    mp = MysqlPool()
    # 获取该用户的ldap信息
    # 拼写查询用户的语句
    sql_select_tem = """
        select 
          u.*, lo.*
        from 
          sw_user u 
          left join sw_ldap_ous lo on u.ldap_ou_name = lo.ou_name
        where
          u.account = %(account)s 
          -- 不校验ou_name了, 因为account是唯一的
          -- and u.ldap_ou_name = %(ou_name)s
          and befrom = 'ldap';
    """
    # 不校验ou_name了, 因为account是唯一的
    sql_select_data = {"account": user_account, "ou_name": ou_name}
    # 发起查询
    res_db_select = mp.fetch_one(sql_select_tem, sql_select_data)
    # print(res_db_select)

    # 为空说明账户不存在
    if not res_db_select:
        raise ZeroDivisionError("用户名或密码不对")
        # return res_format(err='我一眼就看出来你不是我的用户')
    # 判断用户是否被冻结
    status = res_db_select["status"]
    if status != 'on':
        raise ZeroDivisionError("勇者被施加了冻结状态, 先别工作了吧")
        # return res_format(err='勇者也需要休息, 先别工作了吧')
    # 获取用户信息
    user_id = res_db_select["user_id"]
    dn = res_db_select["ldap_dn"]
    # role_id = res_db_select["role_id"],
    befrom = res_db_select["befrom"]
    as_account = res_db_select["as_account"]
    as_displayname = res_db_select["as_displayname"]
    as_tel = res_db_select["as_tel"]
    as_email = res_db_select["as_email"]
    as_password = res_db_select["as_password"]

    # 组合属性名字列表
    search_attrs = [as_account, as_displayname, as_tel, as_email, as_password]

    # 测试登录并获取本用户的信息
    dict_ldap_userinfo = ldap_try_bind(user_account, dn, user_password, search_attrs, as_password)
    logging.info(f"获取到的ldap用户实时属性: {dict_ldap_userinfo}")
    displayname_new = dict_ldap_userinfo[as_displayname]
    email_new = dict_ldap_userinfo[as_email]
    tel_new = dict_ldap_userinfo[as_tel]

    # 更新用户最后登录时间和ldap中对应属性的信息
    sql_update_template = """
            update sw_user 
            set 
              displayname = %(displayname_new)s,
              email = %(email_new)s,
              tel = %(tel_new)s,
              date_latest_login = now()
            where 
              account = %(user_account)s
              and ldap_ou_name = %(ou_name)s
              and befrom = 'ldap';
        """

    # 如果有值是列表, 则取第一个值
    def v_format(v_tmp):
        if isinstance(v_tmp, list):
            if v_tmp:
                return v_tmp[0]
            else:
                return ''
        else:
            return v_tmp

    sql_update_data = {
        "displayname_new": v_format(displayname_new),
        "email_new": v_format(email_new),
        "tel_new": v_format(tel_new),
        "user_account": user_account,
        "ou_name": ou_name,
    }


    logging.info(sql_update_template)
    logging.info(sql_update_data)
    mp.transaction(sql_update_template, sql_update_data)

    # 生成用户的简要信息, 用于jwt的payload
    # payload = {
    #     "id": user_id,
    #     "account": user_account,
    #     "displayname": displayname_new,
    #     "role_id": role_id,
    #     "email": email_new,
    #     "tel": tel_new,
    #     "befrom": befrom,
    # }

    payload = build_payload(user_account)
    # 生成token
    jwt_str = login_jwt.create(payload)

    # 获取用户头像
    sql_select_photo_tem = """
            select 
              p.photo_base64
            from 
              sw_user u 
              left join sw_photo p on u.photo_id = p.photo_id
            where
              u.account = %(account)s 
              -- 不校验ou_name了, 因为account是唯一的
              -- and u.ldap_ou_name = %(ou_name)s
              and befrom = 'ldap';
        """
    # 不校验ou_name了, 因为account是唯一的
    sql_select_photo_data = {"account": user_account, "ou_name": ou_name}
    # 发起查询
    res_db_photo = mp.fetch_one(sql_select_photo_tem, sql_select_photo_data)
    user_photo_base64 = res_db_photo["photo_base64"]

    logging.info(f"ldap用户: {user_account} 使用密码登录成功")


    # logging.info(res_db_select)

    return payload, jwt_str, user_photo_base64

