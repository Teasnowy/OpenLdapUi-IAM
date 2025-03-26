import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import { createPinia } from 'pinia'
import './permission.js'
import {userInfo} from "@/pinia/envs";
import {router_left, per, before_router } from '@/router/router'

const app = createApp(App)
// 引入全局变量
const pinia = createPinia()

// 修改支持中文
app.use(ElementPlus, {
    locale: zhCn,
})

// 引用全局变量
app.use(pinia)
// 引用页面左侧路由
// import {router_left, per, before_router } from '@/router/router'

// before_router()
// import { per } from './directive/permission'

// import {userInfo} from "@/pinia/envs";
let user_info = userInfo()
// 先挂载动态路由再use
user_info.update_menus().then(()=>{
    console.log("main")
    before_router().then(()=>{
        app.directive('dcj', per)
        app.use(router_left)
        app.mount('#app')
    }).catch(()=>{})

}).catch(()=>{})

export { app }

