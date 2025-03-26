# ldap登录和管理相关接口
from flask import Blueprint, request
from ..db import ldap_general
from ..data_format import interface_try
from ..user import ldap_manage


routes_ldap = Blueprint('routes_ldap', __name__)


@routes_ldap.route('/api/user/ldap/ous/manage/check', methods=['post'], endpoint="LDAP-获取所有ldap组")
def ldap_manage_check():
    """
    获取所有ldap搜索模板
    """
    data_result = interface_try(ldap_manage.ous_check, request,)
    return data_result


@routes_ldap.route('/api/user/ldap/ous/manage/create', methods=['post'], endpoint="LDAP-新建LDAP组")
def ldap_manage_create():
    """
    新建ldap搜索模板
    """
    data_result = interface_try(ldap_manage.ous_create, request,)
    return data_result


@routes_ldap.route('/api/user/ldap/ous/manage/update', methods=['post'], endpoint="LDAP-更新LDAP组")
def ldap_manage_update():
    """
    更新ldap搜索模板
    """
    data_result = interface_try(ldap_manage.ous_update, request,)
    return data_result


@routes_ldap.route('/api/user/ldap/ous/manage/delete', methods=['post'], endpoint="LDAP-删除LDAP组")
def ldap_manage_delete():
    """
    删除ldap搜索模板
    """
    data_result = interface_try(ldap_manage.ous_delete, request, )
    return data_result


@routes_ldap.route('/api/user/ldap/ous/manage/searchTmp', methods=['post'], endpoint="LDAP-搜索临时LDAP组的用户")
def ldap_manage_search_tmp():
    """
    依靠临时提供的ldap搜索方案来获取其中的用户及用户信息
    """
    data_result = interface_try(ldap_manage.ous_search_tmp, request,)
    return data_result


@routes_ldap.route('/api/user/ldap/ous/manage/searchExists', methods=['post'], endpoint="LDAP-搜索指定LDAP组的用户")
def ldap_manage_search_exists():
    """
    依靠数据库中已存在的ldap搜索方案模板的名字来获取其中的用户及用户信息
    """
    data_result = interface_try(ldap_manage.ous_search_exists, request,)
    return data_result


@routes_ldap.route('/api/user/ldap/login', methods=['post'], endpoint="LDAP-登录(已废弃)")
def ldap_user_login():
    """
    ldap用户登录(已废弃, 改为统一登录接口)
    """
    data_result = interface_try(ldap_general.ldap_try_bind, request, is_jwt=False)
    return data_result


@routes_ldap.route('/api/user/ldap/ous/manage/useradd', methods=['post'], endpoint="LDAP-批量导入用户")
def ldap_manage_user_add():
    """
    添加ldap用户
    """
    data_result = interface_try(ldap_manage.ous_user_add, request, )
    return data_result


@routes_ldap.route('/api/user/ldap/ous/manage/userdel', methods=['post'], endpoint="LDAP-删除单个用户")
def ldap_manage_user_del():
    """
    删除单个ldap用户
    """
    data_result = interface_try(ldap_manage.ous_user_del, request,)
    return data_result


@routes_ldap.route('/api/user/ldap/ous/manage/ldapattrs', methods=['post'], endpoint="LDAP-获取openldap所有属性")
def ldap_ldap_attrs():
    """
    获取ldap服务器中所有属性列表
    """
    data_result = interface_try(ldap_manage.get_ldap_attrs, request,)
    return data_result
