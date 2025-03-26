import datetime
import logging
import hashlib
import base64
from flask import jsonify, request
from .user import login_jwt
from .db.db_select import kvdb


def res_format(data=None, ok=None, err=None, code=None, jwt=None):
    """
    格式化后端生成的数据, 用来相应前端
    :param data: 正常返回的数据
    :param ok: 本次请求的状态, 正常应该是ok
    :param err: 错误信息, 可以为空
    :param code: 状态码, 正常为10000
    :param jwt: 当jwt被更新时, 将用此属性通知前端更新
    :return:
    """

    if err and not ok:
        # 如果有异常信息且没定义状态, 则赋值no
        ok = 'no'
    elif not ok:
        # 如果仅没定义状态, 则赋值ok
        ok = 'ok'

    # 如果err信息不为空,且code为空, 则code默认为10001
    if err and not code:
        code = 10001
    elif code:
        # 如果手动指定了code, 那么就用指定的值
        pass
    else:
        # 正常返回时code设定为10000
        code = 10000
    # logging.info(f"{type(data)}: {data}")

    # 如果发现data已被包装, 则不做动作

    # 返回格式为字典时的已包装判断
    # logging.info(f"被格式化的数据格式为: {type(data)}")
    if data and isinstance(data, dict):
        # logging.info(f"被格式化的数据key为: {list(data.keys())}")
        # logging.info(sorted(data.keys()))
        # logging.info(["code", "ok", "message_err", "data", "jwt", "time", ].sort())
        # 这里要注意列表内的元素的顺序, 与data_return中一致, 不然不会被判断一样
        if sorted(data.keys()) == sorted(["code", "ok", "message_err", "data", "jwt", "time", ]):
            logging.info(f"已被格式化, 返回原数据")
            return data

    # 返回格式为字符串时的已包装判断
    # try:
    #     json.loads(data)
    #     if list(data.keys()) == ["code", "ok", "message_err", "data", "time"]:
    #         return data
    # except Exception:
    #     pass

    data_return = {
        "code": code,
        "ok": ok,
        "message_err": err,
        "data": data,
        "jwt": jwt,
        "time": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    }

    # 这里依旧使用字符串, 因为用字典格式返回会导致raise ZeroDivisionError()无法被json序列化, 即使是flask的jsonify也不行
    # return json.dumps(data_return, default=str)
    # 这里又恢复了字典形式, 是因为接口处使用except ZeroDivisionError针对其单独做字符串
    return data_return


# 统一整理接口的各种try, 其中调用的函数必须只能接受data_request一个参数
def interface_try(func, request_input, is_jwt=True):
    """
    统一整理接口的各种try, 其中调用的函数必须只能接受data_request一个参数
    :param func: 处理数据的主函数
    :param request_input: 数据, 一般都是request
    :param is_jwt: 是否需要检查jwt
    :return:
    """
    url = request.url_rule.rule
    logging.info(f"当前请求的路径: {url}")
    # 初始化可能会更新的jwt
    jwt_renew = None
    # 初始化用户信息, 用来做可能需要的权限验证
    decoded_payload = None
    # 初始化用户名
    user_account = request_input.headers.get('X-Username')

    try:
        data_json = request_input.json
        if not data_json:
            logging.error(f'{url}: POST报文为空, 已返回：Nothing to deal with')
            return res_format(err='POST报文为空'), 400
    except Exception as el:
        logging.error(f'{url}: POST报文格式必须为json, 数据:{request_input.data}')
        logging.exception(el)
        return res_format(err='POST报文格式必须为json'), 400
    logging.info(f"{url}: 收到报文: {data_json}")

    # 尝试校验登录凭据
    try:
        if is_jwt:
            # 获取jwt
            jwt_header = request_input.headers.get('Authorization')
            if not jwt_header:
                logging.error(f'{url}: 用户{user_account}未提供凭据, 拒绝服务')
                return res_format(err="未检测到访问凭证", code=40001), 401
            # 检查头部格式
            if not jwt_header.startswith('Bearer '):
                logging.error(f'{url}: 用户{user_account}传来的凭证格式错误, 拒绝服务')
                return res_format(err="访问凭证错误", code=40001), 401
            # 提取真正的令牌部分
            jwt_request = jwt_header.split(" ")[1]

            # 校验与键值数据库中是否一致
            kv = kvdb()
            key_jwt = f"jwt_{user_account}"
            value_kvdb_jwt = kv.read(key_jwt)
            if value_kvdb_jwt != jwt_request:
                return res_format(err="已在别处注销或已过期, 请重新登录", code=40001), 401

            # 校验jwt
            is_exp, is_renew, jwt_renew, decoded_payload = login_jwt.check(jwt_request, user_account)
            # logging.info(is_exp, is_renew, jwt_renew, decoded_payload)
            if is_exp:
                # raise ZeroDivisionError('凭证已过期')
                # logging.error(f"检测到{user_account}凭证过期")
                return res_format(err="凭证已过期", code=40001), 401

            # 校验后端接口权限, admin除外
            if decoded_payload['account'] != 'admin':
                if url not in decoded_payload['apis']:
                    return res_format(err='权限不足, 拒绝访问', code=40002), 401
    except Exception as el:
        logging.error(f'{url}: 用户{user_account}传来的凭证有问题, 拒绝服务')
        logging.exception(el)
        return res_format(err=str(el), code=40001), 401

    # 处理数据
    try:
        res_tmp = func(data_json)
        # logging.info(res)
        res = res_format(res_tmp)
        # logging.info(f"{url}: 返回: {res}")
        response = jsonify(res)
        # 添加自定义标头
        if jwt_renew:
            response.headers['X-JWT-RENEW'] = jwt_renew
        # logging.info(f"返回的标头: {response.headers}")
        return response, 200
    except ZeroDivisionError as el:
        # 捕获 ZeroDivisionError 并提取错误信息
        res_el = res_format(err=str(el))
        logging.error(f"{url}: 返回报文: {res_el}")
        logging.exception(el)
        return res_el, 500
    except Exception as el:
        res_el = res_format(err=str(el))
        logging.error(f"{url}: 返回报文: {res_el}")
        logging.exception(el)
        return res_el, 500


def file_to_base64_md5(image_path):
    # 读取图像文件并转换为 Base64
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data).decode('utf-8')

        # 计算 MD5 值
        md5_hash = hashlib.md5(image_data).hexdigest()

        return base64_encoded, md5_hash

def str_to_md5(text:str):
    if not text:
        return None
    # 创建 MD5 哈希对象
    md5_hash = hashlib.md5()

    # 将字符串编码为字节并更新哈希对象
    md5_hash.update(text.encode('utf-8'))

    # 获取并打印 MD5 哈希值（以十六进制形式表示）
    md5_value = md5_hash.hexdigest()
    return md5_value