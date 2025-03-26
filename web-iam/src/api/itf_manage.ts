

// 后端返回的所有ldap搜索方案组
export type itfResLdapOus = {
    [key: string]: itfResLdapOu;
}
export interface itfResLdapOu {
    "as_account"?: string,
    "as_displayname"?: string,
    "as_email"?: string,
    "as_password"?: string,
    "as_tel"?: string,
    "can_login_directly"?: string,
    "description"?: string,
    "ou_base"?: string,
    "ou_id"?: number,
    "ou_name"?: string,
    "ou_search"?: string
}

// 请求已存在ldap方案组中有效用户的信息
export interface itfReqLdapOuUsers {
    "ou_name": string
}

// 后端返回ldap方案组中有效用户的信息列表
export interface itfResLdapOuUsers {
    users: {
        [key:string]: itfResLdapOuUser
    },
    attrs: itfResLdapAttrs
}

// 后端返回ldap方案组中有效的单个用户
export interface itfResLdapOuUser {
    "displayname": string,
    // 用户是否已被本系统收录
    "is_exists": boolean,
    "email": string,
    "tel": string,
    "account": string,
    "dn": string,
    "roles": Array<string>,
    "groups": Array<string>,
}

// 向后端请求批量添加ldap用户的所有用户信息
export interface itfReqAddLdapUsers {
    dict_user_info: {
        [key:string]: itfReqAddLdapUser
    }
}

// 向后端请求批量添加ldap用户的单个用户信息
export interface itfReqAddLdapUser {
    "ldap_ou_name": string,
    "account": string,
    "ldap_dn": string,
    "tel": string,
    "displayname": string,
    "status": "on"|"off",
    "roles": Array<string>,
    "groups": Array<string>,
    "email": string,
    is_exists?: boolean
}


//
export interface itfResLdapAttrs {
    "account"?: string,
    "displayname"?: string,
    "email"?: string,
    "password"?: string,
    "tel"?: string,
}

// 将后端返回的ldap用户对象整理为客供table展示的列表
export type itfTableLdapOuUsers = itfTableLdapOuUser[];
export interface itfTableLdapOuUser {
    [key:string]: string
}

// 向后端查询自己的信息时的结果
export interface itfmyInfo {
    "account": string,
    "befrom": "" | "local" | "ldap" | null,
    "date_create": string,
    "displayname": string,
    "email": string,
    "groups": Array<string>,
    "photo_base64": string,
    "rank": string,
    "roles": Array<string>,
    "tel": string,
    "containers": {
        [key:string]: Array<string>
    }
    "menus": {
        [key:string]: Array<string>
    }
}

// 后端返回的用户列表
export interface itfResUserList {
    [key:string]: itfResUserInfo
}

// 后端返回的单个用户信息
export interface itfResUserInfo {
    "account"?: string|null,
    "befrom"?: "ldap"|"local",
    "date_create"?: string|null,
    "date_latest_login"?: string|null,
    "date_update"?: string|null,
    "displayname"?: string|null,
    "email"?: string|null,
    "ldap_dn"?: string|null,
    "ldap_ou_name"?: string|null,
    "photo_id"?: string|null,
    "roles"?: Array<string>,
    "groups"?: Array<string>,
    "status"?: "on"|"off",
    "tel"?: string|null,
    "user_id"?: number,
    "is_online"?: boolean,
    password?:string|null
}

// 后端返回的单个用户信息
export interface itfShowUserInfo {
    "account"?: string|null,
    "befrom"?: "ldap"|"local",
    "date_create"?: string|null,
    "date_latest_login"?: string|null,
    "date_update"?: string|null,
    "displayname"?: string|null,
    "email"?: string|null,
    "ldap_dn"?: string|null,
    "ldap_ou_name"?: string|null,
    "photo_id"?: string|null,
    "roles"?: Array<string>,
    "groups"?: Array<string>,
    "status"?: "on"|"off",
    "tel"?: string|null,
    "user_id"?: number,
    password?:string|null
}

// 批量新增本地用户时的请求列表
export interface itfReqBatchUserCreateList {
    user_list: itfReqBatchUserCreate[]
}
// 批量新增本地用户时的单个用户信息
export interface itfReqBatchUserCreate {
    "account": string,
    "displayname": string,
    "password": string,
    "roles": Array<string>,
    "groups"?: Array<string>,
    "tel": string,
    "email": string,
    "status"?: "on"|"off",
}

// 后端返回的角色信息字典
export interface itfResRoleObj {
    [key:string]: itfResRole
}
// 后端返回的单个角色的id
export interface itfResRole {
    role_id: string,
    role_desc: string,
    date_create: string,
    date_update: string,
    webs: Array<{
        "web_name": string,
        "web_route": string,
        "web_desc": string
    }>,
    users: Array<{
        account: string,
        displayname: string,
    }>,
    groups: Array<{
        group_desc: string,
        group_id: string,
    }>,
    containers: Array<{
        "container_desc": string,
        "container_name": string,
        "web_name": string,
        "web_route": string
    }>,
    apis: Array<{
        api_endpoint: string,
        api_url: string,
    }>,

}

// 后端返回的组信息字典
export interface itfResGroupObj {
    [key:string]: itfResGroup
}
// 后端返回的单个组信息
export interface itfResGroup {
    group_id: string,
    group_desc: string,
    date_create: string,
    date_update: string,
    roles: Array<{
        role_id: string,
        role_desc: string,
    }>,
    users: Array<{
        account: string,
        displayname: string,
    }>
}

// 请求后端删除用户时的请求数据
export interface itfReqDelObj {
    user_list: itfReqDel[]
}

// 请求后端删除用户时的单个用户信息
export interface itfReqDel {
    "account": string,
    "befrom": "local"|"ldap"
}

// 请求后更新本地用户的请求数据
export interface itfReqUpdateObj {
    user_list: itfReqUpdate[]
}

// 请求后端更新本地用户时的单个用户信息
export interface itfReqUpdate {
    "account": string,
    "displayname": string,
    "tel": string,
    "status": "on"|"off",
    "roles": string|Array<string>,
    "groups"?: Array<string>,
    "befrom": string,
    "email": string
}

// 批量修改密码时的请求数据
export interface itfReqChangePasswdObj {
    user_list: itfReqChangePasswd[]
}
// 批量修改密码时单个用户的数据
export interface itfReqChangePasswd {
    "account": string,
    "password": string
}

// 向后端请求新建或更新单个用户组时的请求数据
export interface itfReqGroupAdd {
    "group_id": string,
    "group_desc": string,
    // roles: Array<{
    //     role_id: string,
    //     role_desc: string,
    // }>,
    // users: Array<{
    //     account: string,
    //     displayname: string,
    // }>
    roles: Array<string>,
    users: Array<string>,
}

// 后端返回的所有页面 - 对象
export interface itfResWebObj {
    [key:string]: itfResWeb
}

// 后端返回的单个页面
export interface itfResWeb {
    "container_list": itfResCtrObj,
    "date_create": string,
    "date_update": string,
    "web_desc": string,
    "web_id": number,
    "web_name": string,
    "web_route": string,
}

// 向后端请求新建单个web页
export interface itfReqWebAdd {
    "web_name": string,
    "web_route": string,
    "web_desc": string,
}

// 后端返回的单个web(页面)的所有container(展示块)
export interface itfResCtrObj {
    [key:string]: itfResCtr
}

// 后端返回的单个container(展示块)
export interface itfResCtr {
    "container_desc": string,
    "container_name": string,
    "date_create": string,
    "date_update": string
}

// 向后端请求新增指定web的多个container中的单个
export interface itfReqCtrAdd {
    "container_desc": string,
    "container_name": string,
}

// 向后端请求更新指定web的单个container
export interface itfReqCtrUpd {
    "web_route": string,
    "container_desc": string,
    "container_name": string,
}

// 向后端请求新增单个角色
export interface itfReqRoleAdd {
    "role_id": string,
    "role_desc": string,
    "groups": Array<string>,
    "users": Array<string>,
    "apis": Array<string>,
    "webs": Array<string>,
    "containers": Array<{
        "web_route": string,
        "container_name": string
    }>
}

// 后端返回的所有后端接口
export interface itfResApiObj {
    [key:string]: itfResApi
}

// 后端返回的单个后端接口
export interface itfResApi {
    "api_endpoint": string,
    "api_methods": string,
    "api_url": string,
    "date_create": string,
    "date_update": string,
    "interface_id": number
}