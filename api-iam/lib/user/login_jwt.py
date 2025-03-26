import jwt
import datetime
import logging
import re
import time
import json
import base64
from flask import jsonify, request
from ..db.db_select import kvdb
from ..db.exec_ql import MysqlPool
from .user_data_build import build_payload
from collections import defaultdict


def create(user_info: dict) -> str:
    """
    创建jwt的函数
    :param user_info: 用户信息, 通常包含用户名|id|权限信息等等
    :return: str
    """

    # 获取注册相关配置
    kv = kvdb()
    cf = kv.read()['jwt']
    # 获取加密密钥的前缀
    secret_key_prefix = cf["secret_key_prefix"]
    # 获取过期时长
    exp_step = cf["exp_step"]

    # 提取用户名
    user_account = user_info['account']
    # 定义密钥为加用户名
    secret_key = f"{secret_key_prefix}{user_account}"

    # 定义过期时间
    exp = datetime.datetime.now() + datetime.timedelta(seconds=exp_step)
    exp_stamp = int(exp.timestamp())
    exp_str = exp.strftime('%Y-%m-%d %H:%M:%S')
    user_info["exp"] = exp_stamp

    res_jwt = jwt.encode(user_info, secret_key, algorithm='HS256')
    # 上传至内存键值数据库
    k_jwt = f"jwt_{user_account}"
    kv.set(v=res_jwt, k=k_jwt, expire=exp_step)

    logging.info(f"用户{user_account}生成jwt: {res_jwt}, 预定过期时间: {exp_str}")
    return res_jwt


def check(jwt_str: str, user_account: str, force=False, only_check=False) -> (bool, bool, str, dict) :
    """
    检查jwt有效性并续签的函数
    :param jwt_str: jwt字符串
    :param user_account: 用户名
    :param force: 是否强制更新jwt
    :param only_check: 是否仅检查并返回此jwt的信息
    :return:
    """

    # 初始化数据库连接池
    ms = MysqlPool()

    # 表示是否续签的布尔值
    is_renew = False
    # 表示是否已经过期
    is_exp = True
    # 记录新的密钥
    jwt_renew = ""
    # 记录用户信息
    decoded_payload = ""

    # 获取注册相关配置
    cf = kvdb().read()['jwt']
    # 获取加密密钥的前缀
    secret_key_prefix = cf["secret_key_prefix"]
    # 获取续签阈值
    exp_renew = cf["exp_renew"]
    # 获取极限登录时长
    exp_max = cf["exp_max"]
    # 定义密钥为加用户名
    secret_key = f"{secret_key_prefix}{user_account}"

    try:
        decoded_payload = jwt.decode(jwt_str, secret_key, algorithms=['HS256'])

        # logging.info(f"旧jwt信息: {decoded_payload}")

        # 成功解析说明没过期
        is_exp = False

        # 计算距离过期剩余的小时数是否小于exp_renew
        time_now_stamp = int(datetime.datetime.now().timestamp())
        time_exp_stamp = decoded_payload["exp"]
        # 获得离过期还差多少分钟
        time_renew_d = time_exp_stamp - time_now_stamp
        # 获取用户类型
        befrom = decoded_payload["befrom"]

        if (0 < time_renew_d < exp_renew or force) and not only_check:
            # 这里要查数据库, 重新生成payload, 否则可能出现用户无限续签, 修改了用户权限但前端无法及时更新到用户的身份变更
            # sql_select_template = "select * from sw_user where account = %(user_account)s and befrom = %(befrom)s"
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
            #         and u.befrom = %(befrom)s
            #     GROUP BY u.account;
            # """
            # sql_select_data = {"user_account": user_account, "befrom": befrom}
            # res_user_info_list = ms.fetch_all(sql_select_template, sql_select_data)

            latest_payload = build_payload(user_account)

            # 如果查到的结果不为空, 则说用户存在
            if latest_payload:
                # res_user_info = ms.fetch_all(sql_select_template, sql_select_data)[0]
                # 获取用户的最后登录时间, 这里获取到的时间格式是datetime.datetime(xxxx, xx, x, xx, xx, xx)
                date_latest_login = latest_payload["date_latest_login"]

                # 比较登录时间, 只有小于极限登录时间, 才可以续签
                time_login_stamp = date_latest_login
                if (time_now_stamp - time_login_stamp) < exp_max or force:
                    # 生成用户的简要信息, 用于更新jwt的payload
                    # latest_payload = {
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
                    # 用新信息续签
                    logging.info(f"用户{user_account}的jwt: {jwt_str}触发续签")
                    jwt_renew = create(latest_payload)
                    is_renew = True
                else:
                    logging.info(f"用户{user_account}的jwt已达极限登录时长, 拒绝续签: {jwt_str}")
                    # 此时应标记为过期
                    is_exp = True

    except jwt.ExpiredSignatureError:
        # jwt.ExpiredSignatureError 会自动捕获payload段内的exp字段, 并分析时间差异
        logging.error(f'用户{user_account}的jwt-token已经过期: {jwt_str}')
    except jwt.InvalidTokenError:
        logging.error(f'用户{user_account}的jwt-token解析失败: {jwt_str}')
    except Exception as el:
        logging.error(f"在判断用户{user_account}是否续签时遇到了意外的错误")
        logging.exception(el)
        raise ZeroDivisionError("登录校验系统出现了意外的错误")

    # 整理数据, 返回最终结果的元组, 分别是: (是否过期, 是否续签, 新的jwt, 用户信息)
    return is_exp, is_renew, jwt_renew, decoded_payload


def get_info(jwt_input=None) -> dict:
    """
    仅解析jwt的payload部分, 不验证其他部分
    :param jwt_input: jwt 字符串, 不传就自动获取flask的header
    :return:
    """
    if jwt_input:
        jwt_str = jwt_input
    else:
        jwt_str = request.headers.get('Authorization')

    # logging.info(f"准备仅提取payload的jwt: {jwt_str}")
    payload_base64 = re.split('\.', jwt_str)[1]
    # 如果长度不是 4 的倍数，则需要修复 padding
    padding_needed = len(payload_base64) % 12
    if padding_needed:
        payload_base64 += "=" * (12 - padding_needed)
    # logging.info(f"准备解析的jwt中段, 长度{len(payload_base64)}: {payload_base64}")
    # 解析base64, byte转字符串转字典, 数据列表中有None值可能导致解析失败
    # payload = json.loads(base64.b64decode(payload_base64).decode('utf-8'))
    # 值里面有/这样的符合要使用这个
    payload = json.loads(base64.urlsafe_b64decode(payload_base64))

    return payload
