import hashlib
import logging
import re
import time
from ..db.ldap_general import ldap_update_dn_replace, ldap_try_bind
from ..data_format import str_to_md5
from . import check
from ..db.db_select import kvdb
from ..db.exec_ql import MysqlPool


def entry(data_request):
    """
    用来更新用户信息的函数
    :param data_request: 前端传来的json, 应包含user_account, user_displayname, password, tel, email, code_input, user_from
    """

    try:
        user_from = data_request['user_type']
    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    if user_from == 'local':
        update_user_local(data_request)
    elif user_from == 'ldap':
        # raise ZeroDivisionError('暂不支持ldap')
        update_user_ldap(data_request)
    else:
        raise ZeroDivisionError(f'不支持的用户类型: {user_from}')

    data_result = {
        "ok": 'ok'
    }

    return data_result


def update_user_ldap(data_request):
    """
    ldap用户更新个人信息 (直接更改ldap服务器)
    :param data_request: 应包含 user_account, user_displayname, password, tel, email, code_tel_input, code_email_input, user_type
    :return:
    """

    # 解析传入的信息
    try:
        user_account = data_request["user_account"]
        user_displayname = data_request["user_displayname"]
        # 用户填入的手机号
        tel = data_request["tel"]
        email = data_request["email"]
        # 如果填了手机, 则获取前台填入的短信验证码
        if tel:
            code_tel_input = data_request["code_tel_input"]
        else:
            code_tel_input = ""
        # 如果填了邮箱, 则获取前台填入的邮箱验证码
        if email:
            code_email_input = data_request["code_email_input"]
        else:
            code_email_input = ''
        # 账号所属, 目前分为本地local和ldap
        user_type = data_request["user_type"]
        # user_name, user_displayname, password, mobile, mail
    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    if user_type != 'ldap':
        raise ZeroDivisionError('本函数只支持ldap用户修改')

    # 初始化键值数据库
    kv = kvdb()
    # 查看是否开启了ldap用户更新个人信息
    cf_ldap = kv.read()["ldap"]
    if cf_ldap["modify_oneself"] != 'yes':
        raise ZeroDivisionError('不允许ldap用户自行修改')

    # 判断传入参数是否合规----------------
    check.user_info_local(**data_request, check_type='update')

    # 初始化数据库
    mp = MysqlPool()

    # 获取该用户对应的ldap组的信息, 用于获取个人信息在ldap服务器上的属性名
    sql_select_tem = """
            select 
              u.*, lo.*
            from 
              sw_user u 
                left join sw_ldap_ous lo on u.ldap_ou_name = lo.ou_name
            where
              u.account = %(account)s 
              and befrom = 'ldap';
        """
    # 不校验ou_name了, 因为account是唯一的
    sql_select_data = {"account": user_account}
    # 发起查询
    res_db_select = mp.fetch_one(sql_select_tem, sql_select_data)

    # 为空说明账户不存在
    if not res_db_select:
        raise ZeroDivisionError("用户名或密码不对")
        # return res_format(err='我一眼就看出来你不是我的用户')
    # 判断用户是否被冻结
    status = res_db_select["status"]
    if status != 'on':
        raise ZeroDivisionError("勇者被施加了冻结状态, 先别工作了吧")
        # return res_format(err='勇者也需要休息, 先别工作了吧')

    # 查看用户信息是不是没变
    payload_old = {
        "displayname": res_db_select["displayname"],
        "email": res_db_select["email"],
        "tel": res_db_select["tel"],
    }
    payload_new = {
        "displayname": user_displayname,
        "email": email,
        "tel": tel,
    }
    if payload_old == payload_new:
        raise ZeroDivisionError("检测到数据未变更, 拒绝服务")

    # 获取用户信息
    dn = res_db_select["ldap_dn"]
    as_displayname = res_db_select["as_displayname"]
    as_tel = res_db_select["as_tel"]
    as_email = res_db_select["as_email"]

    # 组合数据
    data_mod = {
        as_displayname: [user_displayname],
        as_tel: [tel],
        as_email: [email]
    }

    try:
        # 获取配置, 看一下是不是需要验证码
        kv = kvdb()
        cf_auth = kv.read()["auth"]
        must_email = cf_auth["must_email"]
        must_tel = cf_auth["must_tel"]

        # 如果原手机号与现在传入的手机号不同, 则校验验证码
        if tel != res_db_select["tel"] and must_tel == 'yes':
            check.check_code_sms(tel, code_tel_input)
        # 如果原邮箱与现在传入的邮箱不同, 则校验验证码
        if email != res_db_select["email"] and must_email == 'yes':
            check.check_code_email(email, code_email_input)

        # 更新ldap服务器里的信息
        ldap_update_dn_replace(dn, data_mod)
        # 更新用户表里的信息
        # 组合要更新的信息
        sql_update_template = """
            update sw_user set
                displayname = %(displayname)s,
                tel = %(tel)s, 
                email = %(email)s
            where 
                account = %(account)s
                and befrom = 'ldap';
        """
        sql_update_data = {
            "account": user_account,
            "displayname": user_displayname,
            "tel": tel,
            "email": email,
        }
        mp.transaction(sql_update_template, sql_update_data)

    except Exception as el:
        logging.exception(el)
        logging.error(f"用户{user_account}更新个人信息失败")
        raise ZeroDivisionError(f"更新个人信息失败")


def update_user_local(data_request):
    """
    本地用户更新个人信息
    :param data_request: 应包含 user_account, user_displayname, password, tel, email, code_tel_input, code_email_input, user_type
    :return:
    """

    # 解析传入的信息
    try:
        user_account = data_request["user_account"]
        user_displayname = data_request["user_displayname"]
        # 密码改为由单独的接口修改
        # user_password = data_request["password"]
        # 用户填入的手机号
        tel = data_request["tel"]
        email = data_request["email"]
        # 如果填了手机, 则获取前台填入的短信验证码
        if tel:
            code_tel_input = data_request["code_tel_input"]
        else:
            code_tel_input = ""
        # 如果填了邮箱, 则获取前台填入的邮箱验证码
        if email:
            code_email_input = data_request["code_email_input"]
        else:
            code_email_input = ''
        # 账号所属, 目前分为本地local和ldap
        user_type = data_request["user_type"]
        # user_name, user_displayname, password, mobile, mail
    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    if user_type != 'local':
        raise ZeroDivisionError('只支持本地用户修改')

    # 判断传入参数是否合规----------------
    check.user_info_local(**data_request, check_type='update')

    # 初始化数据库连接池
    ms = MysqlPool()

    # 检查数据库中是否有此用户
    sql_select_template = "select * from sw_user where account = %(user_account)s and befrom = 'local';"
    sql_select_data = {"user_account": user_account}
    res_user_info_list = ms.fetch_all(sql_select_template, sql_select_data)
    # 如果查到的结果不为空, 则说明用户存在
    if res_user_info_list:
        # 获取原用户信息
        res_user_info = ms.fetch_all(sql_select_template, sql_select_data)[0]
        payload = {
            "account": res_user_info["account"],
            "displayname": res_user_info["displayname"],
            "email": res_user_info["email"],
            "tel": res_user_info["tel"],
        }

        # 组合要更新的信息
        sql_update_template = """
                    update sw_user set
                        displayname = %(displayname)s,
                        tel = %(tel)s, 
                        email = %(email)s
                    where 
                        account = %(account)s
                        and befrom = 'local';
                """
        sql_update_data = {
            "account": user_account,
            "displayname": user_displayname,
            "tel": tel,
            "email": email,
        }

        # 如果完全一致, 说明不需要更改
        if sql_update_data == payload:
            raise ZeroDivisionError('检测到数据未变更, 拒绝服务')

        # 获取配置, 看一下是不是需要验证码
        kv = kvdb()
        cf_auth = kv.read()["auth"]
        must_email = cf_auth["must_email"]
        must_tel = cf_auth["must_tel"]

        # 如果原手机号与现在传入的手机号不同, 则校验验证码
        if tel != res_user_info["tel"] and must_tel == 'yes':
            check.check_code_sms(tel, code_tel_input)
        # 如果原邮箱与现在传入的邮箱不同, 则校验验证码
        if email != res_user_info["email"] and must_email == 'yes':
            check.check_code_email(email, code_email_input)

        ms.transaction(sql_update_template, sql_update_data)
        logging.info(f"本地用户{user_account}的个人信息更新成功, 原: {payload}, 现: {sql_update_data}")
        # 即刻续签一次jwt, 更新用户信息

    else:
        raise ZeroDivisionError("数据库中没有此用户")


def update_password_useold(data_request):
    """
    通过旧密码更新用户密码
    :param data_request: 应包含 user_account, password_old, password_new
    :return:
    """

    # 解析传入的信息
    try:
        user_type = data_request["user_type"]
        user_account = data_request["user_account"]
        user_password_old = data_request["user_password_old"]
        user_password_new = data_request["user_password_new"]

    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    if user_type == 'local':
        update_password_local_useold(data_request)
    elif user_type == 'ldap':
        update_password_ldap_useold(data_request)
    else:
        raise ZeroDivisionError(f"不支持的用户类型{user_type}")




def update_password_ldap_useold(data_request):
    """
    通过旧密码更新ldap用户密码
    :param data_request: 应包含 user_account, password_old, password_new
    :return:
    """

    # 解析传入的信息
    try:
        user_account = data_request["user_account"]
        user_password_old = data_request["user_password_old"]
        user_password_new = data_request["user_password_new"]

    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

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
          and befrom = 'ldap';
    """
    # 不校验ou_name了, 因为account是唯一的
    sql_select_data = {"account": user_account}
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
    dn = res_db_select["ldap_dn"]
    as_password = res_db_select["as_password"]

    # 初始化键值数据库
    kv = kvdb()
    # 查看是否开启了ldap用户更新个人信息
    cf_ldap = kv.read()["ldap"]
    if cf_ldap["modify_oneself"] != 'yes':
        raise ZeroDivisionError('不允许ldap用户自行修改')

    # 测试登录, 不获取用户信息
    ldap_try_bind(user_account, dn, user_password_old, get_info=False)
    # 修改ldap服务端的密码
    data_mod = {
        as_password: [user_password_new]
    }
    # logging.info()
    ldap_update_dn_replace(dn, data_mod)
    logging.info(f"ldap用户{user_account}密码修改成功")
    return {"ok": "ok"}


def update_password_local_useold(data_request):
    """
    通过旧密码更新本地用户密码
    :param data_request: 应包含 user_account, password_old, password_new
    :return:
    """

    # 解析传入的信息
    try:
        user_account = data_request["user_account"]
        user_password_old = data_request["user_password_old"]
        user_password_new = data_request["user_password_new"]

    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 初始化数据库连接池
    ms = MysqlPool()

    # 按账号和旧密码查找, 有数据说明原密码正确
    sql_select_template = """
        select * from sw_user 
        where 
            account = %(user_account)s 
            and password = %(user_password_old)s
            and befrom = 'local';
    """
    sql_select_data = {"user_account": user_account, "user_password_old": user_password_old}
    res_user_info_list = ms.fetch_all(sql_select_template, sql_select_data)
    # 如果查到的结果不为空, 则说明用户存在
    if res_user_info_list:
        # 组合要更新的信息
        sql_update_template = """
            update sw_user set
                password = %(user_password_new)s
            where 
                account = %(user_account)s
                and befrom = 'local';
        """
        sql_update_data = {
            "user_account": user_account,
            "user_password_new": user_password_new,
        }
        ms.transaction(sql_update_template, sql_update_data)
    else:
        raise ZeroDivisionError("原密码错误")

    logging.info(f"本地用户{user_account}密码修改成功")
    return {"ok": "ok"}


def update_password_local_sms(data_request):
    """
    通过对应账号的短信验证码更新本地用户密码
    :param data_request: 应包含 user_account, user_password_new, code_tel_input
    :return:
    """

    # 解析传入的信息
    try:
        user_account = data_request["user_account"]
        code_tel_input = data_request["code_tel_input"]
        user_password_new = data_request["user_password_new"]
    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 验证密码格式
    check.rule_password(user_password_new)
    # 验证用户是否存在
    res_user_info = check.check_user_exist_local(user_account)
    # 如果查到的结果不为空, 则说明用户存在
    if res_user_info:
        # 获取手机号
        tel = res_user_info["tel"]
        # 检查验证码
        check.check_code_sms(tel, code_tel_input)
        # 初始化数据库连接池
        # mp = MysqlPool()
        # # 组合要更新的信息
        # sql_update_template = """
        #     update sw_user set
        #         password = %(user_password_new)s
        #     where
        #         account = %(user_account)s
        #         and befrom = 'local';
        # """
        # sql_update_data = {
        #     "user_account": user_account,
        #     "user_password_new": user_password_new,
        # }
        # mp.transaction(sql_update_template, sql_update_data)
        passwd_change_select(res_user_info, user_password_new)
    else:
        raise ZeroDivisionError("账号与手机号不匹配")

    logging.info(f"用户{user_account}修改密码成功")
    return {"ok": "ok"}


def update_password_local_email(data_request):
    """
    通过对应账号的邮箱验证码更新本地用户密码
    :param data_request: 应包含 user_account, user_password_new, code_tel_input
    :return:
    """

    # 解析传入的信息
    try:
        user_account = data_request["user_account"]
        code_email_input = data_request["code_email_input"]
        user_password_new = data_request["user_password_new"]
    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")
    # 验证密码格式
    check.rule_password(user_password_new)
    # 验证用户是否存在
    res_user_info = check.check_user_exist_local(user_account)
    # 如果查到的结果不为空, 则说明用户存在
    if res_user_info:
        # 获取手机号
        email = res_user_info["email"]
        # 检查验证码
        check.check_code_email(email, code_email_input)
        # 初始化数据库连接池
        mp = MysqlPool()
        # 组合要更新的信息
        # sql_update_template = """
        #     update sw_user set
        #         password = %(user_password_new)s
        #     where
        #         account = %(user_account)s
        #         and befrom = 'local';
        # """
        # sql_update_data = {
        #     "user_account": user_account,
        #     "user_password_new": user_password_new,
        # }
        # mp.transaction(sql_update_template, sql_update_data)
        passwd_change_select(res_user_info, user_password_new)
    else:
        raise ZeroDivisionError("账号与手机号不匹配")

    logging.info(f"{user_account}修改密码成功")
    return {"ok": "ok"}


def passwd_change_select(user_info, user_password_new):
    """
    根据用户类型的不同选择不同的改密码分支
    """
    account = user_info["account"]
    befrom = user_info["befrom"]
    if befrom == 'local':
        passwd_change_local(account, user_password_new)
    elif befrom == 'ldap':
        # 获取配置以验证本系统是否开放了修改ldap用户的密码的功能
        kv = kvdb()
        cf_auth = kv.read()['auth']
        if 'forget_passwd_ldap' in cf_auth and cf_auth["forget_passwd_ldap"] == 'yes':
            passwd_change_ldap(user_info, user_password_new)
        else:
            raise ZeroDivisionError(f'暂不支持LDAP用户修改密码')
    else:
        raise ZeroDivisionError(f'不支持的用户类型: {befrom}')


def passwd_change_local(account, user_password_new):
    """
    修改本地用户的密码
    """
    mp = MysqlPool()
    # 组合要更新的信息
    sql_update_template = """
                update sw_user set
                    password = %(user_password_new)s
                where 
                    account = %(user_account)s
                    and befrom = 'local';
            """
    sql_update_data = {
        "user_account": account,
        "user_password_new": user_password_new,
    }
    mp.transaction(sql_update_template, sql_update_data)


def passwd_change_ldap(user_info, user_password_new):
    """
    修改ldap用户的密码
    """

    dn = user_info["ldap_dn"]
    account = user_info["account"]
    ldap_ou_name = user_info["ldap_ou_name"]

    # 查询ldap模板确定密码的对应字段
    sql_select_tem = "select as_password from sw_ldap_ous where ou_name = %(ldap_ou_name)s"
    sql_select_data = {"ldap_ou_name": ldap_ou_name}
    mp = MysqlPool()
    db_res = mp.fetch_one(sql_select_tem, sql_select_data)


    if db_res:
        ldap_as_password = db_res["as_password"]

        data_mod = {
            ldap_as_password: [user_password_new]
        }

        ldap_update_dn_replace(dn, data_mod)
    else:
        raise ZeroDivisionError(f"用户{account}对应的LDAP组{ldap_ou_name}不存在")



def update_photo(data_request):
    """
    用户更新头像
    :param data_request: 里面包含用户头像的图片base64的user_photo_base64以及user_account和user_type
    :return:
    """
    # 解析传入的信息
    try:
        user_account = data_request["user_account"]
        befrom = data_request["user_type"]
        user_photo_base64 = data_request["user_photo_base64"]
    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")
    # logging.info(user_photo_base64[0:100])
    # 预订正常返回
    data_result = {"ok": "ok"}

    # 检查图片
    check.rule_photo(user_photo_base64)
    # 先看用户在不在
    check.check_user_exist_local(user_account, befrom)

    # 计算图片base64的md5
    md5_hash = str_to_md5(user_photo_base64)
    # 向数据库插入图片 (为保证事务顺序, 放弃额外的函数)
    # photo_to_db(user_photo_base64, md5_hash)

    # 初始化数据库
    mp = MysqlPool()
    list_sql = []

    # 编写更新语句
    sql_update_tem = """
        update sw_user 
        set 
            photo_id = %(md5_hash)s
        where 
            account = %(user_account)s 
            and befrom = %(befrom)s;
    """
    list_sql.append(sql_update_tem)

    # 编写插入图片的语句
    sql_insert_tem = """
        replace into sw_photo (photo_id, photo_base64) values (%(md5_hash)s, %(photo_64)s)
    """
    list_sql.append(sql_insert_tem)

    # 编写清理旧图片的语句
    sql_delete_tem = """
        DELETE FROM sw_photo
        WHERE photo_id NOT IN (
            SELECT photo_id 
            FROM sw_user
            WHERE photo_id IS NOT NULL
        );
    """
    list_sql.append(sql_delete_tem)

    sql_update_data = {
        "md5_hash": md5_hash,
        "user_account": user_account,
        "befrom": befrom,
        "photo_64": user_photo_base64,
    }


    mp.transaction(list_sql, sql_update_data, is_list=True)

    return data_result


def photo_to_db(photo_64, photo_md5):
    """
    将图片的base64上传至数据库 (已弃用此函数, 因为其不能保证事务顺序)
    :param photo_64: 图片的base64字符串
    :param photo_md5: 图片的base64字符串的md5值
    :return:
    """

    # 初始化数据库
    mp = MysqlPool()

    # 编写查询语句, 防止重复上传失败
    sql_select_tem = """
            select * from sw_photo where photo_id = %(photo_md5)s
        """
    sql_select_data = {
        "photo_md5": photo_md5,
    }
    res_db_select = mp.fetch_one(sql_select_tem, sql_select_data)
    # logging.info(res_db_select)
    if res_db_select:
        logging.info(f"图片: {photo_md5}重复, 不执行上传")
    else:
        # 编写上传语句
        sql_insert_tem = """
            insert into sw_photo (photo_id, photo_base64) values (%(photo_md5)s, %(photo_64)s)
        """
        sql_insert_data = {
            "photo_64": photo_64,
            "photo_md5": photo_md5,
        }
        # 执行
        mp.transaction(sql_insert_tem, sql_insert_data)
        logging.info(f"图片: {photo_md5}已上传")
    time.sleep(10)
    # 编写清理无用头像的语句
    sql_delete_tem = """
        DELETE FROM sw_photo
        WHERE photo_id NOT IN (
            SELECT photo_id 
            FROM sw_user
            WHERE photo_id IS NOT NULL
        );
    """
    mp.transaction(sql_delete_tem)
    logging.info("已清理未被使用的头像")
