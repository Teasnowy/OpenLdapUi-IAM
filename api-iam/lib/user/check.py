import re
import unicodedata
import logging
from ..db.db_select import kvdb
from ..db.exec_ql import MysqlPool
from ..db.ldap_general import ldap_getattrs
from flask import jsonify, request


def get_custom_length(s: str) -> int:
    """
    计算字符串长度, 中文算2长度
    :param s:
    :return:
    """
    length = 0
    for char in s:
        # 判断字符是否为中文字符
        if unicodedata.category(char) == 'Lo':  # 'Lo' 是 Unicode 中的字母类，中文字符通常属于此类
            length += 2  # 中文字符视为两个字符
        else:
            length += 1  # 英文字符视为一个字符
    return length


def rule_account(user_account):
    """
    校验用户名格式
    :param user_account: 用户名
    :return:
    """

    # 必须是字符串
    if not isinstance(user_account, str):
        raise ZeroDivisionError(f"用户名必须是字符串格式")
    # 定义用户名和别名中允许包含的特殊字符
    nterpunction_user_list = ['_']
    # 判断用户名中是否包含不支持的特殊字符
    tmp_useraccount = re.sub('[a-zA-Z0-9]', '', user_account)
    for i in tmp_useraccount:
        if i not in nterpunction_user_list:
            raise ZeroDivisionError(f"用户名中仅允许包含特殊字符: {''.join(nterpunction_user_list)}")
    # 判断用户名位数是否超长
    if 4 > len(user_account) or len(user_account) > 30:
        raise ZeroDivisionError(f"用户名长度应在4至30字符之间")
    # logging.info(f"account{len(user_account)}通过")

def rule_displayname(user_displayname):
    """
    校验别名格式
    :param user_displayname: 别名
    :return:
    """

    # 必须是字符串
    if not isinstance(user_displayname, str):
        raise ZeroDivisionError(f"显示名必须是字符串格式")
    # 定义用户名和别名中允许包含的特殊字符
    nterpunction_user_list = ['-', '_']
    tmp_displayname = re.sub('[\u4e00-\u9fa5a-zA-Z0-9]', '', user_displayname)
    for i in tmp_displayname:
        if i not in nterpunction_user_list:
            raise ZeroDivisionError(f"显示名中仅允许包含特殊字符: {''.join(nterpunction_user_list)}")
    # 判断用户别名是否超长
    n = get_custom_length(user_displayname)

    if 4 > n or n > 30:
        raise ZeroDivisionError(f"名字长度应在4至30字符之间")


def rule_desc(desc, num_max:int=300, not_null=False):
    """
    校验详细描述信息
    :param desc:
    :param num_max: 最长支持多少字符, 默认300
    :param not_null: 是否不能为空, 默认为否
    :return:
    """

    if not_null and not desc:
        raise ZeroDivisionError(f"描述信息不允许为空")

    # 判断否超长
    n = get_custom_length(desc)

    if n > num_max:
        raise ZeroDivisionError(f"描述信息长度不能超过{num_max}")


def rule_url(url, num_max:int=300, not_null=True):
    """
    校验url
    :param url:
    :param num_max: 最长支持多少字符, 默认300
    :param not_null: 是否不能为空, 默认为否
    :return:
    """

    if not_null and not url:
        raise ZeroDivisionError(f"url不允许为空")

    # 判断否超长
    n = get_custom_length(url)

    if n > num_max:
        raise ZeroDivisionError(f"url长度不能超过{num_max}")



def rule_password(user_password):
    """
    校验密码格式
    :param user_password: 密码
    :return:
    """

    # 必须是字符串
    if not isinstance(user_password, str):
        raise ZeroDivisionError(f"密码必须是字符串格式")

    # 定义密码中允许包含的特殊字符
    nterpunction_passwd_list = '!@#$%^&*()_+-=,./?;:'
    if 30 < len(user_password) or len(user_password) < 6:
        raise ZeroDivisionError(f"密码长度应在6至30字符之间")
    # 判断密码中的特殊字符是否符合规定
    tmp_passwd = re.sub('[a-zA-Z0-9]', '', user_password)
    # logging.info(tmp_passwd)
    for i in tmp_passwd:
        if i not in nterpunction_passwd_list:
            raise ZeroDivisionError(f"密码中仅允许包含特殊字符: {''.join(nterpunction_passwd_list)}")


def rule_tel(tel, code_tel_input=None, need_code=True, not_null=True):
    """
    验证手机号格式, 需要的话, 一起校验验证码(仅格式, 不校验有效性)
    :param tel: 手机号
    :param code_tel_input: 验证码
    :param need_code: 是否需要一起校验验证码
    :param not_null: 是否允许邮箱为空
    :return:
    """

    # 如果不允许手机号为空
    if not_null:
        if not tel:
            raise ZeroDivisionError(f"手机号码不能为空")

    # 判断手机号码是否符合长度, 这里兼容为空的情况
    if tel:
        # 必须是字符串
        if not isinstance(tel, str):
            raise ZeroDivisionError(f"手机号码必须是字符串格式")
        if not re.findall('^[0-9]{11}$', tel):
            raise ZeroDivisionError(f"手机号码应为11位数字")

    # 当需要验证码关联时, 一起校验验证码格式
    if need_code:
        # 必须是字符串
        if not isinstance(code_tel_input, str):
            raise ZeroDivisionError(f"短信验证码必须是字符串格式")
        # 判断短信验证码长度
        if len(code_tel_input) != 6:
            raise ZeroDivisionError(f"短信验证码格式不对")


def rule_email(email, code_email_input=None, need_code=True, not_null=True):
    """
    验证邮箱地址格式, 需要的话, 一起校验验证码(仅格式, 不校验有效性)
    :param email: 邮箱地址
    :param code_email_input:  邮箱验证码
    :param need_code: 是否需要一起校验验证码
    :param not_null: 是否允许邮箱为空
    :return:
    """
    # 如果不允许邮箱为空
    if not_null:
        if not email:
            raise ZeroDivisionError(f"邮箱地址不能为空")

    # 判断邮箱是否符合规定, 兼容为空的情况
    if email:
        # 必须是字符串
        if not isinstance(email, str):
            raise ZeroDivisionError(f"邮箱地址必须是字符串格式")
        if not re.findall('.+@.+', email):
            raise ZeroDivisionError(f"看起来不是有效的邮箱地址")
        if need_code:
            # 必须是字符串
            if not isinstance(code_email_input, str):
                raise ZeroDivisionError(f"邮箱验证码必须是字符串格式")
            # 且此时邮箱验证码不应该为空, 应为6位数字
            if len(code_email_input) != 6:
                raise ZeroDivisionError(f"邮箱验证码格式不对")


def check_auth_api(apis):
    """
    检查当前进程接口是否在允许范围内
    :param apis:
    :return:
    """


def check_code_sms(tel, code_tel_input):
    """
    校验短信验证码是否正确有效
    :param tel: 手机号
    :param code_tel_input: 验证码
    :return:
    """

    # 必须是字符串
    if not isinstance(code_tel_input, str):
        raise ZeroDivisionError(f"短信验证码必须是字符串格式")
    # 判断短信验证码长度
    if len(code_tel_input) != 6:
        raise ZeroDivisionError(f"短信验证码格式不对")

    # 标记短信验证码的有效期的key, , 此变量的值必须与user.sign_up.tel_code_send中的变量db_k_up的值相同
    db_k_up_tel = f'up_tel_exp_{tel}'

    # 初始化键值数据库
    db = kvdb()

    # 获取此电话号码对应的验证码
    code_db_tel = db.read(k=db_k_up_tel, default='')

    # 判断短信验证码是否已失效或不对
    if not code_db_tel:
        logging.error(f"手机号: {tel} 的验证码已失效")
        raise ZeroDivisionError("短信验证码已失效")
    elif str(code_db_tel) != str(code_tel_input):
        logging.error(f"手机号: {tel} 填写的验证码{code_tel_input}与数据库中{code_db_tel}不符")
        raise ZeroDivisionError("短信验证码错误")


def check_code_email(email, code_email_input):
    """
    校验邮箱验证码是否正确有效
    :param email: 邮箱
    :param code_email_input: 验证码
    :return:
    """

    # 必须是字符串
    if not isinstance(code_email_input, str):
        raise ZeroDivisionError(f"邮箱验证码必须是字符串格式")
    # 且此时邮箱验证码不应该为空, 应为6位数字
    if len(code_email_input) != 6:
        raise ZeroDivisionError(f"邮箱验证码格式不对")

    # 标记邮箱短信验证码的有效期的key, 此变量的值必须与user.sign_up.email_code_send中的变量db_k_up的值相同
    db_k_up_email = f'up_email_exp_{email}'

    # 初始化键值数据库
    db = kvdb()

    # 获取此邮箱对应的验证码
    code_db_email = db.read(k=db_k_up_email, default='')
    # 判断邮箱验证码是否已失效或不对
    if not code_db_email:
        logging.error(f"邮箱: {email} 的验证码已失效")
        raise ZeroDivisionError("邮箱验证码已失效")
    elif str(code_db_email) != str(code_email_input):
        logging.error(f"邮箱: {email} 填写的验证码{code_email_input}({type(code_email_input)})与数据库中{code_db_email}({type(code_db_email)})不符")
        raise ZeroDivisionError("邮箱验证码错误")


def rule_ous_attrs(list_input_attrs:list):
    """
    检查用户传来的字段名在不在模板中
    :return:
    """

    # 获取所有模板中的属性列表
    list_ldap_attrs = ldap_getattrs()
    for input_attrs in list_input_attrs:
        if input_attrs.casefold() not in (item.casefold() for item in list_ldap_attrs):
            logging.error(f"ldap属性{input_attrs}即使忽略大小写也无法在全局变量list_ldap_attrs中匹配到")
            raise ZeroDivisionError(f"ldap属性{input_attrs}超出三界之外, 不在五行之中")


def rule_photo(user_photo_basr64:str|None, is_null:bool=False):
    """
    校验上传的头像的basr64, 必须带有MIME标识
    :param user_photo_basr64:
    :param is_null: 是否允许为空
    :return:
    """
    # 校验头像格式

    if not user_photo_basr64:
        if is_null:
            return
        else:
            raise ZeroDivisionError("没有收到有效的图像")

    if not isinstance(user_photo_basr64, str):
        raise ZeroDivisionError("上传的头像数据格式不正确")

    # 定义允许的图片类型
    # ["image/png", "image/jepg", "image/gif"]
    type_white_list = ["image/jpeg", "image/gif", "image/png"]

    # 计算头像大小
    photo_size = len(user_photo_basr64.encode('utf-8'))
    logging.info(f"头像大小: {photo_size}")
    # 因为base64字符串普遍比原图片大1/3, 这里限制头像大小为153600, 约150KB
    if photo_size > 153600:
        raise ZeroDivisionError("压缩后图片大小仍超过100KB")

    # 从base64字符串中提取图片格式
    find_type =  re.findall('^data:[^;]*', user_photo_basr64)
    if find_type:
        # 校验图片格式
        t = re.split(':', find_type[0])[1]
        if t not in type_white_list:
            raise ZeroDivisionError(f"不支持的图像格式: {t}")
    else:
        raise ZeroDivisionError("无法识别的图像格式")


    return

def check_auth_num(user_type, user_account, clean_up: bool=False):
    """
    检查用户登录次数
    :param user_type: 用户类型, 是ldap还是local
    :param user_account: 用户的账号
    :param clean_up: 布尔值, 次数是否置零
    :return:
    """
    key_auth_num = f'num_auth_{user_type}_{user_account}'
    # 初始化键值数据库
    dc = kvdb()

    # 如果置零, 那么就删除这个key
    if clean_up:
        dc.delete(key_auth_num)
        return
    # 获取登录相关配置
    cf = dc.read()["auth"]
    limit_duration = cf["limit_duration"]
    limit_num = cf["limit_num"]

    # 判断登录次数是否超过配置
    num_auth = dc.get(key_auth_num, default=0)
    if limit_num <= int(num_auth):
        # raise ZeroDivisionError(f"您已失败{limit_num}次, 请{limit_duration}秒后再试")
        raise ZeroDivisionError(f"登录频繁, 请{limit_duration}秒后再试")
    # 登录次数+1
    dc.incr(1, key_auth_num, expire=limit_duration)
    return


def check_user_exist_local(user_account, befrom='local') -> dict|None:
    """
    单个用户是否存在, 返回用户信息, 不存在则报错
    :param user_account: 账号名
    :param befrom: 用户类型, 默认为本地用户
    :return:
    """
    # 初始化数据库连接池
    mp = MysqlPool()

    # 按账号和手机号查找, 有数据说明手机号与账号匹配
    sql_select_template = """
            select * from sw_user 
            where 
                account = %(user_account)s 
                -- 不再限制用户种类
                -- and befrom = %(befrom)s
                ;
        """
    sql_select_data = {"user_account": user_account, "befrom": befrom}
    res_user_info = mp.fetch_one(sql_select_template, sql_select_data)
    if not res_user_info:
        raise ZeroDivisionError(f"{user_account}用户不存在")

    return res_user_info


def check_users_notexist_local(user_account_list, befrom='local'):
    """
    多个用户是否都不存在, 有一个存在则报错
    :param user_account_list: 账号名的列表
    :param befrom: 用户类型, 默认为本地用户
    :return:
    """
    # 初始化数据库连接池
    mp = MysqlPool()

    # 不再分辨befrom, 全局账号唯一
    sql_select_template = """
        select account from sw_user 
        where 
            account in %(user_account)s 
            -- 不再区分本地和其他类型用户
            -- and befrom = %(befrom)s
            ;
    """
    sql_select_data = {"user_account": user_account_list, "befrom": befrom}
    res_user_info = mp.fetch_all(sql_select_template, sql_select_data)
    res_user_list = [i['account'] for i in res_user_info]
    if res_user_info:
        raise ZeroDivisionError(f"账号 {' '.join(res_user_list)} 已存在于数据库")


def check_users_exist_local(user_account_list):
    """
    多个用户是否都存在, 有一个不存在则报错
    :param user_account_list: 账号名的列表
    :return:
    """
    # 初始化数据库连接池
    mp = MysqlPool()

    # 按账号和手机号查找, 有数据说明手机号与账号匹配
    sql_select_template = """
        select account from sw_user 
        where 
            account in %(user_account)s;
    """
    sql_select_data = {"user_account": user_account_list,}
    res_user_info = mp.fetch_all(sql_select_template, sql_select_data)
    list_account_db = [i["account"] for i in res_user_info]
    for u in  user_account_list:
        if u not in list_account_db:
            raise ZeroDivisionError(f"只有{u}不存在的街道")


def check_account_repeat(list_tmp):
    """
    检查列表中是否有重复元素
    :param list_tmp: 列表
    :return: bool
    """
    if len(list_tmp) > len(set(list_tmp)):
        raise ZeroDivisionError("提交的用户名中有重复值")



def check_account_and_tel(user_account, tel):
    """
    检查用户与手机号是否匹配
    :param user_account:
    :param tel:
    :return:
    """
    pass


def check_account_and_email(user_account, email):
    """
    检查用户与邮箱地址是否匹配
    :param user_account:
    :param email:
    :return:
    """
    pass


def user_info_local(
        user_account=None, user_displayname=None, password=None, tel=None, code_tel_input=None, email=None,
        code_email_input=None, user_type='local', user_photo_base64='', check_type=None,
):
    """
    校验用户注册或修改时进行的各种用户信息的格式校验
    :param user_photo_base64: 用户头像的base64编码, 注册时可以为空
    :param user_account: 用户账号
    :param user_displayname:    别名
    :param password:   密码
    :param tel: 电话
    :param code_tel_input: 手机验证码
    :param email: 邮箱
    :param code_email_input: 邮箱验证码
    :param user_type: 用户类型, 目前仅支持本地local
    :param check_type: 校验类型, 可以为: 注册signup, 更新update, 登录login, 短信验证sms, 邮箱验证email
    :return:
    """

    # 初始化键值数据库
    dc = kvdb()
    # 获取登录相关配置
    cf_auth = dc.read()["auth"]
    # 判断是否开启了必须验证手机号的规则
    cf_must_tel = cf_auth['must_tel']
    must_tel = False
    not_null_tel = False
    if cf_must_tel == 'yes':
        must_tel = True
        not_null_tel = True
    # 判断是否开启了必须验证邮箱的规则
    cf_must_email = cf_auth['must_email']
    must_email = False
    not_null_email = False
    if cf_must_email == 'yes':
        must_email = True
        not_null_email = True

    # 如果是本地用户注册的校验
    if check_type == 'signup' and user_type == 'local':
        # 邮箱和手机号至少填一个
        if not tel and not email:
            raise ZeroDivisionError("邮箱和手机号至少填写一个")
        rule_photo(user_photo_base64, is_null=True)
        rule_account(user_account)
        rule_displayname(user_displayname)
        rule_tel(tel, code_tel_input, not_null=not_null_tel, need_code=must_tel)
        rule_password(password)
        # 邮箱允许为空
        rule_email(email, code_email_input, not_null=not_null_email, need_code=must_email)
    # 如果是本地用户更新的校验
    elif check_type == 'update' and user_type == 'local':
        # 邮箱和手机号至少填一个
        if not tel and not email:
            raise ZeroDivisionError("邮箱和手机号至少填写一个")
        rule_account(user_account)
        rule_displayname(user_displayname)
        # 这里用户有可能不修改手机号和邮箱, 所以不校验验证码格式
        rule_tel(tel, code_tel_input, not_null=False, need_code=False)
        # 邮箱允许为空
        rule_email(email, code_email_input, not_null=False, need_code=False)
    # 如果是ldap用户更新的校验
    elif check_type == 'update' and user_type == 'ldap':
        # 邮箱和手机号至少填一个
        if not tel and not email:
            raise ZeroDivisionError("邮箱和手机号至少填写一个")
        rule_account(user_account)
        rule_displayname(user_displayname)
        # 这里用户有可能不修改手机号和邮箱, 所以不校验验证码格式
        rule_tel(tel, code_tel_input, not_null=False, need_code=False)
        # 邮箱允许为空
        rule_email(email, code_email_input, not_null=False, need_code=False)
    # 如果是本地用户的登录校验
    elif check_type == 'login' and user_type == 'local':
        rule_account(user_account)
        rule_password(password)
    # 如果是本地用户的发送短信前校验
    elif check_type == 'sms' and user_type == 'local':
        # 这里不关联验证码
        rule_tel(tel, need_code=False)
        # 如果是本地用户的发送邮件前校验
    elif check_type == 'email' and user_type == 'local':
        # 这里不关联验证码
        rule_email(email, need_code=False)
    else:
        raise ZeroDivisionError("不支持的数据格式校验类型")