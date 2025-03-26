import re
from ..data_format import res_format
from ..db.db_select import *
from ..db.exec_ql import *
from ..user import check, login_jwt, user_data_build
import logging
from collections import defaultdict
from flask import jsonify, request


def get_user_all(data_req):
    """
    获取数据库中目前的所有用户数据 (不包含头像)
    :param data_req: 任意数据
    :return:
    """
    # 初始化数据库连接池
    mp = MysqlPool()
    kv = kvdb()
    # 加密前端此时传来的密码
    # password_encrypt_web = encrypt_string(user_account, user_password)
    # 放弃加密, 直接使用前端做单向加密

    sql_select_template = """
        select 
            u.*,
            GROUP_CONCAT(DISTINCT ug.group_id ORDER BY ug.group_id SEPARATOR ',') AS groups,
            GROUP_CONCAT(DISTINCT ru.role_id ORDER BY ru.role_id SEPARATOR ',') AS roles
        from 
            sw_user u
            left join sw_roleuser ru on u.account = ru.account
            left join sw_usergroup ug on u.account = ug.account
        GROUP BY u.account
    """

    # logging.info(sql_select_data)
    res_user_info = mp.fetch_all(sql_select_template,)

    # 返回字典, 而不是列表
    data_res = {}
    for user_info in res_user_info:
        account = user_info["account"]
        # 不返回管理员
        if account == 'admin':
            continue
        # 查看是否在线
        k_jwt = f"jwt_{account}"
        is_online = False
        if kv.read(k_jwt):
            is_online = True
        user_info["is_online"] = is_online

        # 对特殊数据进行处理
        # 将role_id转为列表
        user_info["roles"] = re.split(',', user_info["roles"] or "") if user_info["roles"] else []
        # 转化组列表
        user_info["groups"] = re.split(',', user_info["groups"] or "") if user_info["groups"] else []

        # data_res[user_info["user_id"]] = user_info
        # 改用account做key
        data_res[user_info["account"]] = user_info

    return data_res


def get_myinfo(data_req):
    """
    获取本人的信息
    :param data_req: 只要不为空就行
    :return:
    """

    data_res = {}

    # 尝试解析jwt
    try:
        # 提取header中的jwt
        jwt_header = request.headers.get('Authorization')
        # 提取真正的令牌部分
        jwt_request = jwt_header.split(" ")[1]
        # 提取header中的用户名
        user_account = request.headers.get('X-Username')

        # 验证并解析
        is_exp, is_renew, jwt_renew, payload = login_jwt.check(jwt_request, user_account)

        # logging.info(type(payload))
        # 仅解析jwt的用户信息部分, 而不验证其他信息
        # payload = jwt.decode(jwt_str, algorithm='HS256', options={"verify_signature": False})
        account = payload["account"]
        befrom = payload["befrom"]
    except:
        # logging.exception(el)
        return data_res

    if account and befrom:
    #     mp = MysqlPool()
    #     sql_select_tem = """
    #         select
    #                 u.*,
    #                 GROUP_CONCAT(DISTINCT ug.group_id ORDER BY ug.group_id SEPARATOR ',') AS groups,
    #                 GROUP_CONCAT(DISTINCT ru.role_id ORDER BY ru.role_id SEPARATOR ',') AS roles,
    #                 p.photo_base64
    #         from
    #                 sw_user u
    #                 left join sw_roleuser ru on u.account = ru.account
    #                 left join sw_usergroup ug on u.account = ug.account
    #                 left join sw_photo p on u.photo_id = p.photo_id
    #         where
    #                 u.account = %(account)s
    #                 and u.befrom = %(befrom)s
    #         GROUP BY u.account
    #     """
    #     sql_select_data = {
    #         "befrom": befrom,
    #         "account": account
    #     }
    #     db_res = mp.fetch_one(sql_select_tem, sql_select_data)
    #     # 提取有效信息
    #     data_res["account"] = db_res["account"]
    #     data_res["displayname"] = db_res["displayname"]
    #     data_res["rank"] = db_res["rank"]
    #     data_res["email"] = db_res["email"]
    #     data_res["tel"] = db_res["tel"]
    #     data_res["befrom"] = db_res["befrom"]
    #     data_res["date_create"] = db_res["date_create"]
    #     data_res["groups"] = re.split(',', db_res["groups"] or "") if db_res["groups"] else []
    #     data_res["roles"] = re.split(',', db_res["roles"] or "") if db_res["roles"] else []
    #     data_res["photo_base64"] = db_res["photo_base64"]

        # 查询所有前后端权限信息
        # data_permissions = user_data_build.get_permissions_all(payload)
        # payload["webs"] = data_permissions["webs"]
        # payload["apis"] = data_permissions["apis"]
        # payload["containers"] = data_permissions["containers"]
        # 仅获取前端权限
        # data_menus = user_data_build.get_permissions_meuns(payload)
        # payload["menus"] = data_menus
        # 获取头像
        photo_base64 = user_data_build.get_photo_base64(account)
        payload["photo_base64"] = photo_base64

    return payload


def get_my_menus(data_req):
    """
    仅获取自己有权限的前端菜单块
    :return:
    """
    data_res = {}

    # 尝试解析jwt
    try:
        # 提取header中的jwt
        jwt_header = request.headers.get('Authorization')
        # 提取真正的令牌部分
        jwt_request = jwt_header.split(" ")[1]
        # 提取header中的用户名
        user_account = request.headers.get('X-Username')

        # 验证并解析
        is_exp, is_renew, jwt_renew, payload = login_jwt.check(jwt_request, user_account)

        # logging.info(type(payload))
        # 仅解析jwt的用户信息部分, 而不验证其他信息
        # payload = jwt.decode(jwt_str, algorithm='HS256', options={"verify_signature": False})
        account = payload["account"]
        befrom = payload["befrom"]
    except:
        # logging.exception(el)
        # return res_format(err="jwt校验失败", code=40001)
        return data_res

    data_menus = user_data_build.get_permissions_meuns(payload)

    return data_menus



def get_role_id_all(data_req):
    """
    获取数据库中目前的role的id
    :param data_req: 任意数据
    :return:
    """
    # 初始化数据库连接池
    mp = MysqlPool()
    # 加密前端此时传来的密码
    # password_encrypt_web = encrypt_string(user_account, user_password)
    # 放弃加密, 直接使用前端做单向加密

    # 对比数据库中的加密字符串
    sql_select_template = """
        select role_id from sw_role;
    """
    # logging.info(sql_select_data)
    res_role_info = mp.fetch_all(sql_select_template,)

    # 返回列表
    data_res = {}
    for role_info in res_role_info:
        data_res[role_info["role_id"]] = role_info

    return res_role_info


def create_batch(data_req):
    """
    批量新增本地用户
    :param data_req: 包含user_list, 是个列表, 里面是用户信息
    :return:
    """

    try:
        user_list = data_req['user_list']
        for u in user_list:
            if sorted(u.keys()) != sorted(["account", "displayname", "password", "tel", "email", "roles", "groups", "status"]):
                # raise ZeroDivisionError(f"某待注册用户的传参和预期不符: {u}")
                return res_format(err=f"某待注册用户的传参和预期不符: {u}")
    except Exception as el:
        logging.error(f"报文格式错误: {data_req}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 获取账号列表
    user_account_list = [i["account"] for i in user_list]
    if not user_account_list:
        return res_format(err="用户列表为空")

    # 校验用户各字段的格式, 此时允许手机号或邮箱都为空, 也不需要验证码
    for u in user_list:
        check.rule_password(u["password"])
        check.rule_tel(u["tel"], not_null=False, need_code=False)
        check.rule_account(u["account"])
        check.rule_email(u["email"], not_null=False, need_code=False)
        check.rule_displayname(u["displayname"])
    # 检查提交的列表中账号是否有重复的
    check.check_account_repeat(user_account_list)
    # 检查这些用户中数据库中是否存在
    check.check_users_notexist_local(user_account_list)


    # 初始化数据库连接池
    mp = MysqlPool()

    # 传入的角色的列表
    list_role_input = []
    # 传入的组的列表
    list_group_input = []
    # 执行insert的sql的模板列表
    list_sql = []
    # 执行insert的sql的数据列表
    data_sql = {}
    n = 1
    nr = 1
    ng = 1
    # 用户表的值
    list_sql_user_value = []
    # 用户权限中间表的值
    list_sql_role_value = []
    # 用户组中间表的值
    list_sql_group_value = []

    for u in user_list:
        list_sql_user_value.append(
            f"(null,'local',now(),now(),now(),%(account_{n})s,%(displayname_{n})s,%(email_{n})s,"
            f"%(tel_{n})s,%(status_{n})s,%(password_{n})s)"
        )
        # 装填用户一般数据
        data_sql[f"account_{n}"] = u['account']
        data_sql[f"displayname_{n}"] = u['displayname']
        data_sql[f"email_{n}"] = u['email']
        data_sql[f"tel_{n}"] = u['tel']
        data_sql[f"status_{n}"] = u['status']
        data_sql[f"password_{n}"] = u['password']
        # 装填权限数据, 这里注意字段名与user表重复, 要加点字符
        for r in u["roles"]:
            list_sql_role_value.append(f"(%(account_{n})s,%(role_id_{nr})s)")
            data_sql[f"role_id_{nr}"] = r
            list_role_input.append(r)
            nr += 1
        # 装填组数据
        for g in u["groups"]:
            list_sql_group_value.append(f"(%(account_{n})s,%(group_id_{ng})s)")
            data_sql[f"group_id_{ng}"] = g
            list_group_input.append(g)
            ng += 1
        n += 1
    # 组合sql语句
    # 用户表sql模板
    list_sql_user_tem = f"""
        insert into sw_user
            (user_id,befrom,date_create,date_update,date_latest_login,account,displayname,email,tel,status,password)
        values {','.join(list_sql_user_value)};
    """
    list_sql.append(list_sql_user_tem)

    data_sql["user_account_list"] = user_account_list

    # 删除可能已有的遗留权限关系
    sql_delete_roles = "delete from sw_roleuser where account in %(user_account_list)s;"
    list_sql.append(sql_delete_roles)
    # 用户权限中间表的模板
    if list_sql_role_value:
        list_sql_role_tem = f"""
            insert into sw_roleuser
                (account,role_id)
            values {','.join(list_sql_role_value)};
        """
        list_sql.append(list_sql_role_tem)

    # 删除可能已有的遗留组关系
    sql_delete_groups = "delete from sw_usergroup where account in %(user_account_list)s;"
    list_sql.append(sql_delete_groups)
    # 用户组中间表的模板
    if list_sql_group_value:
        list_sql_group_tem = f"""
            insert into sw_usergroup
                (account,group_id)
            values {','.join(list_sql_group_value)};
        """
        list_sql.append(list_sql_group_tem)

    # 获取所有组名
    sql_select_group = "select group_id from sw_group"
    res_db_group = mp.fetch_all(sql_select_group,)
    list_group_db = [i["group_id"] for i in res_db_group]
    # 如果有, 说明不存在, 报错
    for g in list_group_input:
        if g not in list_group_db:
            return res_format(err=f"组{g}不存在", code=10002)

    # 获取所有规则名
    sql_select_group = "select role_id from sw_role"
    res_db_roles = mp.fetch_all(sql_select_group)
    list_role_db = [i["role_id"] for i in res_db_roles]
    for r in list_role_input:
        if r not in list_role_db:
            return res_format(err=f"没有{r}这个角色名", code=10002)

    # for i in list_sql:
    #     print(i)
    # print(data_sql)

    mp.transaction(list_sql, data_sql, is_list=True)

    logging.info(f"用户{user_account_list}创建成功")

    return {"ok": "ok"}


def update_batch(data_req):
    """
    批量修改用户, 不涉及密码
    :param data_req: 传入的参数, 应包含user_list
    :return:
    """

    try:
        user_list = data_req['user_list']
        for u in user_list:
            if sorted(u.keys()) != sorted(["account", "displayname", "tel", "email", "roles", "groups", "status", "befrom"]):
                # logging.error(f"用户传参: {u}")
                raise ZeroDivisionError(f"某待更新用户的传参和预期不符: {u}")
    except Exception as el:
        logging.error(f"报文格式错误: {data_req}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 获取账号列表
    user_account_list = [i["account"] for i in user_list]

    # 校验用户各字段的格式, 此时允许手机号或邮箱都为空, 也不需要验证码
    for u in user_list:
        # 不允许修改管理员
        # if u["account"] == 'admin':
        #     return res_format(err="放肆! 不允许修改管理员权限")
        # 因为前端限制直接修改ldap用户的某些字段, 所以一些条件只检查本地用户的
        if u["befrom"] == 'local':
            check.rule_tel(u["tel"], not_null=False, need_code=False)
            check.rule_email(u["email"], not_null=False, need_code=False)
            check.rule_displayname(u["displayname"])
        # check.rule_account(u["account"])
    # 检查提交的列表中账号是否有重复的
    check.check_account_repeat(user_account_list)
    # 检查有没有不存在的用户
    check.check_users_exist_local(user_account_list)

    # 初始化数据库连接池
    mp = MysqlPool()

    # 传入的角色的列表
    list_role_input = []
    # 传入的组的列表
    list_group_input = []
    # 执行insert的sql的模板列表
    list_sql = []
    # 执行insert的sql的数据列表
    data_sql = {}
    n = 1
    nr = 1
    ng = 1
    # 用户权限中间表的值
    list_sql_role_value = []
    # 用户组中间表的值
    list_sql_group_value = []

    for user_info in user_list:
        # 模板部分
        list_sql.append(f"""
            update sw_user set
                displayname = %(displayname_{n})s,
                email = %(email_{n})s,
                tel = %(tel_{n})s,
                status = %(status_{n})s
            where
                account = %(account_{n})s
                and befrom = %(befrom_{n})s;
        """)

        # 数据部分
        data_sql[f"displayname_{n}"] = user_info["displayname"]
        data_sql[f"email_{n}"] = user_info["email"]
        data_sql[f"tel_{n}"] = user_info["tel"]
        data_sql[f"status_{n}"] = user_info["status"]
        data_sql[f"account_{n}"] = user_info["account"]
        data_sql[f"befrom_{n}"] = user_info["befrom"]

        # 装填权限数据, 这里注意字段名与user表重复, 要加点字符
        for r in user_info["roles"]:
            list_sql_role_value.append(f"(%(account_{n})s,%(role_id_{nr})s)")
            data_sql[f"role_id_{nr}"] = r
            list_role_input.append(r)
            nr += 1
        # 装填组数据
        for g in user_info["groups"]:
            list_sql_group_value.append(f"(%(account_{n})s,%(group_id_{ng})s)")
            data_sql[f"group_id_{ng}"] = g
            list_group_input.append(g)
            ng += 1

        n += 1

    data_sql["tmp_account_list"] = user_account_list

    # 组装权限sql
    # 删除现有的权限的关联关系
    sql_delete_roles = "delete from sw_roleuser where account in %(tmp_account_list)s;"
    list_sql.append(sql_delete_roles)
    # 用户权限中间表的模板
    if list_sql_role_value:
        list_sql_role_tem = f"""
            insert into sw_roleuser
                (account,role_id)
            values {','.join(list_sql_role_value)};
        """
        list_sql.append(list_sql_role_tem)

    # 组装组sql
    # 删除现有的组关系
    sql_delete_group = "delete from sw_usergroup where account in %(tmp_account_list)s;"
    list_sql.append(sql_delete_group)
    # 用户组中间表的模板
    if list_sql_group_value:
        list_sql_group_tem = f"""
            insert into sw_usergroup
                (account,group_id)
            values {','.join(list_sql_group_value)};
        """
        list_sql.append(list_sql_group_tem)


    # 获取所有组名
    sql_select_group = "select group_id from sw_group"
    res_db_group = mp.fetch_all(sql_select_group, )
    list_group_db = [i["group_id"] for i in res_db_group]
    # 如果有, 说明不存在, 报错
    for g in list_group_input:
        if g not in list_group_db:
            return res_format(err=f"组{g}不存在", code=10002)

    # 获取所有规则名
    sql_select_group = "select role_id from sw_role"
    res_db_roles = mp.fetch_all(sql_select_group)
    list_role_db = [i["role_id"] for i in res_db_roles]
    for r in list_role_input:
        if r not in list_role_db:
            return res_format(err=f"没有{r}这个角色名", code=10002)

    # for i in list_sql:
    #     print(i)
    # print(data_sql)

    mp.transaction(list_sql, data_sql, is_list=True)

    return {"ok": "ok"}


def delete_batch(data_req):
    """
    批量删除用户 (包括ldap)
    :param data_req: 用户传来的请求主体, 应包含
    :return:
    """

    try:
        user_list = data_req['user_list']
        for u in user_list:
            if sorted(u.keys()) != sorted(["account", "befrom"]):
                raise ZeroDivisionError(f"某待删除用户的传参和预期不符: {u}")
    except Exception as el:
        logging.error(f"报文格式错误: {data_req}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 将要删除的用户归类
    tmp_account_list = []
    user_dict = defaultdict(list)
    for u in user_list:
        if u["account"] == 'admin':
            return res_format(err="放肆! 竟妄图删除管理员")
        user_dict[u["befrom"]].append(u["account"])
        tmp_account_list.append(u["account"])

    # 初始化数据库连接池
    mp = MysqlPool()

    sql_list = []
    sql_data = {}
    # 拼接delete语句
    for k, v in user_dict.items():
        sql_tem_delete_local = f"""
            delete from sw_user 
            where 
                befrom = %(befrom_{k})s
                and account in %(account_list_{k})s;
        """
        sql_list.append(sql_tem_delete_local)
        sql_data[f"befrom_{k}"] = k
        sql_data[f"account_list_{k}"] = v

    sql_data["tmp_account_list"] = tmp_account_list

    # 删除现有的权限关系
    sql_delete_roles = "delete from sw_roleuser where account in %(tmp_account_list)s;"
    sql_list.append(sql_delete_roles)

    # 删除现有的组关系
    sql_delete_group = "delete from sw_usergroup where account in %(tmp_account_list)s;"
    sql_list.append(sql_delete_group)


    mp.transaction(sql_list, sql_data, is_list=True)

    return {"ok": "ok"}


def freeze_batch(data_req):
    """
    批量修改用户状态 (on或off)
    :param data_req: 用户传入的数据, 包括 status状态, user_list用户列表
    :return:
    """

    try:
        status = data_req['status']
        user_list = data_req['user_list']
        for u in user_list:
            if sorted(u.keys()) != sorted(["account", "befrom"]):
                raise ZeroDivisionError(f"某待删除用户的传参和预期不符: {u}")

    except Exception as el:
        logging.error(f"报文格式错误: {data_req}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 验证status的值, 只能为on或off
    if status not in ["on", "off"]:
        raise ZeroDivisionError("status的值不在预期中")

    # 将要更新的用户归类
    user_dict = defaultdict(list)
    for u in user_list:
        user_dict[u["befrom"]].append(u["account"])

    # 初始化数据库连接池
    mp = MysqlPool()

    sql_list = []
    sql_data = {"status": status}
    # 拼接update语句
    for k, v in user_dict.items():
        sql_tem_delete_local = f"""
            update sw_user 
            set status = %(status)s
            where 
                befrom = %(befrom_{k})s
                and account in %(account_list_{k})s;
        """
        sql_list.append(sql_tem_delete_local)
        sql_data[f"befrom_{k}"] = k
        sql_data[f"account_list_{k}"] = v

    mp.transaction(sql_list, sql_data, is_list=True)

    return {"ok": "ok"}


def changepasswd_batch(data_req):
    """
    批量重置本地用户密码
    :param data_req:
    :return:
    """

    try:
        user_list = data_req['user_list']
        for u in user_list:
            if sorted(u.keys()) != sorted(["account", "password"]):
                raise ZeroDivisionError(f"某待删除用户的传参和预期不符: {u}")

    except Exception as el:
        logging.error(f"报文格式错误: {data_req}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 初始化数据库连接池
    mp = MysqlPool()

    n = 1
    sql_tem_list = []
    sql_insert_user_data = {}
    for user_info in user_list:
        # 模板部分
        sql_tem_list.append(f"""
                update sw_user 
                set password = %(password_{n})s
                where
                    account = %(account_{n})s
                    and befrom = 'local';
            """)

        # 数据部分
        sql_insert_user_data[f"password_{n}"] = user_info["password"]
        sql_insert_user_data[f"account_{n}"] = user_info["account"]
        n += 1
    # 组合sql模板

    # print(sql_tem_list)
    # print(sql_insert_user_data)
    # print(mp.print(sql_tem, sql_insert_user_data))
    mp.transaction(sql_tem_list, sql_insert_user_data, is_list=True)

    return {"ok": "ok"}
