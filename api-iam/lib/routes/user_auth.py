# 用户登录和鉴权类接口
import time
from flask import Blueprint, request
from ..data_format import interface_try
from ..user import sign_up
from ..user import login
from ..user import update
from ..user import user_freeze
from ..user import code_send


routes_user_auth = Blueprint('routes_user_auth', __name__)


@routes_user_auth.route('/api/user/init', methods=['post'], endpoint="本地用户-获取初始配置")
def user_init():
    """
    登录注册或更新用户信息时获取的初始信息
    """
    data_result = interface_try(login.get_init, request, is_jwt=False)
    return data_result


@routes_user_auth.route('/api/sms/send/code', methods=['post'], endpoint="通用-对手机号发送验证码")
def sms_send_code():
    """
    发送手机验证码
    """
    data_result = interface_try(code_send.tel_code_send, request, is_jwt=False)
    return data_result


@routes_user_auth.route('/api/email/send/code', methods=['post'], endpoint="通用-对邮箱发送验证码")
def email_send_code():
    """
    发送邮箱证码
    """
    data_result = interface_try(code_send.email_code_send, request, is_jwt=False)
    return data_result


@routes_user_auth.route('/api/user/signup', methods=['post'], endpoint="本地用户-注册")
def user_sign_up():
    """
    本地用户注册接口
    :return:
    """
    data_result = interface_try(sign_up.entry, request, is_jwt=False)
    return data_result


@routes_user_auth.route('/api/user/login', methods=['post'], endpoint="所有用户-登录")
def user_login():
    """
    用户登录接口(兼容ldap用户)
    """
    data_result = interface_try(login.entry, request, is_jwt=False)
    return data_result


@routes_user_auth.route('/api/user/logout', methods=['post'], endpoint="所有用户-注销")
def user_logout():
    """
    用户登录接口(兼容ldap用户)
    """
    data_result = interface_try(login.logout, request, is_jwt=False)
    return data_result


@routes_user_auth.route('/api/user/update/info/local', methods=['post'], endpoint="本地用户-更新个人信息")
def user_update_info_local():
    """
    本地用户更新个人信息接口
    """
    data_result = interface_try(update.entry, request)
    return data_result


@routes_user_auth.route('/api/user/update/photo', methods=['post'], endpoint="所有用户-上传头像")
def user_update_photo():
    """
    用户更新头像
    """
    data_result = interface_try(update.update_photo, request)
    return data_result


@routes_user_auth.route('/api/user/update/passwd/local/useold', methods=['post'], endpoint="本地用户-旧密码更新密码")
def user_update_passwd_local_old():
    """
    本地用户更新密码接口, 通过旧密码方式
    """
    data_result = interface_try(update.update_password_useold, request)
    return data_result


@routes_user_auth.route('/api/user/update/passwd/local/usetel', methods=['post'], endpoint="本地用户-短信重置密码")
def user_update_passwd_local_tel():
    """
    本地用户更新密码接口, 通过短信验证码
    """
    data_result = interface_try(update.update_password_local_sms, request, is_jwt=False)
    return data_result


@routes_user_auth.route('/api/user/update/passwd/local/useemail', methods=['post'], endpoint="本地用户-邮箱重置密码")
def user_update_passwd_local_email():
    """
    本地用户更新密码接口, 通过邮箱验证码
    """
    data_result = interface_try(update.update_password_local_email, request, is_jwt=False)
    return data_result


@routes_user_auth.route('/api/user/delete/local', methods=['post'], endpoint="本地用户-删除")
def user_delete_local():
    """
    本地用户删除
    """
    data_result = interface_try(update.update_password_local_useold, request)
    return data_result


@routes_user_auth.route('/api/user/freeze/local', methods=['post'], endpoint="本地用户-冻结")
def user_freeze_local():
    """
    本地用户冻结
    """
    data_result = interface_try(user_freeze.freeze, request)
    return data_result


@routes_user_auth.route('/api/user/unfreeze/local', methods=['post'], endpoint="本地用户-解冻")
def user_unfreeze_local():
    """
    本地用户解冻
    """
    data_result = interface_try(user_freeze.unfreeze, request)
    return data_result


@routes_user_auth.route('/api/user/check/telEmail', methods=['post'], endpoint="本地用户-获取邮箱和手机")
def user_check_telemail():
    """
    查看本地用户是否有邮箱和手机号
    """
    # time.sleep(5)
    data_result = interface_try(code_send.check_tel_email, request, is_jwt=False)
    return data_result


@routes_user_auth.route('/api/fromuser/email/send/code', methods=['post'], endpoint="本地用户-通过账号发送邮箱验证码")
def user_fromuser_email():
    """
    本地用户通过账户名发送邮箱验证码
    """
    data_result = interface_try(code_send.email_code_send_account, request, is_jwt=False)
    return data_result


@routes_user_auth.route('/api/fromuser/sms/send/code', methods=['post'], endpoint="本地用户-通过账号发送短信验证码")
def user_fromuser_sms():
    """
    本地用户通过账户名发送短信验证码
    """
    time.sleep(5)
    data_result = interface_try(code_send.tel_code_send_account, request, is_jwt=False)
    return data_result



