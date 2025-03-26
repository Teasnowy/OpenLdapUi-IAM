from ..db.exec_ql import MysqlPool
from ..data_format import res_format
from .check import rule_displayname, rule_ous_attrs, rule_account
from ..db.ldap_general import ldap_search, decorator_ldap, ldap_getattrs, format_ou_users
import logging


@decorator_ldap
def ous_check(data_request):
    """
    此函数用于查询所有的ldap搜索组
    :param data_request: 前端传来的数据, 应包含
    :return:
    """

    # 解析传入的信息
    try:
        # 传什么都可以, 只要不为空就行
        pass
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 定义返回数据的格式
    data_result = {}

    # 初始化数据库连接池
    ms = MysqlPool()
    # 拼写查询sql
    sql_select_tem = """
        select * from sw_ldap_ous
    """

    # 查询并返回结果
    list_res_db = ms.fetch_all(sql_select_tem)
    for res_db in list_res_db:
        ou_name = res_db["ou_name"]
        data_result[ou_name] = res_db

    return data_result


@decorator_ldap
def ous_create(data_request):
    """
    此函数用于创建新的ldap搜索组
    :param data_request: 前端传来的数据, 应包含
    :return:
    """

    # 解析传入的信息
    try:
        ou_name = data_request["ou_name"]
        ou_base = data_request["ou_base"]
        ou_search = data_request["ou_search"]
        can_login_directly = data_request["can_login_directly"]
        description = data_request["description"]
        # as_account其实是不生效的, 真正的用户名是添加用户时管理员指定的
        as_account = data_request["as_account"]
        as_displayname = data_request["as_displayname"]
        as_tel = data_request["as_tel"]
        as_email = data_request["as_email"]
        as_password = data_request["as_password"]

    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 用校验用户显示名的规则校验方案名
    rule_displayname(ou_name)
    # 校验属性名字列表
    search_attrs = [as_account, as_displayname, as_tel, as_email, as_password]
    rule_ous_attrs(search_attrs)

    # 定义返回数据格式
    data_result = {
        "ok": True
    }

    # 初始化数据库连接池
    ms = MysqlPool()

    # 拼写查询sql, 先确定不重名
    sql_select_tem = """
        select 1 from sw_ldap_ous where ou_name = %(ou_name)s
    """
    sql_select_data = {"ou_name": ou_name}

    # 如果查询到了数据, 就说明有重名的搜索方案已经被定义了
    res_db_select = ms.fetch_all(sql_select_tem, sql_select_data)
    if res_db_select:
        raise ZeroDivisionError("已有同名的ldap匹配方案")

    # 拼写insert语句, 新建匹配方案
    sql_insert_tem = """
        insert into sw_ldap_ous (ou_id, ou_name, ou_base, ou_search, can_login_directly, description, as_account, 
            as_displayname, as_tel, as_email, as_password)
        values
            (null, %(ou_name)s, %(ou_base)s, %(ou_search)s, %(can_login_directly)s, %(description)s, %(as_account)s, 
            %(as_displayname)s, %(as_tel)s, %(as_email)s, %(as_password)s)
    """
    sql_insert_data = {
        "ou_name": ou_name,
        "ou_base": ou_base,
        "ou_search": ou_search,
        "can_login_directly": can_login_directly,
        "description": description,
        "as_account": as_account,
        "as_displayname": as_displayname,
        "as_tel": as_tel,
        "as_email": as_email,
        "as_password": as_password,
    }
    ms.transaction(sql_insert_tem, sql_insert_data)
    logging.info(f"已成功创建ldap的匹配方案{ou_name}: {sql_insert_data}")

    return data_result


@decorator_ldap
def ous_update(data_request):
    """
    此函数用于更新ldap搜索方案
    :param data_request: 前端传来的数据, 应包含
    :return:
    """

    # 解析传入的信息
    try:
        ou_name = data_request["ou_name"]
        ou_base = data_request["ou_base"]
        ou_search = data_request["ou_search"]
        can_login_directly = data_request["can_login_directly"]
        description = data_request["description"]
        as_account = data_request["as_account"]
        as_displayname = data_request["as_displayname"]
        as_tel = data_request["as_tel"]
        as_email = data_request["as_email"]
        as_password = data_request["as_password"]

    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 用校验用户显示名的规则校验方案名
    rule_displayname(ou_name)
    # 校验属性名字列表
    search_attrs = [as_account, as_displayname, as_tel, as_email, as_password]
    rule_ous_attrs(search_attrs)

    # 初始化数据库连接池
    ms = MysqlPool()

    # 拼写查询sql, 先确定不重名
    sql_select_tem = """
        select 1 from sw_ldap_ous where ou_name = %(ou_name)s
    """
    sql_select_data = {"ou_name": ou_name}

    # 如果查询到了数据, 就说明有这个方案
    res_db_select = ms.fetch_all(sql_select_tem, sql_select_data)
    if not res_db_select:
        raise ZeroDivisionError(f"没有这个方案名字: {ou_name}")

    # 拼写更新语句
    sql_update_tem = """
            update sw_ldap_ous set 
                ou_base = %(ou_base)s,
                ou_search = %(ou_search)s,
                can_login_directly = %(can_login_directly)s,
                description = %(description)s,
                as_account = %(as_account)s,
                as_displayname = %(as_displayname)s,
                as_tel = %(as_tel)s,
                as_email = %(as_email)s,
                as_password = %(as_password)s
            where
                ou_name = %(ou_name)s
        """
    sql_update_data = {
        "ou_name": ou_name,
        "ou_base": ou_base,
        "ou_search": ou_search,
        "can_login_directly": can_login_directly,
        "description": description,
        "as_account": as_account,
        "as_displayname": as_displayname,
        "as_tel": as_tel,
        "as_email": as_email,
        "as_password": as_password,
    }
    # 执行更新
    ms.transaction(sql_update_tem, sql_update_data)
    # 这里取消, 再次查询并返回, 改由客户端自己查询
    # data_result = ous_check(None)
    data_result = {"ok": "ok"}
    return data_result

@decorator_ldap
def ous_delete(data_request):
    """
    此函数用于删除ldap搜索方案
    :param data_request: 前端传来的数据, 应包含
    :return:
    """

    # 解析传入的信息
    try:
        ou_name = data_request["ou_name"]
        user_clear = data_request["user_clear"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 用校验用户显示名的规则校验方案名
    rule_displayname(ou_name)

    # 定义返回数据格式
    data_result = {
        "ok": "ok"
    }

    # 初始化数据库连接池
    ms = MysqlPool()

    # 拼写查询sql, 先确定不重名 (没必要, 注释了)
    # sql_select_tem = """
    #         select 1 from sw_ldap_ous where ou_name = %(ou_name)s
    #     """
    # sql_select_data = {"ou_name": ou_name}
    #
    # # 如果查询到了数据, 就说明有重名的搜索方案已经被定义了, 再删除
    # res_db_select = ms.fetch_all(sql_select_tem, sql_select_data)
    # if res_db_select:

    # 拼写删除sql
    sql_delete_tem = """
        delete from sw_ldap_ous where ou_name = %(ou_name)s
    """
    sql_delete_data = {"ou_name": ou_name}
    ms.transaction(sql_delete_tem, sql_delete_data)
    logging.info(f"成功删除LDAP组{ou_name}")

    # 如果要一并清理用户
    if user_clear:
        sql_delete_user_tem = """
            delete from sw_user where ou_name = %(ou_name)s
        """
        sql_delete_user_data = {"ou_name": ou_name}
        ms.transaction(sql_delete_user_tem, sql_delete_user_data)
        logging.info(f"成功删除LDAP组{ou_name}所属的用户")

        # 再次查询并返回
        # data_result = ous_check(None)

    # else:
    #     raise ZeroDivisionError(f"没有这个方案名字: {ou_name}")

    return data_result


@decorator_ldap
def ous_search_tmp(data_request):
    """
    依靠临时提供的ldap搜索方案来获取其中的用户及用户信息
    :param data_request:
    :return:
    """
    # 解析传入的信息
    try:
        ou_name = data_request["ou_name"]
        ou_base = data_request["ou_base"]
        ou_search = data_request["ou_search"]
        can_login_directly = data_request["can_login_directly"]
        description = data_request["description"]
        as_account = data_request["as_account"]
        as_displayname = data_request["as_displayname"]
        as_tel = data_request["as_tel"]
        as_email = data_request["as_email"]
        as_password = data_request["as_password"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 组合属性名字字典, key是对应的属性名, value是要返回给前端的易懂字段名
    # search_attrs = [as_account, as_displayname, as_tel, as_email, as_password]
    search_attrs = {
        "account": as_account,
        "displayname": as_displayname,
        "tel": as_tel,
        "email": as_email,
        "password": as_password,
        # as_account: "account",
        # as_displayname: "displayname",
        # as_tel: "tel",
        # as_email: "email",
        # as_password: "password"
    }
    # 校验属性是否存在于ldap中
    rule_ous_attrs(list(search_attrs.values()))

    # 根据用户传入的信息去ldap搜索该方案的用户信息, 屏蔽掉密码信息
    dict_ldap_users = ldap_search(ou_base, ou_search, list(search_attrs.values()), ignore_passwd=True, attr_passwd=as_password)

    # 格式化搜索到的ldap用户
    dict_ldap_users = format_ou_users(dict_ldap_users, search_attrs)

    data_res = {
        "users": dict_ldap_users,
        "attrs": search_attrs
    }

    return data_res


@decorator_ldap
def ous_search_exists(data_request):
    """
    依靠数据库中已存在的ldap搜索方案模板的名字来获取其中的用户及用户信息
    :param data_request:
    :return:
    """
    # 解析传入的信息
    try:
        ou_name = data_request["ou_name"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 初始化数据库连接池
    ms = MysqlPool()

    # 拼写查询sql, 先获取所有需要获取的方案信息
    sql_select_tem = """
            select * from sw_ldap_ous where ou_name = %(ou_name)s
        """
    sql_select_data = {"ou_name": ou_name}

    # 如果为空, 说明没有这个方案
    list_res_db_select = ms.fetch_all(sql_select_tem, sql_select_data)
    if not list_res_db_select:
        raise ZeroDivisionError("没有这个名字的ldap匹配方案")

    res_db_select = list_res_db_select[0]

    # 解析数据库里的字段
    ou_base = res_db_select["ou_base"]
    ou_search = res_db_select["ou_search"]
    as_account = res_db_select["as_account"]
    as_displayname = res_db_select["as_displayname"]
    as_tel = res_db_select["as_tel"]
    as_email = res_db_select["as_email"]
    as_password = res_db_select["as_password"]

    # 组合属性名字字典, key是对应的属性名, value是要返回给前端的易懂字段名
    # search_attrs = [as_account, as_displayname, as_tel, as_email, as_password]
    search_attrs = {
        "account": as_account,
        "displayname": as_displayname,
        "tel": as_tel,
        "email": as_email,
        "password": as_password,
        # as_account: "account",
        # as_displayname: "displayname",
        # as_tel: "tel",
        # as_email: "email",
        # as_password: "password"
    }
    # 校验属性是否存在于ldap中
    rule_ous_attrs(list(search_attrs.values()))

    # 根据用户传入的信息去ldap搜索该方案的用户信息, 屏蔽掉密码信息
    dict_ldap_users = ldap_search(ou_base, ou_search, list(search_attrs.values()), ignore_passwd=True, attr_passwd=as_password)
    # logging.info(f"返回检索到的ldap用户: {dict_ldap_users}")
    # 格式化搜索到的ldap用户
    dict_ldap_users = format_ou_users(dict_ldap_users, search_attrs)
    # logging.info(f"格式化后的ldap用户: {dict_ldap_users}")
    data_res = {
        "users": dict_ldap_users,
        "attrs": search_attrs
    }

    return data_res


@decorator_ldap
def ous_user_add(data_request):
    """
    从搜索方案中挑选出用户后新增进sw_user表
    :param data_request: 前端传来的数据
    :return:
    """

    # 解析传入的信息, 不需要密码, 登录时直接向ldap服务器验证
    try:
        # ldap_ou_name = data_request["ldap_ou_name"]
        dict_user_info = data_request["dict_user_info"]
        for k, v in dict_user_info.items():
            if sorted(v.keys()) != sorted(
                ["ldap_ou_name", "account", "ldap_dn", "tel", "displayname", "roles", "groups", "email", "status"]
            ):
                logging.error("user_info中的数据缺少字段")
                return res_format(err="传入的json数据格式错误", code=10002)

    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 验证是否超长
    if len(dict_user_info) > 50:
        return res_format(err="最多同时创建50个用户", code=10002)
    if not dict_user_info:
        return res_format(err="未传入有效用户", code=10002)
    # 验证账号格式
    for i in dict_user_info.values():
        rule_account(i["account"])

    # 初始化数据库
    mp = MysqlPool()

    # 验证是否有这个组
    sql_select_ldap_tem = """
        select ou_name from sw_ldap_ous;
    """
    list_res_db_ous = mp.fetch_all(sql_select_ldap_tem)
    res_db_ounames = [i["ou_name"] for i in list_res_db_ous]
    list_input_ounames = [v["ldap_ou_name"] for k, v in dict_user_info.items()]
    # 取集合 数据库对输入 的 差集
    coll_ouname = list(set(list_input_ounames) - set(res_db_ounames))
    if coll_ouname:
        coll_ouname_str = '\n\t'.join(coll_ouname)
        return res_format(data=coll_ouname, err=f"以下ldap组不存在: \n\t{coll_ouname_str}", code=10003)

    # 验证数据库中是否已有这些用户名和dn,  (现在和本地用户的账号也不能重复)
    # sql_select_ldap_tem = """
    #     select account,ldap_dn from sw_user where befrom = 'ldap';
    # """
    sql_select_ldap_tem = """
        select account,ldap_dn from sw_user;
    """
    list_res_db = mp.fetch_all(sql_select_ldap_tem)
    # 看dn是否已经存在
    res_db_dn = [i["ldap_dn"] for i in list_res_db]
    # 取集合交集
    coll_dn = list(set(res_db_dn) & set(dict_user_info.keys()))
    if coll_dn:
        coll_dn_str = '\n\t'.join(coll_dn)
        return res_format(data=coll_dn, err=f"以下dn已被用户使用: \n\t{coll_dn_str}", code=10003)
    # 看看账户名是不是已经存在
    res_db_account = [i["ldap_dn"] for i in list_res_db]
    list_input_account = [v["account"] for k, v in dict_user_info.items()]
    coll_account = list(set(res_db_account) & set(list_input_account)) # 取集合交集
    if coll_account:
        return res_format(data=coll_account, err=f"以下账户名已存在: \n\t{','.join(coll_account)}", code=10003)

    # 定义insert的可变的字段
    # set_column = ('account', 'displayname', 'roles', 'email', 'tel', 'ldap_dn', 'ldap_ou_name')
    # 验证通过后开始组合SQL语句

    # n = 1
    # list_sql_values = []
    # sql_insert_user_data = {}
    # for dn, user_info in dict_user_info.items():
    #     # 模板部分
    #     values_tem = f'_{n})s, %('.join(set_column)
    #     sql_values = f"(null,'ldap','on',null,now(),now(),now(),%({values_tem}_{n})s)"
    #     list_sql_values.append(sql_values)
    #     # 数据部分
    #     for c in set_column:
    #         if c == "role_id":
    #             sql_insert_user_data[f'{c}_{n}'] = ','.join(user_info[c])
    #         else:
    #             sql_insert_user_data[f'{c}_{n}'] = user_info[c]
    #
    #     n += 1
    # # 组合sql模板
    # str_sql_values = ',\n\t\t\t'.join(list_sql_values)
    # sql_insert_user_tem = f"""
    #     insert into sw_user
    #         (user_id,befrom,status,password,date_create,date_update,date_latest_login,{','.join(set_column)})
    #     values
    #         {str_sql_values};
    # """

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

    for k, u in dict_user_info.items():
        list_sql_user_value.append(
            f"(null,'ldap',null,now(),now(),now(),%(account_{n})s,%(displayname_{n})s,%(email_{n})s,"
            f"%(tel_{n})s,%(status_{n})s,%(ldap_dn_{n})s,%(ldap_ou_name_{n})s)"
        )
        # 装填用户一般数据
        data_sql[f"account_{n}"] = u['account']
        data_sql[f"displayname_{n}"] = u['displayname']
        data_sql[f"email_{n}"] = u['email']
        data_sql[f"tel_{n}"] = u['tel']
        data_sql[f"status_{n}"] = u['status']
        data_sql[f"ldap_dn_{n}"] = u['ldap_dn']
        data_sql[f"ldap_ou_name_{n}"] = u['ldap_ou_name']
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
            (user_id,befrom,password,date_create,date_update,date_latest_login,
                account,displayname,email,tel,status,ldap_dn,ldap_ou_name)
        values {','.join(list_sql_user_value)};
    """
    list_sql.append(list_sql_user_tem)
    # 用户权限中间表的模板
    if list_sql_role_value:
        list_sql_role_tem = f"""
            insert into sw_roleuser
                (account,role_id)
            values {','.join(list_sql_role_value)};
        """
        list_sql.append(list_sql_role_tem)
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

    for i in list_sql:
        print(i)
    print(data_sql)

    mp.transaction(list_sql, data_sql, is_list=True)

    return {"ok": "ok"}


@decorator_ldap
def ous_user_del(data_request):
    """
    删除指定ous组的ldap用户
    :param data_request: 前端传来的数据
    :return:
    """

    # 解析传入的信息, 不需要密码, 登录时直接向ldap服务器验证
    try:
        ldap_ou_name = data_request["ldap_ou_name"]
        account = data_request["account"]

    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 校验数据
    # 数据不能为空
    if not ldap_ou_name:
        return res_format(err='组名不能为空')
    if not account:
        return res_format(err='用户名不能为空')

    # 初始化数据库
    mp = MysqlPool()
    # 组合删除语句
    sql_delete_user_tem = """
        delete from sw_user where account = %(account)s and befrom = 'ldap' and ldap_ou_name = %(ldap_ou_name)s;
    """
    sql_delete_user_data = {"account": account, "ldap_ou_name": ldap_ou_name}

    # 执行删除
    mp.transaction(sql_delete_user_tem, sql_delete_user_data)

    return


@decorator_ldap
def get_ldap_attrs(data_request):
    """
    用于获取ldap服务器中的所有属性列表
    :param data_request:
    :return:
    """

    return ldap_getattrs()