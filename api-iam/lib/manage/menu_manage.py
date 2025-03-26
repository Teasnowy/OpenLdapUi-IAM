from ..db.db_select import kvdb
from ..data_format import res_format, str_to_md5
from ..db.exec_ql import MysqlPool
import logging
from collections import defaultdict
from ..user.check import rule_displayname, rule_desc, rule_url


def get_dict(data_req):
    """
    获取数据库中目前的所有前端展示块
    :param data_req: 任意数据
    :return:
    """
    # 初始化数据库连接池
    mp = MysqlPool()
    # 加密前端此时传来的密码

    # 对比数据库中的加密字符串
    sql_select_template = """
        select 
            w.web_id,
            w.web_route,
            w.web_name,
            w.web_desc,
            w.date_create AS web_date_create,
            w.date_update AS web_date_update,
            c.container_id,
            c.container_name,
            c.container_desc,
            c.date_create AS container_date_create,
            c.date_update AS container_date_update 
        from 
            sw_web w 
            left join sw_container c on w.web_route = c.web_route
        ;
    """
    # logging.info(sql_select_data)
    res_container_info = mp.fetch_all(sql_select_template,)

    # 返回字典
    data_res = defaultdict(dict)
    for container_info in res_container_info:
        web_route = container_info["web_route"]
        container_name = container_info["container_name"]
        data_res[web_route]["web_route"] = web_route
        data_res[web_route]["web_name"] = container_info["web_name"]
        data_res[web_route]["web_id"] = container_info["web_id"]
        data_res[web_route]["web_desc"] = container_info["web_desc"]
        data_res[web_route]["date_create"] = container_info["web_date_create"]
        data_res[web_route]["date_update"] = container_info["web_date_update"]
        # print(data_res)
        if "container_list" not in data_res[web_route]:
            data_res[web_route]["container_list"] = {}
        # 这个web下面可能没有创建展示块
        if container_name:
            data_res[web_route]["container_list"][container_name] = {
                "container_name": container_name,
                "container_desc": container_info["container_desc"],
                "date_create": container_info["container_date_create"],
                "date_update": container_info["container_date_update"],
            }

    return data_res


def create_web(data_req):
    """
    创建一个web页面
    :param data_req:
    :return:
    """
    try:
        web_route = data_req['web_route']
        web_name = data_req['web_name']
        web_desc = data_req['web_desc']
    except Exception as el:
        logging.error(f"报文格式错误: {data_req}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 校验数据格式
    rule_displayname(web_name)
    rule_url(web_route)

    # 初始化数据库
    mp = MysqlPool()

    # 看一下这个web是不是已经被创建了
    data_db = mp.fetch_all(
        "select web_route from sw_web where web_route = %(web_route)s", {"web_route": web_route}
    )
    # logging.info(f"尝试查询web是否已存在: {data_db}")
    if data_db:
        return res_format(err=f"页面{web_route}已存在, 重复定义")

    # 拼装语句
    sql_insert_tem = """
        insert into sw_web (web_id,web_route,web_name,web_desc,date_create,date_update) 
        values (null, %(web_route)s, %(web_name)s, %(web_desc)s, now(), now())
    """
    sql_data = {
        "web_name": web_name,
        "web_route": web_route,
        "web_desc": web_desc,
    }

    # 执行创建
    mp.transaction(sql_insert_tem, sql_data)

    return {"ok": "ok"}


def update_web(data_req):
    """
    更新一个web的信息
    :param data_req:
    :return:
    """
    try:
        web_route = data_req['web_route']
        web_name = data_req['web_name']
        web_desc = data_req['web_desc']
    except Exception as el:
        logging.error(f"报文格式错误: {data_req}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 校验数据格式
    rule_displayname(web_name)
    rule_url(web_route)

    # 初始化数据库
    mp = MysqlPool()

    # 看一下这个web是不是已经被创建了
    data_db = mp.fetch_all(
        "select web_route from sw_web where web_route = %(web_route)s", {"web_route": web_route}
    )
    if not data_db:
        return res_format(err=f"页面{web_route}不存在")

    # 拼装语句
    sql_update_tem = """
        update sw_web set web_name =  %(web_name)s, web_desc = %(web_desc)s, date_update = now()
        where web_route = %(web_route)s
    """
    sql_data = {
        "web_name": web_name,
        "web_route": web_route,
        "web_desc": web_desc,
    }

    # 执行创建
    mp.transaction(sql_update_tem, sql_data)

    return {"ok": "ok"}


def delete_web(data_req):
    """
    删除一个web以及其所属的所有container
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        web_route = data_req['web_route']
    except Exception as el:
        logging.error(f"报文格式错误: {data_req}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    rule_url(web_route)

    mp = MysqlPool()

    sql_list = []

    # 拼装
    sql_delete_tem_web = "delete from sw_web where web_route = %(web_route)s"
    sql_list.append(sql_delete_tem_web)
    # 删除该页面下所属的按钮
    sql_delete_tem_container = "delete from sw_container where web_route = %(web_route)s"
    sql_list.append(sql_delete_tem_container)

    mp.transaction(sql_list, {"web_route": web_route}, is_list=True)

    return {"ok": "ok"}


def create_containers(data_req):
    """
    批量创建指定web页面的多个前端展示块
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        web_route = data_req['web_route']
        container_list = data_req['container_list']
        for c in container_list:
            if sorted(c.keys()) != sorted(
                    ["container_name", "container_desc"]):
                # raise ZeroDivisionError(f"某待注册用户的传参和预期不符: {u}")
                return res_format(err=f"此展示块的属性列表不对: {c}")
    except Exception as el:
        logging.error(f"报文格式错误: {data_req}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 校验数据
    rule_url(web_route)
    # 检测是否有重复container_name, 获取用户传入的container_name列表
    input_container_name_list = [v["container_name"] for v in container_list]
    if len(input_container_name_list) > len(set(input_container_name_list)):
        return res_format(err=f"提交的展示块名称有重复")

    # sql数据
    sql_data = {"web_route": web_route}
    # 拼装SQL
    sql_insert_values = []
    n = 1
    for i in container_list:
        # 校验数据
        rule_displayname(i["container_name"])
        rule_desc(i["container_desc"])

        sql_insert_values.append(f"(null, %(web_route)s, %(container_name_{n})s, %(container_desc_{n})s, now(), now())")
        sql_data[f"container_name_{n}"] = i["container_name"]
        sql_data[f"container_desc_{n}"] = i["container_desc"]
        n += 1

    sql_insert_tem = f"""
        insert into sw_container (container_id,web_route,container_name,container_desc,date_create,date_update)
        values {','.join(sql_insert_values)};
    """

    mp = MysqlPool()

    # 数据库中取出当前的数据, 用于校验是否已存在
    sql_select_tem = """
        select c.container_name from sw_web w left join sw_container c on w.web_route = c.web_route
        where w.web_route = %(web_route)s;
    """
    data_db = mp.fetch_all(sql_select_tem, {"web_route": web_route})
    if not data_db:
        return res_format(err=f"页面{web_route}不存在")
    db_container_name_list = [v["container_name"] for v in data_db]

    # 对比重复
    union_tmp = list(set(input_container_name_list) & set(db_container_name_list))
    if union_tmp:
        return res_format(err=f"检测到{union_tmp}已定义于{web_route}中")

    # print(sql_insert_tem)
    # 执行创建
    mp.transaction(sql_insert_tem, sql_data)

    return {"ok": "ok"}


def update_container(data_req):
    """
    更新指定web页面的单个前端展示块
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        web_route = data_req['web_route']
        container_name = data_req['container_name']
        container_desc = data_req['container_desc']
    except Exception as el:
        logging.error(f"报文格式错误: {data_req}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    rule_url(web_route)
    rule_displayname(container_name)
    rule_desc(container_desc)

    # sql数据
    sql_data = {
        "web_route": web_route,
        "container_name": container_name,
        "container_desc": container_desc
    }
    # 拼装SQL
    sql_update_tem = """
        update sw_container set container_desc = %(container_desc)s, date_update = now()
        where web_route = %(web_route)s and container_name = %(container_name)s;
    """

    mp = MysqlPool()

    # 数据库中取出当前的数据, 用于校验是否已存在
    sql_select_tem = """
        select container_name from sw_container
        where web_route = %(web_route)s and container_name = %(container_name)s;
    """
    data_db = mp.fetch_all(sql_select_tem, sql_data)
    if not data_db:
        return res_format(err=f"页面{web_route}的{container_name}不存在")

    # 执行更新
    mp.transaction(sql_update_tem, sql_data)

    return {"ok": "ok"}


def delete_container(data_req):
    """
    删除指定的多个展示块
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        web_route = data_req['web_route']
        list_container_name = data_req['list_container_name']
    except Exception as el:
        logging.error(f"报文格式错误: {data_req}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 检查格式
    rule_url(web_route)
    for container_name in list_container_name:
        rule_displayname(container_name)

    # 组合语句
    sql_delete_tem = """
        delete from sw_container 
        where web_route = %(web_route)s and container_name in %(list_container_name)s
    """
    sql_delete_data = {
        "web_route": web_route,
        "list_container_name": list_container_name,
    }

    mp = MysqlPool()

    # 执行创建
    mp.transaction(sql_delete_tem, sql_delete_data)

    return {"ok": "ok"}
