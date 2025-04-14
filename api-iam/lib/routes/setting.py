# 管理类接口, 包括用户, 权限, 组等
import time
from flask import Blueprint, request
from ..data_format import interface_try
from ..crontab import crontab
from ..manage import user_manage, rbac_manage, group_manage, menu_manage


routes_setting = Blueprint('routes_setting', __name__)


@routes_setting.route('/api/manage/get/user/all', methods=['post'], endpoint="管理-获取所有用户的信息")
def get_user_all():
    """
    获取所有用户的详细信息(不含密码和头像), 包括ldap和本地用户
    """
    # time.sleep(5)
    data_result = interface_try(user_manage.get_user_all, request, )
    return data_result


@routes_setting.route('/api/manage/get/user/my', methods=['post'], endpoint="管理-自己的信息")
def get_myinfo():
    """
    获取自己的详细信息(不含密码, 含头像)
    """
    # time.sleep(5)
    data_result = interface_try(user_manage.get_myinfo, request)
    return data_result


@routes_setting.route('/api/manage/get/user/menus', methods=['post'], endpoint="管理-自己的前端权限")
def get_my_menus():
    """
    获取自己的详细信息(不含密码, 含头像, 不能校验jwt)
    """
    # time.sleep(5)
    data_result = interface_try(user_manage.get_my_menus, request, is_jwt=False)
    return data_result


@routes_setting.route('/api/manage/create/user/batch', methods=['post'], endpoint="管理-批量新建本地用户")
def user_create_batch():
    """
    批量新建本地用户
    """
    # time.sleep(5)
    data_result = interface_try(user_manage.create_batch, request,)
    return data_result


@routes_setting.route('/api/manage/delete/user/batch', methods=['post'], endpoint="管理-批量删除用户")
def user_delete_batch():
    """
    批量删除用户(包括ldap)
    """
    # time.sleep(2)
    # raise ZeroDivisionError("后端出错了")
    data_result = interface_try(user_manage.delete_batch, request,)
    return data_result


@routes_setting.route('/api/manage/freeze/user/batch', methods=['post'], endpoint="管理-批量修改用户状态")
def user_freeze_batch():
    """
    批量修改用户状态 (on或off)
    """
    # time.sleep(2)
    # raise ZeroDivisionError("后端出错了")
    data_result = interface_try(user_manage.freeze_batch, request,)
    return data_result


@routes_setting.route('/api/manage/update/user/batch', methods=['post'], endpoint="管理-批量修改本地用户")
def user_update_batch():
    """
    批量修改本地用户
    """
    # time.sleep(2)
    # raise ZeroDivisionError("后端出错了")
    data_result = interface_try(user_manage.update_batch, request, )
    return data_result


@routes_setting.route('/api/manage/changepasswd/user/batch', methods=['post'], endpoint="管理-批量重置本地用户的密码")
def user_changepasswd_batch():
    """
    批量重置本地用户的密码
    """
    # time.sleep(5)
    data_result = interface_try(user_manage.changepasswd_batch, request,)
    return data_result


@routes_setting.route('/api/group/get', methods=['post'], endpoint="管理-获取用户组")
def group_get():
    """
    获取用户组
    """
    # time.sleep(5)
    data_result = interface_try(group_manage.group_get, request)
    return data_result


@routes_setting.route('/api/group/create', methods=['post'], endpoint="管理-新增用户组")
def group_create():
    """
    新增用户组
    """
    # time.sleep(5)
    data_result = interface_try(group_manage.group_create, request)
    return data_result


@routes_setting.route('/api/group/update', methods=['post'], endpoint="管理-更新用户组")
def group_update():
    """
    更新用户组
    """
    # time.sleep(5)
    data_result = interface_try(group_manage.group_update, request)
    return data_result


@routes_setting.route('/api/group/delete', methods=['post'], endpoint="管理-删除用户组")
def group_delete():
    """
    删除用户组
    """
    # time.sleep(5)
    data_result = interface_try(group_manage.group_delete, request)
    return data_result


@routes_setting.route('/api/manage/get/role_id/all', methods=['post'], endpoint="管理-获取所有角色id的列表")
def get_role_id_all():
    """
    获取所有角色id的列表形式
    """
    # time.sleep(5)
    data_result = interface_try(user_manage.get_role_id_all, request,)
    return data_result


@routes_setting.route('/api/manage/get/role/dict', methods=['post'], endpoint="管理-获取所有角色id的dict")
def get_role_dict():
    """
    获取所有角色id的字典形式
    """
    # time.sleep(5)
    data_result = interface_try(rbac_manage.get_dict_new, request,)
    return data_result


@routes_setting.route('/api/manage/role/create', methods=['post'], endpoint="管理-新建单个角色")
def role_create():
    """
    新建单个角色
    """
    # time.sleep(5)
    data_result = interface_try(rbac_manage.create_role, request,)
    return data_result


@routes_setting.route('/api/manage/role/update', methods=['post'], endpoint="管理-更新单个角色")
def role_update():
    """
    更新单个角色
    """
    # time.sleep(5)
    data_result = interface_try(rbac_manage.update_role, request,)
    return data_result


@routes_setting.route('/api/manage/role/delete', methods=['post'], endpoint="管理-删除单个角色")
def role_delete():
    """
    删除单个角色
    """
    # time.sleep(5)
    data_result = interface_try(rbac_manage.delete_role, request,)
    return data_result


@routes_setting.route('/api/manage/web/get/dict', methods=['post'], endpoint="管理-获取所有的web页面和展示块")
def web_get_dict():
    """
    获取所有web页面及其所属的前端展示块
    """
    # time.sleep(5)
    data_result = interface_try(menu_manage.get_dict, request,)
    return data_result


@routes_setting.route('/api/manage/web/create', methods=['post'], endpoint="管理-创建一个web页面")
def web_create():
    """
    创建一个web页面的信息
    """
    # time.sleep(5)
    data_result = interface_try(menu_manage.create_web, request,)
    return data_result


@routes_setting.route('/api/manage/web/update', methods=['post'], endpoint="管理-更新指定web页面的信息")
def web_update():
    """
    更新一个web页面的信息
    """
    # time.sleep(5)
    data_result = interface_try(menu_manage.update_web, request,)
    return data_result


@routes_setting.route('/api/manage/web/delete', methods=['post'], endpoint="管理-删除一个web页面")
def web_delete():
    """
    删除一个web页面
    """
    # time.sleep(5)
    data_result = interface_try(menu_manage.delete_web, request,)
    return data_result


@routes_setting.route('/api/manage/containers/create', methods=['post'], endpoint="管理-批量创建指定web页面的前端展示块")
def containers_create():
    """
    在指定的web页面批量创建展示块
    """
    # time.sleep(5)
    data_result = interface_try(menu_manage.create_containers, request,)
    return data_result


@routes_setting.route('/api/manage/container/update', methods=['post'], endpoint="管理-更新指定web页面的前端展示块")
def containers_update():
    """
    更新指定web页面的前端单个展示快
    """
    # time.sleep(5)
    data_result = interface_try(menu_manage.update_container, request,)
    return data_result


@routes_setting.route('/api/manage/containers/delete', methods=['post'], endpoint="管理-批量删除指定web页面的前端展示块")
def containers_delete():
    """
    批量删除指定web页面的前端展示块
    """
    # time.sleep(5)
    data_result = interface_try(menu_manage.delete_container, request,)
    return data_result


@routes_setting.route('/api/manage/interface/get/dict', methods=['post'], endpoint="管理-获取所有后端接口")
def interface_get():
    """
    批量删除指定web页面的前端展示块
    """
    # time.sleep(5)
    data_result = interface_try(crontab.get_routes, request,)
    return data_result