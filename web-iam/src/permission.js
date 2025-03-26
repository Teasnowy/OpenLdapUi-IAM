import {router_left} from '@/router/router'
const whiteList = [
    '/auth/login',
    '/auth/singup',
    "/auth/passwdForget",
    "/home/ldapServers",
    '/',
]

// 限制没有jwt时能跳转的页面
export default router_left.beforeEach((to, from, next) => {
    document.title = to.meta.title || '雪风';
    const _path = to.path
    // console.log('当前路径: ', _path)
    if (whiteList.includes(_path)) {
        // 在白名单就无条件跳转
        next()
    } else {
        // 不在白名单, 就要看看是否有jwt
        const _token = localStorage.getItem('yukikaze_user_jwt')
        if (_token) {
            // 有则正常跳转
            next()
        } else {
            // 如果没有jwt, 就说明没有登录, 跳转至登录页
            next('/auth/login')
        }
    }
})