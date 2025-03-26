import logging
from ..db.db_select import kvdb
import re
import datetime
from ..db.exec_ql import MysqlPool
from collections import defaultdict


def build_payload(account):
    """
    生成用户的payload信息
    :param account:
    :return:
    """

    # 查询基本信息
    sql_select_info_tem = """
        select 
            u.*,
            GROUP_CONCAT(DISTINCT ug.group_id ORDER BY ug.group_id SEPARATOR ',') AS groups,
            GROUP_CONCAT(DISTINCT ru.role_id ORDER BY ru.role_id SEPARATOR ',') AS roles
        from 
            sw_user u
            left join sw_roleuser ru on u.account = ru.account
            left join sw_usergroup ug on u.account = ug.account
        where 
            u.account = %(user_account)s
        GROUP BY u.account;
    """
    sql_select_info_data = {
        "user_account": account
    }

    mp = MysqlPool()
    res_user_info = mp.fetch_one(sql_select_info_tem, sql_select_info_data)

    if res_user_info:
        # res_user_info = ms.fetch_all(sql_select_template, sql_select_data)[0]

        # 判断用户是否被冻结
        status =  res_user_info["status"]
        if status != 'on':
            raise ZeroDivisionError("勇者也需要休息, 先别工作了吧")

        # 转化时间格式
        str_date_latest_login = res_user_info["date_latest_login"].timestamp()

        # 生成用户的简要信息, 用于jwt的payload

        payload = {
            "id": res_user_info["user_id"],
            "account": res_user_info["account"],
            "displayname": res_user_info["displayname"],
            "rank": res_user_info["rank"],
            "role_id": re.split(',', res_user_info["roles"] or "") if res_user_info["roles"] else [],
            "groups": re.split(',', res_user_info["groups"] or "") if res_user_info["groups"] else [],
            "email": res_user_info["email"],
            "tel": res_user_info["tel"],
            "befrom": res_user_info["befrom"],
            "date_latest_login": str_date_latest_login,
        }

        # 查询该用户涉及角色的所有后端权限
        apis = get_permissions_api(payload)
        payload["apis"] = apis

    else:
        raise ZeroDivisionError("用户名或密码不对")

    return payload



def get_permissions_all(payload):
    """
    获取指定用户的所有权限信息
    :param payload: 用户信息, 是一个最少包含roles和groups列表的字典
    :return:
    """
    mp = MysqlPool()

    webs = []
    containers = defaultdict(list)
    apis = []

    # 整合此用户的角色权限及其对应组的角色权限
    groups = payload["groups"]
    roles = payload["role_id"]
    if groups or roles:
        list_where = []
        if groups:
            list_where.append('r.role_id in (select role_id from sw_rolegroup where group_id in %(groups)s)')
        if roles:
            list_where.append('r.role_id in %(role_user)s')
        sql_select_role_tem = f"""
            select srw.web_route,src.container_name, sri.api_url  from sw_role r
            left join sw_roleweb srw on srw.role_id = r.role_id
            left join sw_rolecontainer src on src.role_id = r.role_id and srw.web_route = src.web_route
            left join sw_roleinterface sri on sri.role_id = r.role_id
            where 
                {' or '.join(list_where)}
        """

        sql_select_role_data = {
            "role_user": roles,
            "groups": groups
        }
        # 查询此用户所有的权限信息
        res_db_role = mp.fetch_all(sql_select_role_tem, sql_select_role_data)



        for r in res_db_role:
            web_route = r['web_route']
            container_name = r['container_name']
            api_url = r['api_url']
            # 整合页面信息
            if web_route and web_route not in webs:
                webs.append(web_route)
            # 整合菜单块信息
            if container_name and container_name not in containers[web_route]:
                containers[web_route].append(container_name)
            # 整合后端api
            if api_url and api_url not in apis:
                apis.append(api_url)

    data_res = {
        "webs": webs,
        "containers": containers,
        "apis": apis,
    }

    return data_res


def get_permissions_meuns(payload):
    """
    仅获取指定用户的所有前端权限
    :param payload: 用户信息, 是一个最少包含roles和groups列表的字典
    :return:
    """
    mp = MysqlPool()
    data_res = {}

    # 整合此用户的角色权限及其对应组的角色权限
    groups = payload["groups"]
    roles = payload["role_id"]
    if groups or roles:
        list_where = []
        if groups:
            list_where.append('r.role_id in (select role_id from sw_rolegroup where group_id in %(groups)s)')
        if roles:
            list_where.append('r.role_id in %(role_user)s')
        sql_select_role_tem = f"""
            select srw.web_route,src.container_name from sw_role r
            left join sw_roleweb srw on srw.role_id = r.role_id
            -- left join sw_web w on srw.web_route = w.web_route
            left join sw_rolecontainer src on src.role_id = r.role_id and srw.web_route = src.web_route
            where 
                srw.web_route is not null
                and ({' or '.join(list_where)})
        """
        sql_select_role_data = {
            "role_user": roles,
            "groups": groups
        }
        # 查询此用户所有的权限信息
        res_db_role = mp.fetch_all(sql_select_role_tem, sql_select_role_data)

        for r in res_db_role:
            web_route = r['web_route']
            container_name = r['container_name']

            # 整合页面信息
            if web_route and web_route not in data_res:
                data_res[web_route] = []
            # 整合菜单块信息
            if container_name and container_name not in data_res[web_route]:
                data_res[web_route].append(container_name)

    return data_res


def get_permissions_api(payload):
    """
    仅获取指定用户的后端接口权限信息
    :param payload: 用户信息, 是一个最少包含roles和groups列表的字典
    :return:
    """
    mp = MysqlPool()
    apis = []

    # 整合此用户的角色权限及其对应组的角色权限
    groups = payload["groups"]
    roles = payload["role_id"]
    if groups or roles:
        list_where = []
        if groups:
            list_where.append('r.role_id in (select role_id from sw_rolegroup where group_id in %(groups)s)')
        if roles:
            list_where.append('r.role_id in %(role_user)s')
        sql_select_role_tem = f"""
            select sri.api_url  from sw_role r
            left join sw_roleinterface sri on sri.role_id = r.role_id
            where 
                {' or '.join(list_where)}
        """
        sql_select_role_data = {
            "role_user": roles,
            "groups": groups
        }
        # 查询此用户所有的权限信息
        res_db_role = mp.fetch_all(sql_select_role_tem, sql_select_role_data)

        apis = [i["api_url"] for i in res_db_role if i["api_url"]]

    return apis


def get_photo_base64(account):
    """
    获取指定用户的头像
    :param account: 用户名
    :return:
    """
    mp = MysqlPool()
    sql_select_photo_tem = """
                select p.photo_base64 from sw_user u
                left join sw_photo p on u.photo_id = p.photo_id
                where u.account = %(account)s;
            """
    sql_select_photo_data = {"account": account}
    res_db_photo_base64 = mp.fetch_one(sql_select_photo_tem, sql_select_photo_data)

    if res_db_photo_base64["photo_base64"]:
        photo_base64 = res_db_photo_base64["photo_base64"]
    else:
        photo_base64 = ""

    return photo_base64

