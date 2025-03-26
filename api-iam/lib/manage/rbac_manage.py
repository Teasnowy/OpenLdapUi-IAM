from ..db.db_select import kvdb
from ..data_format import res_format, str_to_md5
from ..db.exec_ql import MysqlPool, manual_substitute
import logging
from collections import defaultdict
from ..user.check import rule_displayname, rule_desc


def get_dict(data_req):
    """
    获取数据库中目前的role的id
    :param data_req: 任意数据
    :return:
    """
    # 初始化数据库连接池
    mp = MysqlPool()
    # 加密前端此时传来的密码

    # sql_tmp = """
    #     select * from sw_role;
    #     select * from sw_roleuser;
    # """
    # a = mp.fetch_all(sql_tmp)
    # # return a
    # logging.info(a)

    sql_select_template = """
            select
                r.*,
                u.account, u.displayname,
                g.group_id, g.group_desc,
                w.web_route, w.web_name, w.web_desc,
                c.container_name, c.container_desc,
                i.api_url, i.api_endpoint
        from 
                sw_role r
                left join sw_roleuser sru on sru.role_id = r.role_id
                left join sw_rolegroup srg on srg.role_id = r.role_id
                left join sw_roleweb srw on srw.role_id = r.role_id
                left join sw_rolecontainer src on src.role_id = r.role_id
                left join sw_user u on u.account = sru.account
                left join sw_group g on g.group_id = srg.group_id
                left join sw_web w on w.web_route = srw.web_route
                left join sw_container c on c.container_name = src.container_name and c.web_route = src.web_route and c.web_route = srw.web_route
                left join sw_roleinterface sri on sri.role_id = r.role_id
                left join sw_interface i on sri.api_url = i.api_url
		"""
    # logging.info(sql_select_data)
    res_role_info = mp.fetch_all(sql_select_template,)

    # 返回字典
    data_res = defaultdict(dict)
    for r in res_role_info:
        # data_res[role_info["role_id"]] = role_info
        role_id = r["role_id"]
        role_desc = r["role_desc"]
        date_create = r["date_create"]
        date_update = r["date_update"]
        account = r["account"]
        displayname = r["displayname"]
        group_id = r["group_id"]
        group_desc = r["group_desc"]
        web_route = r["web_route"]
        web_name = r["web_name"]
        web_desc = r["web_desc"]
        container_name = r["container_name"]
        container_desc = r["container_desc"]
        api_url = r["api_url"]
        api_endpoint = r["api_endpoint"]

        # 拼合角色本身的信息
        data_res[role_id]["role_id"] = role_id
        data_res[role_id]["role_desc"] = role_desc
        data_res[role_id]["date_create"] = date_create
        data_res[role_id]["date_update"] = date_update

        # 拼合用户信息
        if "users" not in data_res[role_id]:
            data_res[role_id]["users"] = []
        # 这个if是为了防止列表里有个null值
        if account:
            user_info = {"account": account, "displayname": displayname}
            if user_info not in data_res[role_id]["users"]:
                data_res[role_id]["users"].append(user_info)

        # 拼合组信息
        if "groups" not in data_res[role_id]:
            data_res[role_id]["groups"] = []
        if group_id:
            user_info = {"group_id": group_id, "group_desc": group_desc}
            if user_info not in data_res[role_id]["groups"]:
                data_res[role_id]["groups"].append(user_info)

        # 拼合页面信息
        if "webs" not in data_res[role_id]:
            data_res[role_id]["webs"] = []
        if web_route:
            web_info = {"web_route": web_route, "web_name": web_name, "web_desc": web_desc,}
            if web_info not in data_res[role_id]["webs"]:
                data_res[role_id]["webs"].append(web_info)

        # 拼合菜单块信息
        if "containers" not in data_res[role_id]:
            data_res[role_id]["containers"] = []
        if web_route and container_name:
            user_info = {"web_route": web_route, "web_name": web_name, "container_name": container_name, "container_desc": container_desc}
            if user_info not in data_res[role_id]["containers"]:
                data_res[role_id]["containers"].append(user_info)

        # 拼合后端接口信息
        if "apis" not in data_res[role_id]:
            data_res[role_id]["apis"] = []
        if api_url:
            user_info = {"api_url": api_url, "api_endpoint": api_endpoint}
            if user_info not in data_res[role_id]["apis"]:
                data_res[role_id]["apis"].append(user_info)

    return data_res


def get_dict_new(data_req):
    """
    获取字典形式的所有role及其关联信息 (不使用left join, 效率较高)
    :param data_req:
    :return:
    """

    mp = MysqlPool()

    sw_role = mp.fetch_all("select * from sw_role")
    sw_roleuser = mp.fetch_all("select * from sw_roleuser")
    sw_rolegroup = mp.fetch_all("select * from sw_rolegroup")
    sw_roleweb = mp.fetch_all("select * from sw_roleweb")
    sw_rolecontainer = mp.fetch_all("select * from sw_rolecontainer")
    sw_roleinterface = mp.fetch_all("select * from sw_roleinterface")
    sw_user = mp.fetch_all("select * from sw_user")
    sw_group = mp.fetch_all("select * from sw_group")
    sw_web = mp.fetch_all("select * from sw_web")
    sw_container = mp.fetch_all("select * from sw_container")
    sw_interface = mp.fetch_all("select * from sw_interface")

    data_res = {}
    for r in sw_role:
        role_id = r["role_id"]
        role_desc = r["role_desc"]
        date_create = r["date_create"]
        date_update = r["date_update"]

        # 组合用户
        list_account = [i['account'] for i in sw_roleuser if i["role_id"] == role_id]
        list_user_info = [{"account": i['account'], "displayname": i['displayname']} for i in sw_user if
                          i['account'] in list_account]

        # 组合用户组
        list_group_id = [i['group_id'] for i in sw_rolegroup if i["role_id"] == role_id]
        list_group_info = [{"group_id": i['group_id'], "group_desc": i['group_desc']} for i in sw_group if
                           i['group_id'] in list_group_id]

        # 组合web
        list_route = [i['web_route'] for i in sw_roleweb if i["role_id"] == role_id]
        list_web_info = [
            {
                "web_route": i['web_route'],
                "web_name": i['web_name'],
                "web_desc": i['web_desc']
            }
            for i in sw_web if i['web_route'] in list_route
        ]

        # 组合container
        list_container = [
            {"container_name": i['container_name'], "web_route": i['web_route']}
            for i in sw_rolecontainer if i["role_id"] == role_id
        ]
        list_container_info = [
            {
                "container_desc": i['container_desc'],
                "container_name": i['container_name'],
                "web_name": [ii["web_name"] for ii in sw_web if ii['web_route'] == i['web_route']][0],
                "web_route": i['web_route']
            }
            for i in sw_container if
            {"container_name": i['container_name'], "web_route": i['web_route']} in list_container
        ]

        # 后端api
        list_api = [i['api_url'] for i in sw_roleinterface if i["role_id"] == role_id]
        list_api_info = [
            {
                "api_url": i['api_url'],
                "api_endpoint": i['api_endpoint'],
            }
            for i in sw_interface if i['api_url'] in list_api
        ]

        # 拼合所有数据
        data_res[role_id] = {
            "apis": list_api_info,
            "containers": list_container_info,
            "date_create": date_create,
            "date_update": date_update,
            "groups": list_group_info,
            "role_desc": role_desc,
            "role_id": role_id,
            "users": list_user_info,
            "webs": list_web_info
        }

    return data_res



def create_role(data_req):
    """
    创建一个角色
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        role_id = data_req["role_id"]
        role_desc = data_req["role_desc"]
        groups_input = data_req["groups"]
        users_input = data_req["users"]
        apis_input = data_req["apis"]
        webs_input = data_req["webs"]
        # containers_input列表中的元素是字典, 应包含web_route和container_name
        containers_input = data_req["containers"]
        if not isinstance(groups_input, list):
            return res_format(err="groups格式错误", code=10002)
        if not isinstance(users_input, list):
            return res_format(err="users格式错误", code=10002)
        if not isinstance(apis_input, list):
            return res_format(err="apis格式错误", code=10002)
        if not isinstance(webs_input, list):
            return res_format(err="webs格式错误", code=10002)
        if not isinstance(containers_input, list):
            return res_format(err="containers格式错误", code=10002)
        # 将containers_input组合为字典, 方便校验和入库
        containers_input_dict = defaultdict(list)
        for m in containers_input:
            containers_input_dict[m['web_route']].append(m["container_name"])

    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 以用户显示名的标准校验角色名
    rule_displayname(role_id)
    # 校验描述信息的长度
    rule_desc(role_desc)

    # 初始化数据库
    mp = MysqlPool()
    sql_list = []
    sql_insert_role_data = {}

    # 获取所有角色名
    sql_select_role = "select role_id from sw_role where role_id = %(role_id)s;"
    res_db_role = mp.fetch_one(sql_select_role, {"role_id": role_id})
    # 如果有, 说明已存在, 报错
    if res_db_role:
        logging.error(f"角色'{role_id}'已存在")
        return res_format(err=f"角色'{role_id}'已存在", code=10002)

    # 获取所有组名
    if groups_input:
        sql_select_group = "select group_id from sw_group"
        res_db_groups = mp.fetch_all(sql_select_group)
        list_group_db = [i["group_id"] for i in res_db_groups]
        for i in groups_input:
            if not i:
                return res_format(err=f"组名不能为空", code=10002)
            if i not in list_group_db:
                logging.error(f"没有'{i}'这个组名")
                return res_format(err=f"没有'{i}'这个组名", code=10002)

    # 对比web页面是否存在
    if webs_input:
        sql_select_web = "select web_route from sw_web"
        res_db_webs = mp.fetch_all(sql_select_web)
        list_web_db = [i["web_route"] for i in res_db_webs]
        for i in webs_input:
            if not i:
                return res_format(err=f"页面路径不能为空", code=10002)
            if i not in list_web_db:
                logging.error(f"没有'{i}'这个页面路径")
                return res_format(err=f"没有'{i}'这个页面路径", code=10002)

    # 对比菜单和展示块是否存在
    if containers_input:
        # 组合sql
        values_where_container = []
        sql_select_container_data = {}
        nm = 1
        for k, v in containers_input_dict.items():
            if not k or not v:
                return res_format(err=f"菜单名或块名不能为空", code=10002)
            values_where_container.append(f"(web_route = %(web_route_{nm})s and container_name in %(container_list_{nm})s)")
            sql_select_container_data[f"web_route_{nm}"] = k
            sql_select_container_data[f"container_list_{nm}"] = v
            nm += 1
        sql_select_container_tem = f"select count(1) as num_count from sw_container where {' or '.join(values_where_container)}"
        res_db_containers = mp.fetch_one(sql_select_container_tem, sql_select_container_data)
        # 对比返回的count行数和传入的行数
        if res_db_containers["num_count"] != len(containers_input):
            logging.error(f"菜单和块列表中混入了我不认识的东西")
            return res_format(err=f"菜单和块列表中混入了我不认识的东西", code=10002)

    # 获取所有用户名
    if users_input:
        sql_select_account = "select account from sw_user;"
        res_db_account = mp.fetch_all(sql_select_account)
        list_account_db = [i["account"] for i in res_db_account]
        for i in users_input:
            if not i:
                return res_format(err=f"用户名不能为空", code=10002)
            if i not in list_account_db:
                return res_format(err=f"没有'{i}'这个账号", code=10002)

    # 获取所有后端接口
    if users_input:
        sql_select_api = "select api_url from sw_interface;"
        res_db_api = mp.fetch_all(sql_select_api)
        list_api_db = [i["api_url"] for i in res_db_api]
        for i in apis_input:
            if not i:
                return res_format(err=f"接口名不能为空", code=10002)
            if i not in list_api_db:
                return res_format(err=f"没有'{i}'这个后端接口", code=10002)

    # 经过了组织的考验, 新建这个角色
    sql_insert_role_tem = """
        insert into sw_role (role_id, role_desc, date_create, date_update)
        values (%(role_id)s, %(role_desc)s, now(), now());
    """

    sql_insert_role_data["role_id"] = role_id
    sql_insert_role_data["role_desc"] = role_desc
    sql_list.append(sql_insert_role_tem)

    # 删除现有的组关联
    sql_delete_groups = "delete from sw_rolegroup where role_id = %(role_id)s;"
    sql_list.append(sql_delete_groups)
    # 一并新建组的关联关系
    if groups_input:
        ng = 0
        sql_insert_group_tem_line_list = []
        for group_id in groups_input:
            sql_insert_group_tem_line_list.append(f"""
                    (%(group_id_{ng})s, %(role_id)s)""")
            sql_insert_role_data[f"group_id_{ng}"] = group_id
            ng += 1

        sql_insert_role_tem_line_str = ',\n\t\t\t'.join(sql_insert_group_tem_line_list)
        sql_insert_role_tem = f"""
            insert into sw_rolegroup (group_id, role_id) values
                {sql_insert_role_tem_line_str};
        """
        sql_list.append(sql_insert_role_tem)

    # 删除现有的用户关联
    sql_delete_users = "delete from sw_roleuser where role_id = %(role_id)s;"
    sql_list.append(sql_delete_users)
    # 一并新建用户的关联关系
    if users_input:
        nu = 0
        sql_insert_user_tem_line_list = []
        for account in users_input:
            sql_insert_user_tem_line_list.append(f"""
                    (%(role_id)s, %(account_{nu})s)""")
            sql_insert_role_data[f"account_{nu}"] = account
            nu += 1

        sql_insert_user_tem_line_str = ',\n\t\t\t'.join(sql_insert_user_tem_line_list)
        sql_insert_user_tem = f"""
            insert into sw_roleuser (role_id, account) values
                {sql_insert_user_tem_line_str};
        """
        sql_list.append(sql_insert_user_tem)

    # 删除现有的web页面关联
    sql_delete_webs = "delete from sw_roleweb where role_id = %(role_id)s;"
    sql_list.append(sql_delete_webs)
    # 创建角色与web页面关联
    if webs_input:
        nw = 0
        sql_insert_web_tem_line_list = []
        for web in webs_input:
            sql_insert_web_tem_line_list.append(f"""
                            (%(role_id)s, %(web_web_route_{nw})s, now())""")
            sql_insert_role_data[f"web_web_route_{nw}"] = web
            nw += 1

        sql_insert_web_tem_line_str = ',\n\t\t\t'.join(sql_insert_web_tem_line_list)
        sql_insert_web_tem = f"""
                    insert into sw_roleweb (role_id, web_route, date_create) values
                        {sql_insert_web_tem_line_str};
                """
        sql_list.append(sql_insert_web_tem)

    # 删除现有的菜单块关联 sw_rolecontainer
    sql_delete_containers = "delete from sw_rolecontainer where role_id = %(role_id)s;"
    sql_list.append(sql_delete_containers)
    # 创建菜单块关系
    if containers_input:
        nm = 0
        sql_insert_container_tem_line_list = []
        for container in containers_input:
            # 如果没有对页面授予基础查看权限, 则跳过此页面的所有菜单块权限
            if container["web_route"] not in webs_input:
                continue
            sql_insert_container_tem_line_list.append(f"""
                            (%(role_id)s, %(container_web_route_{nm})s, %(container_name_{nm})s, now())""")
            sql_insert_role_data[f"container_web_route_{nm}"] = container["web_route"]
            sql_insert_role_data[f"container_name_{nm}"] = container["container_name"]
            nm += 1

        sql_insert_container_tem_line_str = ',\n\t\t\t'.join(sql_insert_container_tem_line_list)
        sql_insert_container_tem = f"""
                    insert into sw_rolecontainer (role_id,web_route,container_name,date_create) values
                        {sql_insert_container_tem_line_str};
                """
        sql_list.append(sql_insert_container_tem)

    # 删除现有的后端接口关联
    sql_delete_apis = "delete from sw_roleinterface where role_id = %(role_id)s;"
    sql_list.append(sql_delete_apis)
    # 创建角色与后端接口关联
    if apis_input:
        na = 0
        sql_insert_api_tem_line_list = []
        for api in apis_input:
            sql_insert_api_tem_line_list.append(f"""
                            (%(role_id)s, %(api_url_{na})s, now())""")
            sql_insert_role_data[f"api_url_{na}"] = api
            na += 1

        sql_insert_api_tem_line_str = ',\n\t\t\t'.join(sql_insert_api_tem_line_list)
        sql_insert_api_tem = f"""
                    insert into sw_roleinterface (role_id, api_url, date_create) values
                        {sql_insert_api_tem_line_str};
                """
        sql_list.append(sql_insert_api_tem)

    # for i in sql_list:
    #     print(i)

    # 执行
    mp.transaction(sql_list, sql_insert_role_data, is_list=True)
    logging.info(f"成功新建角色: {role_id}, 包含组: {groups_input}, 包含用户: {users_input}, 包含菜单块: {containers_input}, 包含后端接口: {apis_input}, 描述: {role_desc}")

    return {"ok": "ok"}


def update_role(data_req):
    """
    创建一个角色
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        role_id = data_req["role_id"]
        role_desc = data_req["role_desc"]
        groups_input = data_req["groups"]
        users_input = data_req["users"]
        apis_input = data_req["apis"]
        webs_input = data_req["webs"]
        # containers_input列表中的元素是字典, 应包含web_route和container_name
        containers_input = data_req["containers"]
        if not isinstance(groups_input, list):
            return res_format(err="groups格式错误", code=10002)
        if not isinstance(users_input, list):
            return res_format(err="users格式错误", code=10002)
        if not isinstance(apis_input, list):
            return res_format(err="apis格式错误", code=10002)
        if not isinstance(webs_input, list):
            return res_format(err="webs格式错误", code=10002)
        if not isinstance(containers_input, list):
            return res_format(err="containers格式错误", code=10002)
        # 将containers_input组合为字典, 方便校验和入库
        containers_input_dict = defaultdict(list)
        for c in containers_input:
            containers_input_dict[c['web_route']].append(c["container_name"])

    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 以用户显示名的标准校验角色名
    rule_displayname(role_id)
    # 校验描述信息的长度
    rule_desc(role_desc)

    # 初始化数据库
    mp = MysqlPool()
    sql_list = []
    sql_update_role_data = {}

    # 获取所有角色名
    sql_select_role = "select role_id from sw_role where role_id = %(role_id)s;"
    res_db_role = mp.fetch_one(sql_select_role, {"role_id": role_id})
    # 如果没有, 报错
    if not res_db_role:
        logging.error(f"角色'{role_id}'不存在")
        return res_format(err=f"角色'{role_id}'不存在", code=10002)

    # 获取所有组名
    if groups_input:
        sql_select_group = "select group_id from sw_group"
        res_db_groups = mp.fetch_all(sql_select_group)
        list_group_db = [i["group_id"] for i in res_db_groups]
        for i in groups_input:
            if not i:
                return res_format(err=f"组名不能为空", code=10002)
            if i not in list_group_db:
                logging.error(f"没有'{i}'这个组名")
                return res_format(err=f"没有'{i}'这个组名", code=10002)

    # 对比web页面是否存在
    if webs_input:
        sql_select_web = "select web_route from sw_web"
        res_db_webs = mp.fetch_all(sql_select_web)
        list_web_db = [i["web_route"] for i in res_db_webs]
        for i in webs_input:
            if not i:
                return res_format(err=f"页面路径不能为空", code=10002)
            if i not in list_web_db:
                logging.error(f"没有'{i}'这个页面路径")
                return res_format(err=f"没有'{i}'这个页面路径", code=10002)

    # 对比菜单和展示块是否存在
    if containers_input:
        # 组合sql
        values_where_container = []
        sql_select_container_data = {}
        nm = 1
        for k, v in containers_input_dict.items():
            if not k or not v:
                return res_format(err=f"菜单名或块名不能为空", code=10002)
            values_where_container.append(f"(web_route = %(web_route_{nm})s and container_name in %(container_list_{nm})s)")
            sql_select_container_data[f"web_route_{nm}"] = k
            sql_select_container_data[f"container_list_{nm}"] = v
            nm += 1
        sql_select_container_tem = f"select count(1) as num_count from sw_container where {' or '.join(values_where_container)}"
        res_db_containers = mp.fetch_one(sql_select_container_tem, sql_select_container_data)
        # 对比返回的count行数和传入的行数
        if res_db_containers["num_count"] != len(containers_input):
            logging.error(f"菜单和块列表中混入了我不认识的东西")
            return res_format(err=f"菜单和块列表中混入了我不认识的东西", code=10002)

    # 获取所有用户名
    if users_input:
        sql_select_account = "select account from sw_user;"
        res_db_account = mp.fetch_all(sql_select_account)
        list_account_db = [i["account"] for i in res_db_account]
        for i in users_input:
            if not i:
                return res_format(err=f"用户名不能为空", code=10002)
            if i not in list_account_db:
                return res_format(err=f"没有'{i}'这个账号", code=10002)

    # 获取所有后端接口
    if users_input:
        sql_select_api = "select api_url from sw_interface;"
        res_db_api = mp.fetch_all(sql_select_api)
        list_api_db = [i["api_url"] for i in res_db_api]
        for i in apis_input:
            if not i:
                return res_format(err=f"接口名不能为空", code=10002)
            if i not in list_api_db:
                return res_format(err=f"没有'{i}'这个后端接口", code=10002)

    # 经过了组织的考验, 更新这个角色
    sql_update_role_tem = """
        update sw_role set role_desc = %(role_desc)s, date_update = now() where role_id = %(role_id)s
    """

    sql_update_role_data["role_id"] = role_id
    sql_update_role_data["role_desc"] = role_desc
    sql_list.append(sql_update_role_tem)

    # 删除现有的组关联
    sql_delete_groups = "delete from sw_rolegroup where role_id = %(role_id)s;"
    sql_list.append(sql_delete_groups)
    # 一并新建组的关联关系
    if groups_input:
        ng = 0
        sql_insert_group_tem_line_list = []
        for group_id in groups_input:
            sql_insert_group_tem_line_list.append(f"""
                    (%(group_id_{ng})s, %(role_id)s)""")
            sql_update_role_data[f"group_id_{ng}"] = group_id
            ng += 1

        sql_insert_role_tem_line_str = ',\n\t\t\t'.join(sql_insert_group_tem_line_list)
        sql_insert_role_tem = f"""
            insert into sw_rolegroup (group_id, role_id) values
                {sql_insert_role_tem_line_str};
        """
        sql_list.append(sql_insert_role_tem)

    # 删除现有的用户关联
    sql_delete_users = "delete from sw_roleuser where role_id = %(role_id)s;"
    sql_list.append(sql_delete_users)
    # 一并新建用户的关联关系
    if users_input:
        nu = 0
        sql_insert_user_tem_line_list = []
        for account in users_input:
            sql_insert_user_tem_line_list.append(f"""
                    (%(role_id)s, %(account_{nu})s)""")
            sql_update_role_data[f"account_{nu}"] = account
            nu += 1

        sql_insert_user_tem_line_str = ',\n\t\t\t'.join(sql_insert_user_tem_line_list)
        sql_insert_user_tem = f"""
            insert into sw_roleuser (role_id, account) values
                {sql_insert_user_tem_line_str};
        """
        sql_list.append(sql_insert_user_tem)

    # 删除现有的web页面关联
    sql_delete_webs = "delete from sw_roleweb where role_id = %(role_id)s;"
    sql_list.append(sql_delete_webs)
    # 创建角色与web页面关联
    if webs_input:
        nw = 0
        sql_insert_web_tem_line_list = []
        for web in webs_input:
            sql_insert_web_tem_line_list.append(f"""
                            (%(role_id)s, %(web_web_route_{nw})s, now())""")
            sql_update_role_data[f"web_web_route_{nw}"] = web
            nw += 1

        sql_insert_web_tem_line_str = ',\n\t\t\t'.join(sql_insert_web_tem_line_list)
        sql_insert_web_tem = f"""
                    insert into sw_roleweb (role_id, web_route, date_create) values
                        {sql_insert_web_tem_line_str};
                """
        sql_list.append(sql_insert_web_tem)

    # 删除现有的菜单块关联 sw_rolecontainer
    sql_delete_containers = "delete from sw_rolecontainer where role_id = %(role_id)s;"
    sql_list.append(sql_delete_containers)
    # 创建菜单块关系
    if containers_input:
        nm = 0
        sql_insert_container_tem_line_list = []
        for container in containers_input:
            # 如果没有对页面授予基础查看权限, 则跳过此页面的所有菜单块权限
            if container["web_route"] not in webs_input:
                continue
            sql_insert_container_tem_line_list.append(f"""
                            (%(role_id)s, %(container_web_route_{nm})s, %(container_name_{nm})s, now())""")
            sql_update_role_data[f"container_web_route_{nm}"] = container["web_route"]
            sql_update_role_data[f"container_name_{nm}"] = container["container_name"]
            nm += 1

        sql_insert_container_tem_line_str = ',\n\t\t\t'.join(sql_insert_container_tem_line_list)
        sql_insert_container_tem = f"""
                    insert into sw_rolecontainer (role_id,web_route,container_name,date_create) values
                        {sql_insert_container_tem_line_str};
                """
        sql_list.append(sql_insert_container_tem)

    # 删除现有的后端接口关联
    sql_delete_apis = "delete from sw_roleinterface where role_id = %(role_id)s;"
    sql_list.append(sql_delete_apis)
    # 创建角色与后端接口关联
    if apis_input:
        na = 0
        sql_insert_api_tem_line_list = []
        for api in apis_input:
            sql_insert_api_tem_line_list.append(f"""
                            (%(role_id)s, %(api_url_{na})s, now())""")
            sql_update_role_data[f"api_url_{na}"] = api
            na += 1

        sql_insert_api_tem_line_str = ',\n\t\t\t'.join(sql_insert_api_tem_line_list)
        sql_insert_api_tem = f"""
                    insert into sw_roleinterface (role_id, api_url, date_create) values
                        {sql_insert_api_tem_line_str};
                """
        sql_list.append(sql_insert_api_tem)

    ms = manual_substitute(sql_list, sql_update_role_data)
    for i in ms:
        print(i)

    # 执行
    mp.transaction(sql_list, sql_update_role_data, is_list=True)
    logging.info(f"成功更新角色: {role_id}, 包含组: {groups_input}, 包含用户: {users_input}, 包含菜单块: {containers_input}, 包含后端接口: {apis_input}, 描述: {role_desc}")

    return {"ok": "ok"}


def delete_role(data_req):
    """
    创建一个角色
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        role_id = data_req["role_id"]

    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 以用户显示名的标准校验角色名
    rule_displayname(role_id)

    # 初始化数据库
    mp = MysqlPool()
    sql_list = []
    sql_delete_role_data = {}

    # 经过了组织的考验, 删除这个角色
    sql_update_role_tem = """
        delete from sw_role where role_id = %(role_id)s
    """
    sql_delete_role_data["role_id"] = role_id
    sql_list.append(sql_update_role_tem)

    # 删除现有的组关联
    sql_delete_groups = "delete from sw_rolegroup where role_id = %(role_id)s;"
    sql_list.append(sql_delete_groups)

    # 删除现有的用户关联
    sql_delete_users = "delete from sw_roleuser where role_id = %(role_id)s;"
    sql_list.append(sql_delete_users)

    # 删除现有的web页面关联
    sql_delete_webs = "delete from sw_roleweb where role_id = %(role_id)s;"
    sql_list.append(sql_delete_webs)

    # 删除现有的菜单块关联 sw_rolecontainer
    sql_delete_containers = "delete from sw_rolecontainer where role_id = %(role_id)s;"
    sql_list.append(sql_delete_containers)
    #
    # 删除现有的后端接口关联
    sql_delete_apis = "delete from sw_roleinterface where role_id = %(role_id)s;"
    sql_list.append(sql_delete_apis)

    # 执行
    mp.transaction(sql_list, sql_delete_role_data, is_list=True)
    logging.info(f"成功删除角色: {role_id}")

    return {"ok": "ok"}