// import { createPinia } from 'pinia'
import {userInfo} from "@/pinia/envs";
import {router_left} from "@/router/router"
import type {Directive, App} from "vue";



const per =  {

    mounted(el, binding, vnode) {

        // const pinia = createPinia()
        let user_info = userInfo()
        const menu = user_info.menus
        console.log("判断指令时取到的menus: ", menu)

        const cur_path = router_left.currentRoute.value.path
        const { value } = binding
        if (value && value.length > 0) {
            const permissionRoles = menu[cur_path] || []
            const hasPermission = permissionRoles.includes(value)
            if (!hasPermission) {
                el.parentNode && el.parentNode.removeChild(el)
            }
        }
    }
} as Directive
const dir = {
    install(app: App) {
        app.directive('dcj', per)
    }
}
export {
    per
}