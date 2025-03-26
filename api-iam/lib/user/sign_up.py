from .sms_aly import sms_aly
from .email_send import send_email
from ..db.db_select import kvdb
from ..data_format import res_format, str_to_md5
from ..db.exec_ql import MysqlPool
from . import check
import random
import logging
import re


def entry(data_request):
    """
    用户注册函数的入口
    :param data_request: 应包含user_account, user_displayname, password, tel, email, code_input, user_type
    :return:
    """
    try:
        user_type = data_request['user_type']
    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 根据用户类型判断如何注册
    if user_type == 'local':
        up_local(data_request)
    elif user_type == 'ldap':
        raise ZeroDivisionError('暂不支持ldap注册')
    else:
        raise ZeroDivisionError(f'不支持的注册类型: {user_type}')

    data_result = {
        "ok": "ok",
    }

    return data_result


def up_local(data_request):
    """
    本地用户注册函数的入口
    :param data_request: 应包含 user_account, user_displayname, password, tel, email, code_tel_input, code_email_input, user_type
    :return:
    """

    # 解析传入的信息
    try:
        del data_request['password_1']
        # 头像图片的base64
        user_photo_base64 = data_request["user_photo_base64"]
        user_account = data_request["user_account"]
        user_displayname = data_request["user_displayname"]
        user_password = data_request["password"]
        # 用户填入的手机号
        tel = data_request["tel"]
        email = data_request["email"]
        # 前台填入的短信验证码
        if tel:
            code_tel_input = data_request["code_tel_input"]
        else:
            code_tel_input = ''
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

    # 判断传入参数是否合规----------------
    check.user_info_local(**data_request, check_type='signup')
    # 标记短信验证码的有效期的key
    db_k_up_tel = f'up_tel_exp_{tel}'
    # 标记邮箱短信验证码的有效期的key
    db_k_up_email = f'up_tel_exp_{email}'

    # 初始化键值数据库
    db = kvdb()
    # 初始化mysql数据库
    ms = MysqlPool()
    list_sql = []

    # 获取注册相关配置
    cf = db.read()
    cf_auth = cf['auth']
    # 获取此电话号码对应的验证码
    # code_db_tel = db.read(k=db_k_up_tel, default='')
    # 判断是否开启了必须验证手机号的规则
    must_tel = cf_auth['must_tel']
    # 判断是否开启了必须验证邮箱的规则
    must_email = cf_auth['must_email']

    # 判断短信验证码是否已失效或不对
    if tel and must_tel == 'yes':
        check.check_code_sms(tel, code_tel_input)

    # 如果用户填了邮箱, 验证邮箱验证码是否正确
    if email and must_email == 'yes':
        check.check_code_email(email, code_email_input)

    # 判断用户名是否重复
    # 这里的select不能指定为count, 不然还是始终会返回一行数据
    # user_namesake = ms.fetch_all("select * from sw_user where account = %s and befrom = %s", (user_account, user_type))
    user_namesake = ms.fetch_all("select * from sw_user where account = %s;", (user_account,))
    if user_namesake:
        logging.error(f"查询到同名用户数据: {user_namesake}")
        raise ZeroDivisionError("用户名已被注册")

    # 对密码加密
    # user_password_encrypt = encrypt_string(user_account, user_password)
    # 放弃加密, 直接由前端做单向加密
    user_password_encrypt = user_password

    # 校验头像, 允许为空
    check.rule_photo(user_photo_base64, is_null=True)
    # 获取图像md5
    photo_md5 = str_to_md5(user_photo_base64)

    # 开始向数据库内写入用户信息
    # 编辑语句
    template_usercreate = """
        insert into `sw_user` (user_id, account, displayname, email, tel, befrom, 
            status, password, photo_id, date_create, date_update, date_latest_login)
        values (null, %(account)s, %(displayname)s, %(email)s, %(tel)s, 'local', 
            'on', %(password)s, %(photo_id)s, now(), now(), now());
    """
    list_sql.append(template_usercreate)

    # 删除可能已有的遗留权限关系
    sql_delete_roles = "delete from sw_roleuser where account = %(account)s;"
    list_sql.append(sql_delete_roles)
    # 删除可能已有的遗留组关系
    sql_delete_groups = "delete from sw_usergroup where account = %(account)s;"
    list_sql.append(sql_delete_groups)

    # 编写插入图片的语句
    sql_insert_tem = """
        replace into sw_photo (photo_id, photo_base64) values (%(photo_id)s, %(photo_base64)s)
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

    data_usercreate = {
        "account": user_account,
        "displayname": user_displayname,
        "email": email,
        "tel": tel,
        "password": user_password_encrypt,
        "photo_id": photo_md5,
        "photo_base64": user_photo_base64,
    }

    # for i in list_sql:
    #     print(i)

    # 注册用户
    ms.transaction(list_sql, data_usercreate, is_list=True)
    # 向数据库写入图片 (为保证事务顺序, 放弃额外的函数)
    # photo_to_db(user_photo_base64, photo_md5)
    logging.info(f"用户: {user_account}注册成功")


# def tel_code_send(data_resource: dict):
#     """
#     发送短信验证码的函数
#     :param data_resource: 字典, 字典内应包含tel, 值为手机号
#     :return:
#     """
#
#     # 解析传入的信息
#     try:
#         tel = data_resource["tel"]
#     except Exception as el:
#         logging.error(f"报文格式错误: {data_resource}")
#         logging.exception(el)
#         raise ZeroDivisionError("报文格式错误")
#
#     # 判断手机号码是否符合要求
#     check.user_info_local(check_type='sms', tel=tel)
#     # if not re.findall('^[0-9]{11}$', tel):
#     #     raise ZeroDivisionError(f"手机号码应为11位数字")
#
#     # 初始化键值数据库
#     db = kvdb()
#
#     # 获取短信相关配置
#     config = db.read()["sms"]
#     # 获取选择的短信运营商名字
#     lsp_name = config["lsp_select"]
#     # 获取选中的运营商配置信息
#     lsp_config = config["lsp_list"][lsp_name]
#     # 获取验证码有效期
#     exp_up = config["expire_up"]
#     # 标记验证码的有效期的key
#     db_k_up = f'up_tel_exp_{tel}'
#     # 获取同一手机号发送间隔的时长
#     exp_interval = config["expire_interval"]
#     # 标记同一手机号发送间隔的key
#     db_k_interval = f'interval_tel_exp_{tel}'
#
#     # 验证此手机一分钟内是否发送过验证码
#     db_v_interval = db.read(k=db_k_interval, default='')
#     if db_v_interval:
#         logging.error(f'此手机号1分钟内已发送过验证码: {tel}')
#         raise ZeroDivisionError('发短信的技能冷却时间为1分钟')
#
#     # 生成随机验证码
#     code = str(random.randint(100000, 999999))
#
#     sms = {
#         "content": f"我的大人, 本次验证码为: {code}, 5分钟内有效, 为了您的安全, 请勿向他人泄露验证码"
#     }
#
#     logging.info(f"本次生成{tel}的验证码: {code}")
#     if lsp_name == 'aly':
#         sms_aly().send(tel=tel, sms=sms, **lsp_config)
#     else:
#         raise ZeroDivisionError('不支持的短信接口, 请完善功能')
#
#     # 插入表明验证码有效期的key
#     db.set(k=db_k_up, v=code, expire=exp_up)
#     # 插入表明手机号发送间隔的key
#     db.set(k=db_k_interval, v=code, expire=exp_interval)
#
#     return {"data": "OK"}
#
#
# def email_code_send(data_resource, ):
#     """
#     发送邮箱验证码
#     :param data_resource: 前端传来的json, 里面应包含: email
#     :return:
#     """
#
#     # 验证传入的信息
#     try:
#         email = data_resource["email"]
#         # 判断邮箱是否符合规定
#     except Exception as el:
#         logging.error(f"报文格式错误: {data_resource}")
#         logging.exception(el)
#         raise ZeroDivisionError("报文格式错误")
#
#     # 判断邮箱是否符合要求
#     check.user_info_local(check_type='email', email=email)
#     # if not re.findall('@', email):
#     #     raise ZeroDivisionError(f"看起来不是有效的邮箱地址")
#
#     # 初始化键值数据库
#     db = kvdb()
#
#     # 获取邮箱相关配置
#     config = db.read()["email"]
#     # 获取验证码有效期
#     exp_up = config["expire_up"]
#     # 标记验证码的有效期的key
#     db_k_up = f'up_email_exp_{email}'
#     # 获取同一手机号发送间隔的时长
#     exp_interval = config["expire_interval"]
#     # 标记同一手机号发送间隔的key
#     db_k_interval = f'interval_email_exp_{email}'
#
#     # 验证此邮箱一分钟内是否发送过验证码
#     db_v_interval = db.read(k=db_k_interval, default='')
#     if db_v_interval:
#         logging.error(f'此邮箱1分钟内已发送过验证码: {email}')
#         raise ZeroDivisionError('发邮件的技能冷却时间为1分钟')
#
#     # 生成随机验证码
#     code = str(random.randint(100000, 999999))
#     # 拼写邮件正文
#     text = f"我的大人, 本次验证码为: {code}, 5分钟内有效, 为了您的安全, 请勿向他人泄露验证码"
#     # 定义邮件标题
#     title = f'验证码: {code}'
#
#     # 尝试发送
#     try:
#         send_email(to_addr=email, title=title, text=text)
#         # 插入表明验证码有效期的key
#         db.set(k=db_k_up, v=code, expire=exp_up)
#         # 插入表明手机号发送间隔的key
#         db.set(k=db_k_interval, v=code, expire=exp_interval)
#         logging.info(f"向邮箱: {email} 发送验证码: {code}")
#     except Exception as el:
#         logging.error(f"向{email}发送邮件失败")
#         logging.exception(el)
#         raise ZeroDivisionError(f"向{email}发送邮件失败")
#
#     return {"data": "OK"}


