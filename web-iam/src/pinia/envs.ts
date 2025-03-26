// 引入defineStore用于创建store
import {defineStore} from 'pinia'
import {parseJWT} from '@/api/currency'
import {reactive, ref, type Ref, toRefs} from 'vue'
import type {res_jwt_payload, res_user_init} from '@/api/itf_auth'
import {getServer} from "@/api/def_servers";

// 定义并暴露一个store, 第一个参数是它的自定义名字, 第二个是功能函数
export const userInfo = defineStore('envs',() =>{

    // 触发从localstorage刷新jwt和头像到pinia
    function update_jwt(init:boolean=false) {
        let jwt = window.localStorage.getItem("yukikaze_user_jwt") || ""
        let payload:res_jwt_payload = parseJWT(jwt)

        if (!init) {
            id.value = payload.id
            account.value = payload.account
            displayname.value = payload.displayname
            roles.value = payload.roles
            groups.value = payload.groups
            email.value = payload.email
            tel.value = payload.tel
            befrom.value = payload.befrom
            user_photo.value = window.localStorage.getItem("yukikaze_user_photo") || ""
        }
        if (payload) {
            return reactive(payload)
        } else {
            return reactive({
                id: "",
                account: "",
                displayname: "",
                roles: [],
                groups: [],
                email: "",
                tel: "",
                befrom: "",
                user_photo: "",
            })
        }
    }

    let payload_tmp = update_jwt(true)

    let id:Ref<string> = ref(payload_tmp.id || "")
    let account:Ref<string> = ref(payload_tmp.account || "")
    let displayname:Ref<string> = ref(payload_tmp.displayname || "")
    let roles:Ref<Array<string>> = ref(payload_tmp.roles || [])
    let groups:Ref<Array<string>> = ref(payload_tmp.groups || [])
    let email:Ref<string> = ref(payload_tmp.email || "")
    let tel:Ref<string> = ref(payload_tmp.tel || "")
    let befrom = ref(payload_tmp.befrom) as Ref<'local'|'ldap'|''|null>
    let containers:Ref<{[key:string]: Array<string>}> = ref({})
    let menus:Ref<{[key:string]: Array<string>}> = ref({"zzzz": []})
    let aa:Ref<string> = ref('aaa')

    let user_photo = ref(window.localStorage.getItem("yukikaze_user_photo") || "")

    let inti_conf:res_user_init = {
        list_ous: [],
        must_email: true,
        must_tel: true,
        ldap_status: false,
    }

    // 更新test_1的值的函数
    function update_test_1(init:boolean=false) {
        let test_1_init = window.localStorage.getItem("test_1") || ""
        if (!init) {
            test_1.value = test_1_init
        } else {
            return test_1_init
        }
    }

    async function update_menus() {
        menus.value = await getServer('/api/manage/get/user/menus', {"ok": "ok"}) as {[key:string]: Array<string>}
        console.log("pinia做了一次更新")
    }

    let test_1 = ref(update_test_1(true))
    // 对外暴露哪些变量, 需要注意, 如果不是响应式(ref, reactive)的, 则外面读取不到
    return {
        id, account, displayname, roles, groups, email, tel, befrom, update_jwt, test_1, update_test_1, user_photo, aa,
        containers, menus, inti_conf, update_menus
    }
})
