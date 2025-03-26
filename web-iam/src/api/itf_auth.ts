
// 通用操作成功的返回信息
export interface res_ok {
    ok: "ok"|'no'
}

// 获取用户相关的初始化信息 /api/user/init
export interface res_user_init {
    "list_ous": Array<string>
    "must_email": boolean,
    "must_tel": boolean,
    "ldap_status": boolean,
    "forget_passwd_ldap": boolean,
    "ldap_modify_oneself": boolean,
    "image_auth"?: string,
}

// 查看本地用户是否有邮箱和手机号 /api/user/check/telEmail
export interface res_check_telEmail {
    "email_vague": string|null,
    "tel_vague": string|null,
}

// 登录返回信息 /api/user/login
export interface res_login {
    "res_jwt": string,
    "user_photo_base64": string,
    "user_info": {
        "account": string,
        "befrom": string,
        "displayname": string,
        "email": string,
        "exp": number,
        "id": number,
        "role_id": string,
        "tel": string
    }
}

// 登录请求信息 /api/user/login
export interface req_login {
    user_account: string,
    user_password: string,
    user_type: 'local'|'ldap',
    sign_type: 'passwd'|'sms',
    ou_name?: string
}

// 注册时的请求信息 /api/user/signup
export interface req_singup {
    "user_photo_base64": null|string,
    "user_account": string,
    "user_displayname": string,
    "password": string,
    "password_1": string,
    "tel": string,
    "email": string,
    "code_tel_input": string,
    "code_email_input": string,
    "user_type": 'local'|'ldap'
}

// 只更新用户头像时的请求信息
export interface req_photo_update {
    "user_account": string,
    "user_type": 'local'|'ldap'|''|null,
    "user_photo_base64": string|null|undefined
}

// jwt中payload的参数
export interface res_jwt_payload {
    "id": string,
    "account": string,
    "displayname": string,
    "roles": Array<string>,
    "groups": Array<string>,
    "email": string,
    "tel": string,
    "befrom": 'local'|'ldap'|''|null,
}

// 更新本地用户个人信息时的请求信息 (不含头像和密码)
export interface req_update_userinfo {
    user_account: string,
    user_displayname: string,
    tel: string,
    email: string,
    code_tel_input: string,
    code_email_input: string,
    user_type: 'local'|'ldap'|''|null
}

// 更新本地用户密码时的请求信息
export interface req_update_passwd {
    "user_account": string,
    "user_password_old": string,
    "user_password_new": string,
    user_type: 'local'|'ldap'|''|null
}


