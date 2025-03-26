import {createRouter,createWebHistory, createWebHashHistory} from 'vue-router'
import login from '@/pages/auth/login.vue'
import passwd_forget from '@/pages/auth/passwd_forget.vue'
import singup from '@/pages/auth/singup.vue'
import Layout from '@/components/layout.vue'
import Test from '@/pages/test.vue'
import myInfo from '@/pages/manage/myInfo.vue'
import setting from '@/pages/manage/setting.vue'
import ldap_group from '@/pages/manage/ldap_group.vue'
import user_manage from '@/pages/manage/user_manage.vue'
import rbac_manage from '@/pages/manage/rbac_manage.vue'
import group_manage from '@/pages/manage/group_manage.vue'
import menu_manage from '@/pages/manage/menu_manage.vue'
import ldap_servers from '@/pages/devops/ldap_servers.vue'
import {userInfo} from "@/pinia/envs";
import type {Directive} from "vue";
// import {userInfo} from "@/pinia/envs";


const _router = [
    {
        // 自定义名字
        name:'ldap_servers',
        // 自定义路径
        path:'/home/ldapServers',
        // 引用的组件
        component:ldap_servers,
        meta: {
            title: "雪风-LDAP远程管理"
        },
    },
    {
        name: 'myInfo',
        path: '/home/myInfo',
        component: myInfo,
        meta: {
            title: "雪风-我的信息"
        },
    },
    {
        // 自定义名字
        name:'rbac_manage',
        // 自定义路径
        path:'/home/setting/rbac_manage',
        // 引用的组件
        component:rbac_manage,
        meta: {
            title: "雪风-角色管理"
        },
    },
    {
        // 自定义名字
        name:'user_manage',
        // 自定义路径
        path:'/home/setting/user_manage',
        // 引用的组件
        component:user_manage,
        meta: {
            title: "雪风-用户管理"
        },
    },
    {
        // 自定义名字
        name:'ldap_group',
        // 自定义路径
        path:'/home/setting/ldap_group',
        // 引用的组件
        component:ldap_group,
        meta: {
            title: "雪风-LDAP组管理"
        },
    },
    {
        // 自定义名字
        name:'group_manage',
        // 自定义路径
        path:'/home/setting/group_manage',
        // 引用的组件
        component:group_manage,
        meta: {
            title: "雪风-用户组管理"
        },
    },
    {
        // 自定义名字
        name:'menu_manage',
        // 自定义路径
        path:'/home/setting/menu_manage',
        // 引用的组件
        component:menu_manage,
        meta: {
            title: "雪风-菜单块管理"
        },
    },
]

// 定义一个路由器, history模式
const router_left = createRouter({
    history:createWebHistory(),
    routes:[
        // 这里定义的是默认展示的组件, 称为重定向
        {
            path:'/',
            redirect:'/home/ldapServers'
        },
        {
            name: 'App',
            path: '/home',
            component: Layout,
            // 页面信息
            children: [
                // {
                //     // 自定义名字
                //     name:'ldap_servers',
                //     // 自定义路径
                //     path:'/home/ldapServers',
                //     // 引用的组件
                //     component:ldap_servers,
                //     meta: {
                //         title: "雪风-LDAP远程管理"
                //     },
                // },
            ]
        },
        {
            name: 'singup',
            path: '/auth/singup',
            component: singup,
            meta: {
                title: "雪风-注册"
            },
        },
        {
            name: 'passwdForget',
            path: '/auth/passwdForget',
            component: passwd_forget,
            meta: {
                title: "雪风-忘记密码"
            },
        },
        {
            name: 'auth',
            path: '/auth/login',
            component: login,
            meta: {
                title: "雪风-登录"
            },
        },
        // {
        //     path: '/:catchAll(.*)',
        //     name: 'App',
        //     component: Layout,
        //     // 页面信息
        //     children: [
        //         {
        //             // 自定义名字
        //             name:'links',
        //             // 自定义路径
        //             path:'/home/links',
        //             // 引用的组件
        //             component:home,
        //             meta: {
        //                 title: "雪风-首页"
        //             },
        //         },
        //     ]
        // }
    ]
})

async function before_router() {
    // const _menu = Object.keys(user_info.menus)
    // const res_menu = await getServer('/api/manage/get/user/menus', {"ok": "ok"}) as {[key:string]: Array<string>}
    // console.log("路由表获取了一次权限信息", res_menu)
    let user_info = userInfo()
    let res_menu = user_info.menus
    console.log("路由表从pinia获取了一次权限信息", res_menu)
    const _menu = Object.keys(res_menu)
    // 定义白名单, 所有用户都强制有这个用户的权限
    const list_white_path_houduan = ['/', '/home/ldapServers']
    // console.log("获取到路由: ", _menu)
    const last_menu = _router.filter(item => {
        if (list_white_path_houduan.includes(item.path)) {
            return true
        } else {
            return _menu.includes(item.path)
        }
    })
    // 当前页面不在权限列表内则跳转到首页
    let list_white_path_qianduan = ['/auth/login', '/auth/passwdForget', '/auth/singup', '/', '/home/ldapServers']
    let last_menu_list = last_menu.map(item => item.path).concat(list_white_path_qianduan)
    // console.log("当前有权限的路由列表: ", last_menu_list)
    // console.log("当前取得的页面路径: ", window.location.pathname)
    if (!last_menu_list.includes(window.location.pathname)) {
        // console.log("触发了跳转: ", window.location.pathname)
        // router.push('/')
        window.location.replace('/')
    }

    console.log("生成有权限的路由: ", last_menu)
    // 这个add会导致router_left.options.routes里没有追加的新的路由信息, 但是不影响组件的加载
    router_left.addRoute({
        name: 'App',
        path: '/home',
        component: Layout,
        // 页面信息
        children: last_menu
    })

    // const _index = router_left.options.routes.findIndex(item => item.path === '/home')
    // router_left.options.routes[_index].children?.push(...last_menu)
    // router_left.addRoute(router_left.options.routes[_index])
    // console.log("路由表最终的权限信息", router_left)
}


declare module 'vue-router' {
    interface RouteMeta {
        title?: string
        icon?: string
    }
}

// 菜单块的显示判断
const per =  {
    async mounted(el, binding, vnode) {
        // 从pinia中获取到当前用户有权限的页面和html组件, 格式为{[key:string]: Array<string>}
        let user_info = userInfo()
        const res_menu = user_info.menus

        // console.log("判断指令时取到的menus: ", res_menu)
        // 获取当前所处的路径, 注意要确保router_left已被app.use了, 不然只能用window.location.pathname获取
        const cur_path = router_left.currentRoute.value.path
        // 获取指令的值
        const { value } = binding
        // 如果指令被定义了且不为空
        if (value && value.length > 0) {
            // 从pinia变量中获取当前页面的有权限的组件列表
            const permissionRoles = res_menu[cur_path] || []
            // 判断是否存在于权限列表中
            const hasPermission = permissionRoles.includes(value)
            if (!hasPermission) {
                // 不在则移除这个组件
                el.parentNode && el.parentNode.removeChild(el)
            }
        }
    }
} as Directive

// 将路由暴露出去
// export default router_left

export { router_left, per, before_router }