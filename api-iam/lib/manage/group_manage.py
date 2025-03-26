from ..db.db_select import kvdb
from ..data_format import res_format, str_to_md5
from ..db.exec_ql import MysqlPool
from ..user.check import rule_displayname, rule_desc
import logging
import re


def group_get(data_req):
    """
    获取所有用户组, 以及组对应的角色和用户
    :param data_req: 前端请求的信息, 只要不为空就随意
    :return:
    """

    # 定义返回数据的格式
    data_res = {}

    # 初始化数据库连接池
    ms = MysqlPool()
    # 拼写查询sql
    # sql_select_tem = """
    #     select
    #         g.*,
    #         GROUP_CONCAT(DISTINCT ug.account ORDER BY ug.account SEPARATOR ',') AS users,
    #         GROUP_CONCAT(DISTINCT rg.role_id ORDER BY rg.role_id SEPARATOR ',') AS roles
    #     from sw_group g
    #     left join sw_rolegroup rg on rg.group_id = g.group_id
    #     left join sw_usergroup ug on ug.group_id = g.group_id
    #     group by g.group_id;
    # """
    sql_select_tem = """
        select 
            g.*,
            ug.account,
            u.displayname,
            rg.role_id,
            r.role_desc
        from sw_group g
        left join sw_rolegroup rg on rg.group_id = g.group_id
        left join sw_usergroup ug on ug.group_id = g.group_id
        left join sw_user u on u.account = ug.account
        left join sw_role r on r.role_id = rg.role_id
    """

    # 查询并返回结果
    list_res_db = ms.fetch_all(sql_select_tem)

    # for res_db in list_res_db:
    #     res_db["roles"] = re.split(',', res_db["roles"] or "")
    #     res_db["users"] = re.split(',', res_db["users"] or "")
    #     data_res.append(res_db)

    # 规整数据, 以group_id为主键
    for res in list_res_db:

        group_id = res["group_id"]
        group_desc = res["group_desc"]
        date_create = res["date_create"]
        date_update = res["date_update"]
        account = res["account"]
        displayname = res["displayname"]
        role_id = res["role_id"]
        role_desc = res["role_desc"]

        if group_id not in data_res:
            gi = {
                "group_id": group_id,
                "group_desc": group_desc,
                "date_create": date_create,
                "date_update": date_update,
                "roles": [],
                "users": []
            }
            data_res[group_id] = gi

        # 装填此次的用户
        if account:
            ui = {
                "account": account,
                "displayname": displayname,
            }
            if ui not in data_res[group_id]["users"]:
                data_res[group_id]["users"].append(ui)

        # 装填此次的角色
        if role_id:
            ri = {
                "role_id": role_id,
                "role_desc": role_desc,
            }
            if ri not in data_res[group_id]["roles"]:
                data_res[group_id]["roles"].append(ri)

    # return list(data_res.values())
    # 还是改为返回字典, 由前端自己转为列表, 不然不好定位当前选定了哪个组
    return data_res


def group_create(data_req):
    """
    创建用户组
    :param data_req: 前端传来的请求数据, 需要包括: group_id, group_desc, roles, users
    :return:
    """

    # 解析传入的信息
    try:
        group_id = data_req["group_id"]
        group_desc = data_req["group_desc"]
        roles_input = data_req["roles"]
        users_input = data_req["users"]
        if not isinstance(roles_input, list):
            return res_format(err="roles格式错误", code=10002)
        if not isinstance(users_input, list):
            return res_format(err="users格式错误", code=10002)

    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 以用户显示名的标准校验组名
    rule_displayname(group_id)
    # 校验描述信息的长度
    rule_desc(group_desc)

    # 初始化数据库
    mp = MysqlPool()
    sql_list = []
    sql_insert_group_data = {}

    # 获取所有组名
    sql_select_group = "select group_id from sw_group where group_id = %(group_id)s;"
    res_db_group = mp.fetch_one(sql_select_group, {"group_id": group_id})
    # 如果有, 说明已存在, 报错
    if res_db_group:
        return res_format(err=f"组{group_id}已存在", code=10002)

    # 获取所有规则名
    sql_select_group = "select role_id from sw_role"
    res_db_roles = mp.fetch_all(sql_select_group)
    list_role_db = [i["role_id"] for i in res_db_roles]
    for i in roles_input:
        if i not in list_role_db:
            return res_format(err=f"没有{i}这个角色名", code=10002)

    # 获取所有用户名
    sql_select_account = "select account from sw_user;"
    res_db_account = mp.fetch_all(sql_select_account)
    list_account_db = [i["account"] for i in res_db_account]
    for i in users_input:
        if i not in list_account_db:
            return res_format(err=f"没有{i}这个账号", code=10002)

    # 经过了组织的考验, 新建这个组
    sql_insert_group_tem = """
        insert into sw_group (group_id, group_desc, date_create, date_update)
        values (%(group_id)s, %(group_desc)s, now(), now());
    """

    sql_insert_group_data["group_id"] = group_id
    sql_insert_group_data["group_desc"] = group_desc
    sql_list.append(sql_insert_group_tem)

    # 删除现有的权限的关联关系
    sql_delete_roles = "delete from sw_rolegroup where group_id = %(group_id)s;"
    sql_list.append(sql_delete_roles)
    # 一并新建权限的关联关系
    if roles_input:
        nr = 0
        sql_insert_role_tem_line_list = []
        for role_id in roles_input:
            sql_insert_role_tem_line_list.append(f"""
                (%(group_id)s, %(role_id_{nr})s)""")
            sql_insert_group_data[f"role_id_{nr}"] = role_id
            nr += 1

        sql_insert_role_tem_line_str = ',\n\t\t\t'.join(sql_insert_role_tem_line_list)
        sql_insert_role_tem = f"""
            replace into sw_rolegroup (group_id, role_id) values
                {sql_insert_role_tem_line_str};
        """
        sql_list.append(sql_insert_role_tem)


    # 删除现有的用户关联
    sql_delete_users = "delete from sw_usergroup where group_id = %(group_id)s;"
    sql_list.append(sql_delete_users)
    # 一并新建用户的关联关系
    if users_input:
        nu = 0
        sql_insert_user_tem_line_list = []
        for account in users_input:
            sql_insert_user_tem_line_list.append(f"""
                (%(group_id)s, %(account_{nu})s)""")
            sql_insert_group_data[f"account_{nu}"] = account
            nu += 1

        sql_insert_user_tem_line_str = ',\n\t\t\t'.join(sql_insert_user_tem_line_list)
        sql_insert_user_tem = f"""
            replace into sw_usergroup (group_id, account) values
                {sql_insert_user_tem_line_str};
            """
        sql_list.append(sql_insert_user_tem)


    for i in sql_list:
        print(i)

    # 执行
    mp.transaction(sql_list, sql_insert_group_data, is_list=True)
    logging.info(f"成功新建组: {group_id}, 包含权限: {roles_input}, 包含用户: {users_input}, 描述: {group_desc}")

    return {"ok": "ok"}


def group_update(data_req):
    """
    更新用户组信息
    :param data_req: 前端传来的请求数据, 需要包括: group_id, group_desc, roles, users
    :return:
    """
    # 解析传入的信息
    try:
        group_id = data_req["group_id"]
        group_desc = data_req["group_desc"]
        roles_input = data_req["roles"]
        users_input = data_req["users"]
        if not isinstance(roles_input, list):
            return res_format(err="roles格式错误", code=10002)
        if not isinstance(users_input, list):
            return res_format(err="users格式错误", code=10002)

    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 以用户显示名的标准校验组名
    rule_displayname(group_id)
    # 校验描述信息的长度
    rule_desc(group_desc)

    # 初始化数据库
    mp = MysqlPool()
    sql_list = []
    sql_insert_group_data = {}

    # 获取所有组名
    sql_select_group = "select group_id from sw_group where group_id = %(group_id)s"
    res_db_group = mp.fetch_one(sql_select_group, {"group_id": group_id})
    # 如果没有, 说明不存在, 报错
    if not res_db_group:
        return res_format(err=f"组{group_id}不存在", code=10002)

    # 获取所有规则名
    if roles_input:
        sql_select_role = "select role_id from sw_role"
        res_db_roles = mp.fetch_all(sql_select_role)
        list_role_db = [i["role_id"] for i in res_db_roles]
        for i in roles_input:
            if i not in list_role_db:
                return res_format(err=f"没有{i}这个角色名", code=10002)

    # 获取所有用户名
    if users_input:
        sql_select_account = "select account from sw_user"
        res_db_account = mp.fetch_all(sql_select_account)
        list_account_db = [i["account"] for i in res_db_account]
        for i in users_input:
            if i not in list_account_db:
                return res_format(err=f"没有{i}这个账号", code=10002)

    # 经过了组织的考验, 更新这个组
    sql_update_group_tem = """
            update sw_group
            set 
                group_desc = %(group_desc)s,
                date_update = now()
            where
                group_id = %(group_id)s;
        """
    sql_insert_group_data["group_id"] = group_id
    sql_insert_group_data["group_desc"] = group_desc
    sql_list.append(sql_update_group_tem)

    # 删除现有的权限的关联关系
    sql_delete_roles = "delete from sw_rolegroup where group_id = %(group_id)s;"
    sql_list.append(sql_delete_roles)
    # 新建权限的关联关系
    if roles_input:
        nr = 0
        sql_insert_role_tem_line_list = []
        for role_id in roles_input:
            sql_insert_role_tem_line_list.append(f"""
                    (%(group_id)s, %(role_id_{nr})s)""")
            sql_insert_group_data[f"role_id_{nr}"] = role_id
            nr += 1

        sql_insert_role_tem_line_str = ',\n\t\t\t'.join(sql_insert_role_tem_line_list)
        sql_insert_role_tem = f"""
                replace into sw_rolegroup (group_id, role_id) values
                    {sql_insert_role_tem_line_str};
            """
        sql_list.append(sql_insert_role_tem)

    # 删除现有的用户关联
    sql_delete_users = "delete from sw_usergroup where group_id = %(group_id)s;"
    sql_list.append(sql_delete_users)
    # 新建用户的关联关系
    if users_input:
        nu = 0
        sql_insert_user_tem_line_list = []
        for account in users_input:
            sql_insert_user_tem_line_list.append(f"""
                    (%(group_id)s, %(account_{nu})s)""")
            sql_insert_group_data[f"account_{nu}"] = account
            nu += 1

        sql_insert_user_tem_line_str = ',\n\t\t\t'.join(sql_insert_user_tem_line_list)
        sql_insert_user_tem = f"""
                replace into sw_usergroup (group_id, account) values
                    {sql_insert_user_tem_line_str};
                """
        sql_list.append(sql_insert_user_tem)

    # for i in sql_list:
    #     print(i)

    # 执行
    mp.transaction(sql_list, sql_insert_group_data, is_list=True)
    logging.info(f"成功更新组: {group_id}, 包含权限: {roles_input}, 包含用户: {users_input}, 描述: {group_desc}")

    return {"ok": "ok"}


def group_delete(data_req):
    """
    删除用户组, 以及其相关权限和用户关联关系
    :param data_req: 需要包含 group_id
    :return:
    """

    # 解析传入的信息
    try:
        group_id = data_req["group_id"]

    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 以用户显示名的标准校验组名
    rule_displayname(group_id)

    # 组合删除用户关系的语句
    sql_delete_users = "delete from sw_usergroup where group_id = %(group_id)s;"
    # 组合删除角色关系的语句
    sql_delete_roles = "delete from sw_rolegroup where group_id = %(group_id)s;"
    # 组合删除用户组本身的语句
    sql_delete_group = "delete from sw_group where group_id = %(group_id)s;"

    # 组合数据
    sql_delete_data = {
        "group_id": group_id
    }
    sql_tem_list = [
        sql_delete_users,
        sql_delete_roles,
        sql_delete_group
    ]

    # 初始化数据库
    mp = MysqlPool()

    # 执行
    mp.transaction(sql_tem_list, sql_delete_data, is_list=True)
    logging.info(f"用户组{group_id}已删除")

    return {"ok": "ok"}