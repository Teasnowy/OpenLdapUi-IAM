from .sms_aly import sms_aly
from . import sms_txy
from .email_send import send_email
from ..db.db_select import kvdb
from ..db.exec_ql import MysqlPool
from . import check
import random
import logging
import re


def tel_code_send(data_request: dict):
    """
    发送短信验证码的函数
    :param data_request: 字典, 字典内应包含tel, 值为手机号
    :return:
    """

    # 解析传入的信息
    try:
        tel = data_request["tel"]
    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 判断手机号码是否符合要求
    check.user_info_local(check_type='sms', tel=tel)
    # if not re.findall('^[0-9]{11}$', tel):
    #     raise ZeroDivisionError(f"手机号码应为11位数字")

    # 初始化键值数据库
    db = kvdb()

    # 获取短信相关配置
    config = db.read()["sms"]
    # 获取选择的短信运营商名字
    lsp_name = config["lsp_select"]
    # 获取选中的运营商配置信息
    lsp_config = config["lsp_list"][lsp_name]
    # 获取验证码有效期
    exp_up = config["expire_up"]
    # 标记验证码的有效期的key
    db_k_up = f'up_tel_exp_{tel}'
    # 获取同一手机号发送间隔的时长
    exp_interval = config["expire_interval"]
    # 标记同一手机号发送间隔的key
    db_k_interval = f'interval_tel_exp_{tel}'

    # 验证此手机一分钟内是否发送过验证码
    db_v_interval = db.read(k=db_k_interval, default='')
    if db_v_interval:
        logging.error(f'此手机号1分钟内已发送过验证码: {tel}')
        raise ZeroDivisionError('发短信的技能冷却时间为1分钟')

    # 生成随机验证码
    code = str(random.randint(100000, 999999))

    sms = {
        "content": f"我的大人, 本次验证码为: {code}, 5分钟内有效, 为了您的安全, 请勿向他人泄露验证码"
    }

    logging.info(f"本次生成{tel}的验证码: {code}")
    if lsp_name == 'aly':
        sms_aly().send(tel=tel, sms=sms, **lsp_config)
    elif lsp_name == 'txy':
        sms_txy.send_sms(tel=tel, data=[code], **lsp_config)
    else:
        raise ZeroDivisionError(f'不支持的短信接口: {lsp_name}, 请联系管理员')

    # 插入表明验证码有效期的key
    db.set(k=db_k_up, v=code, expire=exp_up)
    # 插入表明手机号发送间隔的key
    db.set(k=db_k_interval, v=code, expire=exp_interval)

    return {"ok": "ok"}


def email_code_send(data_request, ):
    """
    发送邮箱验证码
    :param data_request: 前端传来的json, 里面应包含: email
    :return:
    """

    # 验证传入的信息
    try:
        email = data_request["email"]
        # 判断邮箱是否符合规定
    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 判断邮箱是否符合要求
    check.user_info_local(check_type='email', email=email)
    # if not re.findall('@', email):
    #     raise ZeroDivisionError(f"看起来不是有效的邮箱地址")

    # 初始化键值数据库
    db = kvdb()

    # 获取邮箱相关配置
    config = db.read()["email"]
    # 获取验证码有效期
    exp_up = config["expire_up"]
    # 标记验证码的有效期的key
    db_k_up = f'up_email_exp_{email}'
    # 获取同一手机号发送间隔的时长
    exp_interval = config["expire_interval"]
    # 标记同一手机号发送间隔的key
    db_k_interval = f'interval_email_exp_{email}'

    # 验证此邮箱一分钟内是否发送过验证码
    db_v_interval = db.read(k=db_k_interval, default='')
    logging.info(f"---------------{db_k_interval}------------------{db.read(k=db_k_interval, default='')}")
    if db_v_interval:
        logging.error(f'此邮箱1分钟内已发送过验证码: {email}')
        raise ZeroDivisionError('发邮件的技能冷却时间为1分钟')

    # 先占一个key, 防止狂点按钮, 钻了发送期间的空
    db.set(k=db_k_interval, v="", expire=exp_interval)

    # 生成随机验证码
    code = str(random.randint(100000, 999999))
    # 拼写邮件正文
    text = f"我的大人, 本次验证码为: {code}, 5分钟内有效, 为了您的安全, 请勿向他人泄露验证码"
    # 定义邮件标题
    title = f'验证码: {code}'

    # 尝试发送
    try:
        send_email(to_addr=email, title=title, text=text)
        # 插入表明验证码有效期的key
        db.set(k=db_k_up, v=code, expire=exp_up)
        # 插入表明手机号发送间隔的key
        db.set(k=db_k_interval, v=code, expire=exp_interval)
        logging.info(f"向邮箱: {email} 发送验证码: {code}")
    except Exception as el:
        logging.error(f"向{email}发送邮件失败")
        logging.exception(el)
        raise ZeroDivisionError(f"向{email}发送邮件失败")

    return {"ok": "ok"}


def check_tel_email(data_request):
    """
    查询指定的用户是否有手机号或邮箱
    :param data_request: 应包含账户名user_account
    :return:
    """

    # 验证传入的信息
    try:
        user_account = data_request["user_account"]
        # 判断邮箱是否符合规定
    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 初始化数据库连接并编辑语句
    mp = MysqlPool()
    sql_select_template = """
            select * from sw_user 
            where 
                account = %(user_account)s
                -- 不再区分本地和其他类型用户
                -- and befrom = 'local'
                ;
        """
    sql_select_data = {"user_account": user_account}
    res_user_info = mp.fetch_one(sql_select_template, sql_select_data)
    if not res_user_info:
        raise ZeroDivisionError("该用户没有登记有效邮箱或手机号")

    # 抽取手机号码的前三位和后四位
    tel = res_user_info['tel']
    if tel:
        tel_vague = f"{tel[0:3]}****{tel[-4:]}"
    else:
        tel_vague = None
    # 抽取邮箱的前两位和@后面
    email = res_user_info['email']
    if email:
        email_vague = f"{email[0:2]}****{re.findall('@.*', email)[0]}"
    else:
        email_vague = None

    # 定义返回数据
    data_result = {
        "tel_vague": tel_vague,
        "email_vague": email_vague
    }

    return data_result


def email_code_send_account(data_request):
    """
    向指定本地用户对应的邮箱发送验证码
    :param data_request: 应包含账户名user_account
    :return:
    """

    # 验证传入的信息
    try:
        user_account = data_request["user_account"]
        # 判断邮箱是否符合规定
    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 初始化数据库连接并编辑语句
    mp = MysqlPool()
    sql_select_template = """
            select * from sw_user 
            where 
                account = %(user_account)s 
                -- 不再区分本地和其他类型用户
                -- and befrom = 'local'
                ;
        """
    sql_select_data = {"user_account": user_account}
    res_user_info = mp.fetch_one(sql_select_template, sql_select_data)
    if not res_user_info:
        raise ZeroDivisionError("该用户没有登记有效邮箱或手机号")
    # 提取邮箱地址
    user_email = res_user_info["email"]
    # 发送邮件
    email_code_send({"email": user_email})
    return {"ok": "ok"}


def tel_code_send_account(data_request):
    """
    向指定本地用户对应的手机号发送验证码
    :param data_request: 应包含账户名user_account
    :return:
    """

    # 验证传入的信息
    try:
        user_account = data_request["user_account"]
        # 判断邮箱是否符合规定
    except Exception as el:
        logging.error(f"报文格式错误: {data_request}")
        logging.exception(el)
        raise ZeroDivisionError("报文格式错误")

    # 初始化数据库连接并编辑语句
    mp = MysqlPool()
    sql_select_template = """
            select * from sw_user 
            where 
                account = %(user_account)s 
                -- 不再区分本地和其他类型用户
                -- and befrom = 'local'
                ;
        """
    sql_select_data = {"user_account": user_account}
    res_user_info = mp.fetch_one(sql_select_template, sql_select_data)
    if not res_user_info:
        raise ZeroDivisionError("该用户没有登记有效邮箱或手机号")
    # 提取邮箱地址
    user_tel = res_user_info["tel"]
    # 发送邮件
    tel_code_send({"tel": user_tel})
    return {"ok": "ok"}