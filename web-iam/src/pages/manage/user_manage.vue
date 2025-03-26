<script setup lang="ts">
  import {computed, reactive, type Ref, ref} from 'vue'
  import {type LocationQueryValue, useRoute, useRouter} from 'vue-router'
  import type {
    itfResUserList, itfResUserInfo, itfReqBatchUserCreateList, itfReqBatchUserCreate, itfResRoleObj, itfResRole,
    itfReqDelObj, itfReqDel, itfReqUpdateObj, itfReqUpdate, itfShowUserInfo, itfReqChangePasswdObj, itfReqChangePasswd,
    itfResLdapOus, itfResLdapOu, itfResLdapOuUsers, itfResLdapOuUser, itfReqAddLdapUsers, itfReqAddLdapUser, itfResGroup
  } from '@/api/itf_manage'
  import type {res_user_init} from '@/api/itf_auth'
  import {Edit, CirclePlus, RefreshRight, ArrowLeftBold} from '@element-plus/icons-vue'
  import {userInfo} from "@/pinia/envs";
  import {global_window} from '@/api/def_feedback'
  import {getServer} from '@/api/def_servers'


  let route = useRoute();
  let router = useRouter()
  // 初始化全局变量
  let user_info = userInfo()

  // 面包屑标识展示哪些卡片的变量
  let select_breadcrumb:Ref<string> = ref("users")
  // 当前被选定的用户id
  let select_user_id:Ref<number> = ref(0)
  // 当前被选定的用户account
  let select_user_account:Ref<string> = ref("")
  // 当前被选定的用户详细信息
  let select_user:Ref<itfShowUserInfo> = ref({})
  // 单个用户的编辑状态
  let status_user_edit:Ref<boolean> = ref(false)
  // 新建或修改用户时的默认权限
  let role_delault = '访客'
  // 单个用户的修改密码状态
  let status_user_passwd:Ref<boolean> = ref(false)
  // 存储单个用户的密码
  let data_user_passwd:Ref<string> = ref("")
  // 后端返回的所有权限信息
  let data_res_role_info:Ref<itfResRoleObj> = ref({})
  // 将权限信息转为列表
  let data_role_list:Ref<itfResRole[]> = ref([])
  // 后端返回的组信息
  let data_res_group_list:Ref<itfResGroup[]> = ref([])
  // 存储当前所有用户信息, 实际上是个对象, 不是列表
  let data_res_user_info:Ref<itfResUserList> = ref({})
  // 将data_res_user_info 转为列表, 便于用table直接展示, 因为table引用Object.values()过的数据会导致无法勾选
  let data_user_list:Ref<itfResUserInfo[]> = ref([])
  // 存储被选中的用户详细信息列表
  let select_user_list:Ref<itfResUserInfo[]> = ref([])
  // 刷新用户列表的按钮的加载状态
  let status_btn_users_get:Ref<boolean> = ref(false)
  // 批量删除用户的确认弹框状态
  let status_win_users_delete:Ref<boolean> = ref(false)
  // 批量删除用户的按钮的加载状态
  let status_btn_users_delete:Ref<boolean> = ref(false)
  // 批量修改用户的修改框状态
  let status_win_users_update:Ref<boolean> = ref(false)
  // 批量修改用户的按钮的加载状态
  let status_btn_users_update:Ref<boolean> = ref(false)
  // 批量创建用户的弹窗状态
  let status_win_users_create:Ref<boolean> = ref(false)
  // 批量创建用户的按钮的加载状态
  let status_btn_users_create:Ref<boolean> = ref(false)
  // 批量重置密码的弹窗状态
  let status_win_users_changepasswd:Ref<boolean> = ref(false)
  // 批量重置密码的按钮的状态
  let status_btn_users_changepasswd:Ref<boolean> = ref(false)
  // 存储批量创建的用户信息的列表
  let batch_user_create:Ref<itfReqBatchUserCreateList> = ref({user_list: []})
  // 批量删除用户时的请求信息
  let batch_user_delete:Ref<itfReqDelObj> = ref({user_list:[]})
  // 批量修改用户时的请求信息
  let batch_user_update:Ref<itfReqUpdateObj> = ref({user_list:[]})
  // 用户输入的同一修改为的密码
  let input_batch_passwd:Ref<string> = ref("")
  // 批量修改密码时的请求信息
  let batch_user_changepasswd:Ref<itfReqChangePasswdObj> = ref({user_list:[]})

  // ldap搜索组的信息
  let data_res_ous:Ref<itfResLdapOus> = ref({})
  // 获取ldap搜索组按钮的状态
  let status_btn_ous:Ref<boolean> = ref(false)
  // 当前选定的ldap搜索组的值
  let select_ous_name:Ref<string> = ref("")
  // ldap搜索框的弹出状态
  let status_win_ldap_search:Ref<boolean> = ref(false)
  // ldap用户搜索的按钮状态
  let status_btn_ldap_search:Ref<boolean> = ref(false)
  // 后端返回的ldap用户搜索结果
  let data_res_ldapUsers:Ref<itfResLdapOuUsers> = ref({users:{},attrs:{}})
  // 勾选中的ldap用户
  let select_ldapUser_list:Ref<itfReqAddLdapUser[]> = ref([])
  // 将后端返回的ldap用户转为列表, 供table展示
  let data_ldapUsers_list:Ref<itfReqAddLdapUser[]> = ref([])
  // 初始化的后端配置信息
  let data_req_conf:res_user_init = {
    list_ous: [],
    must_email: true,
    must_tel: true,
    ldap_status: true,
    forget_passwd_ldap: false,
    ldap_modify_oneself: false,
  }

  // 从后端初始化信息
  def_init().then(()=>{
    if (data_req_conf.ldap_status) {
      // 如果后端开启了ldap, 立即初始化一次ldap搜索组信息
      def_get_ous()
    }
  }).catch(()=>{})
  // 立刻初始化一次用户列表
  def_get_users()
  // def_get_users().then(()=>{
  //   to_userinfo()
  // }).catch()
  // 立刻初始化一次批量新增用户时的数据
  def_init_user_create()






  // 用户展示列表的选择列
  // const selectable = (row: itfResUserInfo) => [].includes(row.user_id)

  let input_search_user:Ref<string> = ref("")
  // 筛选用户的计算函数
  const filter_show_user = computed(() =>
      data_user_list.value.filter(
          (data:itfResUserInfo) =>
              (!input_search_user.value || data.account!.toLowerCase().includes(input_search_user.value.toLowerCase())) ||
              (!input_search_user.value || data.displayname!.toLowerCase().includes(input_search_user.value.toLowerCase()))
          // console.log(select_date_work.value, data.date_work)
      )
  )

  // 修改url的query中account的函数
  function def_change_query_account(account:string="") {
    let tmp_query: { [key: string]: string | undefined } = { ...route.query, account: account}
    // 如果为空则删除这个account
    if (!account) {
      delete tmp_query.account
    }
    // push会被记录到浏览器历史记录, replace不会
    router.push({path: route.path, query: tmp_query})
  }

  // 获取初始化信息
  async function def_init() {
    let res_init:any = await getServer('/api/user/init', {"ok": 'ok'})
    data_req_conf = res_init as res_user_init
  }

  // 获取所有用户的列表和权限信息
  async function def_get_users() {
    status_btn_users_get.value = true
    let tmp_status_user = false
    let tmp_status_group = false
    // 获取所有用户的列表
    await getServer("/api/manage/get/user/all", {"ok":"ok"}).then((res)=>{
      data_res_user_info.value = res as itfResUserList
      // tmp_list = Object.values(unref(data_res_user_info))
      console.log("data_res_user_info: ", data_res_user_info.value)
      data_user_list.value = Object.values(data_res_user_info.value)
      // 如有account参数则跳转
      to_userinfo()
      tmp_status_user = true
    }).catch((err)=>{
    })

    if (tmp_status_user) {
      // 同时获取一次权限信息
      await getServer("/api/manage/get/role_id/all", {"ok":"ok"}).then((res)=>{
        data_role_list.value = res as itfResRole[]
        tmp_status_group = true
      }).catch((err)=>{
      })
    }

    if (tmp_status_group) {
      // 同时获取一次组信息
      await getServer("/api/group/get", {"ok":"ok"}).then((res)=>{
        data_res_group_list.value = res as itfResGroup[]
      }).catch((err)=>{
      })
    }
    status_btn_users_get.value = false
    // console.log("立刻初始化一次用户列表: ", data_res_user_info.value)
  }

  // 检测url中是否传入了account参数, 有则跳转至该用户详情页
  function to_userinfo() {
    let query_account:string | null | LocationQueryValue[] = route.query.account
    // console.log("url中带有参数: ", query_account)
    if (query_account && typeof query_account == 'string') {
      // console.log("识别query_account类型: ", typeof query_account, data_res_user_info.value)
      if (Object.keys(data_res_user_info.value).includes(query_account)) {
        // console.log("触发进入用户详情页: ", query_account)
        def_user_detail(data_res_user_info.value[query_account])
      }
    }
  }

  // 后端传来的时间格式转换为 YY-mm-DD HH:mm:ss
  function def_fromat_date(d:string) {
    if (!d) {
      return "未定义"
    }
    let date = new Date(d)
    // 使用 Intl.DateTimeFormat 格式化日期，并转换到 Asia/Shanghai 时区
    const options:any = {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZone: 'Asia/Shanghai',
      hour12: false  // 24小时制
    };

    const formatter = new Intl.DateTimeFormat('zh-CN', options);
    return formatter.format(date);
  }

  // // 用户列表多选时触发的动作
  function user_select_changed(val: itfResUserInfo[]){
    // select_user_list = reactive([])
    console.log("对多选列表赋值")
    select_user_list.value = val
  }
  // 判断哪些用户不能勾选
  const selectable = (row: itfResUserInfo) => !['admin'].includes(row.account!)

  // // 导入ldap用户列表多选时触发的动作
  function ldapUser_select_changed(val: itfReqAddLdapUser[]){
    // select_user_list = reactive([])
    console.log("对ldap多选列表赋值")
    // 这里不能对val做二次引用处理, 当勾选后表内的input框再次改动, 就无法同步修改select_ldapUser_list
    // val.forEach((i)=>{
    //
    // })
    select_ldapUser_list.value = val
  }

  // 判断导入ldap用户时哪些不可被勾选 (已存在的不可被勾选)
  let selectable_ldap= (row: itfReqAddLdapUser) => !row.is_exists


  // 点击单个用户名或详情按钮时的操作
  function def_user_detail(user_info:itfResUserInfo) {
    select_breadcrumb.value = 'detail'
    // 这里要用深度复制
    select_user.value = {...user_info}
    // role_id转为列表
    select_user_id.value = select_user.value.user_id!
    select_user_account.value = select_user.value.account!
    // 给密码一个初始值
    // select_user.value["password"] = ""
    // 更新页面中可能存在的account参数
    def_change_query_account(select_user_account.value)
  }

  // 返回用户列表按钮的函数
  function def_user_list() {
    def_change_query_account()
    select_breadcrumb.value = 'users'
  }

  // 取消单个用户更改的函数
  function def_user_cancel_edit() {
    // 把密码修改也取消掉
    def_user_cancel_passwd()
    // 取消修状态
    status_user_edit.value = false
    // 还原数据, 这里要用深度赋值
    // select_user.value = {...data_res_user_info.value[select_user_id.value]}
    select_user.value = {...data_res_user_info.value[select_user_account.value]}
  }
  // 取消修改单个用户密码的操作
  function def_user_cancel_passwd() {
    // 取消修状态
    status_user_passwd.value = false
    // 还原数据
    data_user_passwd.value = ""
  }

  // 初始化新建用户表单数据的函数(初始化为一个空白行)
  function def_init_user_create() {
    batch_user_create.value = {
      user_list: [{
        "account": "",
        "displayname": "",
        "password": "",
        "roles": [role_delault],
        "groups": [],
        "tel": "",
        "email": "",
        "status": "on"
      }]
    }
  }

  // 点击单个用户克隆按钮时的操作
  function def_user_clone(user_info:itfResUserInfo) {
    batch_user_create.value = {
      user_list: [{
        "account": "",
        "displayname": "",
        "password": "",
        "roles": user_info.roles!,
        "groups": user_info.groups!,
        "tel": user_info.tel!,
        "email": user_info.email!,
        "status": user_info.status!
      }]
    }
    status_win_users_create.value = true
  }

  // 批量新建多个本地用户的函数
  async function def_user_batch_create() {
    status_btn_users_create.value = true
    await getServer("/api/manage/create/user/batch", batch_user_create.value).then((res)=>{
      global_window("success", "新增用户成功")
      // 清空请求数据
      def_init_user_create()
      // 立即刷新一次数据
      def_get_users()
      status_win_users_create.value = false
    }).catch(()=>{
    })
    status_btn_users_create.value = false

  }

  // 批量新建多个本地用户时新增一行空白数据
  function def_batch_add_new() {
    let tmp_line:itfReqBatchUserCreate = {
      "account": "",
      "displayname": "",
      "password": "",
      "roles": [role_delault],
      "groups": [],
      "tel": "",
      "email": "",
      "status": "on"
    }
    batch_user_create.value.user_list.push(tmp_line)
  }

  // 点击删除按钮触发弹窗时的函数
  function def_before_delete(data:itfResUserInfo={}) {
    if (data.account=='admin') {
      global_window("error", "不能对管理员做这个操作")
      return
    }
    batch_user_delete.value.user_list = []
    // 如果有传参就说明只删除指定用户
    if (Object.keys(data).length > 0) {
      // console.log("单个删除")
      // 这里使用深度复制
      let d = {...data}
      batch_user_delete.value.user_list = [{
        account: d.account!,
        befrom: d.befrom!
      }]
      // vs = d.account!
    } else {
      // console.log("批量删除")
      // 分析选中行的用户信息
      select_user_list.value.forEach((i) => {
        // 挨个填入
        batch_user_delete.value.user_list.push({
          account: i.account!,
          befrom: i.befrom!
        })
      })
      // vs = select_user_list.value.map(item => item.account).join(',')
    }
    status_win_users_delete.value = true
  }

  // 批量删除多个用户的函数
  async function def_user_batch_delete() {
    status_btn_users_get.value = true
    status_btn_users_delete.value = true
    let status_tmp = false
    if (status_btn_users_delete.value) {
      // 通过按钮状态判断是否点了确认删除

      await getServer("/api/manage/delete/user/batch", batch_user_delete.value).then((res) => {
        global_window("success", "删除成功")
        status_tmp = true
      }).catch((err) => {
      })
      if (status_tmp) {
        // 如果成功了就刷新一次数据
        await def_get_users()
      }
    }
    status_btn_users_get.value = false
    status_btn_users_delete.value = false
    status_win_users_delete.value = false
  }

  // 批量冻结/解冻多个用户的函数
  async function def_user_batch_freeze() {
    status_btn_users_delete.value = true
    await getServer("/api/manage/freeze/user/batch", {"ok":"ok"}).then((res)=>{

    }).catch((err)=>{

    })
  }

  // 单击单个用户的修改按钮时做的跳转动作
  function def_user_update_jump(user_info:itfResUserInfo) {
    def_user_detail(user_info)
    status_user_edit.value = true
  }

  // 单击批量修改按钮时做的操作
  function def_batch_update_jump() {
    batch_user_update.value.user_list = []

    // 只能修改本地用户 (已移除此限制)
    // if (select_user_list.value.some(item => item.befrom !== 'local')) return global_window('error', "不允许修改ldap用户")

    select_user_list.value.forEach((i) => {
      batch_user_update.value.user_list.push({
        account: i.account!,
        displayname: i.displayname!,
        tel: i.tel!,
        status: i.status!,
        roles: i.roles!,
        groups: i.groups!,
        befrom: i.befrom!,
        email: i.email!,
      })
    })
    status_win_users_update.value = true
  }

  // 批量修改多个用户的函数
  async function def_user_batch_update(data:itfResUserInfo={}) {
    status_btn_users_get.value = true
    status_btn_users_update.value = true
    let status_tmp = false
    // 如果有传参, 则只提交修改这一个用户
    if (Object.keys(data).length > 0) {
      // 这里使用深度复制
      console.log("只修改一个用户: ", Object.keys(data))
      let d = {...data}
      batch_user_update.value.user_list = [{
        account: d.account!,
        displayname: d.displayname!,
        tel: d.tel!,
        status: d.status!,
        roles: d.roles!,
        groups: d.groups!,
        email: d.email!,
        befrom: d.befrom!,
      }]
    }
    await getServer("/api/manage/update/user/batch", batch_user_update.value).then((res)=>{
      global_window("success", "修改成功")
      status_tmp = true
    }).catch(()=>{
    })
    if (status_tmp) {
      status_btn_users_get.value = false
      status_btn_users_update.value = false
      // 重新获取数据
      await def_get_users()
    }
    // 取消编辑状态
    def_user_cancel_edit()
    status_btn_users_get.value = false
    status_btn_users_update.value = false
  }

  // 批量重置多个用户密码的函数
  async function def_user_batch_passwd() {
    status_btn_users_changepasswd.value = true
    // 先清空
    batch_user_changepasswd.value.user_list = []
    // 再提取当前选中的用户的账号, 但密码统一填入数据框中的
    select_user_list.value.forEach((i)=>{
      // 如果用户不是本地用户则报错退出
      if (i.befrom != 'local') {
        global_window('error', "不允许修改ldap用户")
        return
      }
      batch_user_changepasswd.value.user_list.push({
        account: i.account!,
        password: input_batch_passwd.value!
      })
    })

    await getServer("/api/manage/changepasswd/user/batch", batch_user_changepasswd.value).then(()=>{
      global_window("success", "修改成功")
    }).catch((err)=>{
    })
    status_btn_users_changepasswd.value = false
    status_win_users_changepasswd.value = false
  }

  // 获取ldap搜索组的信息
  async function def_get_ous() {
    status_btn_ous.value = true
    await getServer("/api/user/ldap/ous/manage/check", {"ok": "ok"}).then((res)=>{
      data_res_ous.value = res as itfResLdapOus
    }).catch(()=>{})
    status_btn_ous.value = false
  }

  // 获取指定搜索组的所有用户
  async function def_ldap_search() {
    if (!select_ous_name.value) {
      global_window("error", "没有选择ldap组")
      return
    }
    data_ldapUsers_list.value = []
    status_btn_ldap_search.value = true
    await getServer("/api/user/ldap/ous/manage/searchExists", {"ou_name": select_ous_name.value}).then((res)=>{
      data_res_ldapUsers.value = res as itfResLdapOuUsers
      console.log("搜索到ldap用户: ", data_res_ldapUsers.value)
      Object.values(data_res_ldapUsers.value.users).forEach((i)=>{
        data_ldapUsers_list.value.push({
          "ldap_ou_name": select_ous_name.value,
          "account": i.account || "",
          "ldap_dn": i.dn,
          "tel": i.tel,
          "displayname": i.displayname,
          "status": "on",
          "roles": i.roles || [role_delault],
          "groups": i.groups || [],
          "email": i.email,
          "is_exists": i.is_exists
        })
      })

    }).catch(()=>{})
    // 排序
    data_ldapUsers_list.value.sort(sortLdapSearch)
    console.log("搜索到的ldap用户: ", data_res_ldapUsers)
    status_btn_ldap_search.value = false
  }

  // 向后端提交从指定ldap组中选中的用户
  async function def_ldapUsers_add() {
    status_btn_ldap_search.value = true
    let data_req_tmp:itfReqAddLdapUsers = {"dict_user_info":{}}
    select_ldapUser_list.value.forEach((i)=>{
      let {is_exists, ...data_line_tmp} = {...i}
      data_req_tmp.dict_user_info[i.ldap_dn] = data_line_tmp
    })
    let status_tmp = false
    await getServer("/api/user/ldap/ous/manage/useradd", data_req_tmp).then((res)=>{
      status_tmp = true
    }).catch(()=>{})
    if (status_tmp) {
      // 重新搜索一次ldap用户列表
      await def_ldap_search()
      // 重新获取一次用户列表
      await def_get_users()
    }
    status_btn_ldap_search.value = false
  }

  // 对ldap搜索结果table排序的函数
  function sortLdapSearch(obj1:itfReqAddLdapUser, obj2:itfReqAddLdapUser){
    // 按 is_exists  属性排序, is_exists 是布尔值, JavaScript 中 true 和 false 会被转换为数字, true 为 1, false 为 0
    if (obj1.is_exists !== obj2.is_exists) {
      return obj1.is_exists ? 1 : -1; // true 排前面，false 排后面 (利用的是升序排序, 数字越小越排在前面), 降序则 1 : -1
    }

    // 如果 is_exists 相同, 按 dn 属性排序

    return obj1.ldap_dn.localeCompare(obj2.ldap_dn); // 这里是对字符串排序, 字母降序
    // 如果是升序, 那么就反转两个变量
    // obj1.dn.localeCompare(obj2.dn)
    // 如果是数字, 直接用运算符
    // return obj1.dn - obj2.dn

  }

  // table表头的样式
  let style_table_header = {
    "background-color": "#f5f5f5",
    "color": "#5a5a5a",
    "padding-top": "2px",
    "padding-bottom": "2px",
    "border-right": "1px solid #dbdbdb",
    // "border-right-color": "#dbdbdb",
    "--el-table-border-color": "white"
  }
  // table普通列的样式
  let style_table_cell = {
    // "border-bottom": "none",
    "border-right": "none",
    "border-bottom-color": "#f5f5f5",
    "--el-table-border-color": "white",
  }
  // table整体外边框的样式
  let style_table = {
    "--el-table-border-color": "white",
  }

</script>

<template>
  <!--{{ select_user_list }}-->
  <el-card class="card_user_manage" v-if="select_breadcrumb=='users'" show-overflow-tooltip v-loading="status_btn_users_get">
    <!--<el-alert show-icon type="info" class="alert_card_head" :closable="false">用户管理</el-alert>-->
    <div style="margin-bottom: 10px">
      <el-button type="primary" @click="def_get_users" :loading="status_btn_users_get">刷新</el-button>
      <el-button v-dcj="`新增`" type="success" @click="status_win_users_create=true">新增本地用户</el-button>
      <el-button v-dcj="`新增`" type="success" @click="status_win_ldap_search=true">导入LDAP用户</el-button>
      <el-input v-model="input_search_user" clearable style="width: 400px; margin-left: 20px"/>
    </div>

    <!--Object.values(data_res_user_info)-->
    <el-table
        :data="filter_show_user" @selection-change="user_select_changed" v-loading="status_btn_users_get" max-height="600px"
        :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border
    >
      <el-table-column type="selection" :selectable="selectable" width="55"/>
      <el-table-column label="账号" prop="account" min-width="100" sortable>
        <!--<template #header>-->
        <!--  <div class="table_head">账号</div>-->
        <!--</template>-->
        <template #default="scope">
          <!--<el-button text type="primary" @click="def_user_detail(scope.row)">{{scope.row.account}}</el-button>-->
          <el-link @click="def_user_detail(scope.row)"><el-text type="primary">{{scope.row.account}}</el-text></el-link>
        </template>
      </el-table-column>
      <!--<el-table-column label="ID" prop="user_id" min-width="100" />-->
      <el-table-column label="显示名" prop="displayname" min-width="100" sortable>
        <!--<template #header>-->
        <!--  <div class="table_head">显示名</div>-->
        <!--</template>-->
      </el-table-column>
      <el-table-column label="类型" prop="befrom" width="100" sortable>
        <!--<template #header>-->
        <!--  <div class="table_head">类型</div>-->
        <!--</template>-->
      </el-table-column>
      <!--<el-table-column label="角色" prop="role_id" min-width="100" show-overflow-tooltip>-->
      <!--  <template #default="scope">-->
      <!--    <el-tag v-for="i in scope.row.role_id.split(',')" size="small">{{i}}</el-tag>-->
      <!--  </template>-->
      <!--</el-table-column>-->
      <el-table-column label="登录状态" prop="is_online" width="120px" sortable>
        <template #default="scope">
          <el-button v-if="scope.row.is_online" size="small" type="success" plain>在线</el-button>
          <el-button v-if="!scope.row.is_online" size="small" type="info" plain>离线</el-button>
        </template>
      </el-table-column>
      <el-table-column label="账户状态" prop="status" width="120px" sortable>
        <template #default="scope">
          <el-button v-if="scope.row.status=='on'" size="small" type="success">正常</el-button>
          <el-button v-if="scope.row.status=='off'" size="small" type="danger">冻结</el-button>
          <el-button v-if="scope.row.status!='off'&&scope.row.status!='on'" size="small" type="info">未知</el-button>
        </template>
      </el-table-column>
      <!--<el-table-column label="创建时间" prop="date_create" width="200"/>-->
      <!--<el-table-column label="创建时间" prop="date_create" width="200">-->
      <!--  <template #default="scope">-->
      <!--    <el-text type="primary">{{def_fromat_date(scope.row.date_create)}}</el-text>-->
      <!--  </template>-->
      <!--</el-table-column>-->
      <!--<el-table-column label="更新时间" prop="date_update" width="200">-->
      <!--  <template #default="scope">-->
      <!--    <el-text type="primary">{{def_fromat_date(scope.row.date_latest_login)}}</el-text>-->
      <!--  </template>-->
      <!--</el-table-column>-->
      <el-table-column label="最后登录时间" prop="date_latest_login" width="200">
        <template #default="scope">
          <el-text type="primary">{{def_fromat_date(scope.row.date_latest_login)}}</el-text>
        </template>
      </el-table-column>

      <el-table-column label="操作" prop="displayname" width="300">
        <template #default="scope">
          <el-button plain size="small" type="primary" @click="def_user_detail(scope.row)">详情</el-button>
          <el-button v-dcj="`新增`" plain size="small" type="warning" @click="def_user_clone(scope.row)">克隆</el-button>
          <el-button
              v-dcj="`编辑`" plain size="small" type="warning" @click="def_user_update_jump(scope.row)"
          >
            修改
          </el-button>
          <el-button
              v-dcj="`删除`" plain size="small" type="danger" :loading="status_btn_users_delete"
              @click="def_before_delete(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <!--<el-affix position="bottom" :offset="20">-->
    <!--  -->
    <!--</el-affix>-->
    <div style="margin-top: 20px">
      <el-button v-dcj="`编辑`" :disabled="select_user_list.length==0" type="warning" @click="def_batch_update_jump()">批量修改</el-button>
      <el-button v-dcj="`删除`" id="delete_batch" :disabled="select_user_list.length==0" type="danger"  @click="def_before_delete()">批量删除</el-button>
      <el-button v-dcj="`编辑`" :disabled="select_user_list.length==0" type="danger" @click="status_win_users_changepasswd=true">批量重置密码</el-button>
    </div>
  </el-card>


  <!--{{data_res_user_info}}-->
  <!--{{ select_user }}-->
  <!-- 单个用户详情的卡片 -->
  <el-card v-if="select_breadcrumb=='detail'" v-loading="status_btn_users_get">
    <!-- 面包屑部分 -->
    <el-breadcrumb separator="/" class="breadcrumb_user">
      <el-breadcrumb-item @click="select_breadcrumb='users'">
        <!--<a @click="select_breadcrumb='users'"><el-text type="primary"><el-icon><ArrowLeftBold /></el-icon>用户列表</el-text></a>-->
        <a @click="def_user_list()"><el-text type="primary"><el-icon><ArrowLeftBold /></el-icon>用户列表</el-text></a>
      </el-breadcrumb-item>
      <el-breadcrumb-item>{{select_user.account}}</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 单个用户详情展示部分 -->
    <!--<el-descriptions :column="2">-->
    <!--  &lt;!&ndash; 自定义标题 &ndash;&gt;-->
    <!--  <template #title>-->
    <!--    <span class="title_user">{{ select_user.account }}</span>-->
    <!--    &lt;!&ndash; 修改功能的按钮图标 &ndash;&gt;-->
    <!--    <el-link :underline="false"><el-icon color="#409EFF" @click="status_user_edit=true"><Edit /></el-icon></el-link>-->
    <!--  </template>-->
    <!--  &lt;!&ndash;<el-descriptions-item v-for="(v, k) in data_res_user_info[select_user_id]" :label="k">{{v}}</el-descriptions-item>&ndash;&gt;-->
    <!--  <el-descriptions-item label="登录账号">{{select_user.account}}</el-descriptions-item>-->
    <!--  <el-descriptions-item label="邮箱">-->
    <!--    <span v-if="!status_user_edit">{{select_user.email}}</span>-->
    <!--    <el-input v-if="status_user_edit" size="small" v-model="select_user.email" class="input_descriptions"/>-->
    <!--  </el-descriptions-item>-->
    <!--  <el-descriptions-item label="显示名">-->
    <!--    <span v-if="!status_user_edit">{{select_user.displayname}}</span>-->
    <!--    <el-input v-if="status_user_edit" size="small" v-model="select_user.displayname" class="input_descriptions"/>-->
    <!--  </el-descriptions-item>-->
    <!--  <el-descriptions-item label="手机号">-->
    <!--    <span v-if="!status_user_edit">{{select_user.tel}}</span>-->
    <!--    <el-input v-if="status_user_edit" size="small" v-model="select_user.tel" class="input_descriptions"/>-->
    <!--  </el-descriptions-item>-->
    <!--  <el-descriptions-item label="用户类型">{{select_user.befrom}}</el-descriptions-item>-->
    <!--  <el-descriptions-item label="创建时间">{{def_fromat_date(select_user.date_create!)}}</el-descriptions-item>-->
    <!--  <el-descriptions-item label="角色">-->
    <!--    &lt;!&ndash;<span v-if="!status_user_edit">{{select_user.role_id!.join(';')}}</span>&ndash;&gt;-->
    <!--    <el-tag v-if="!status_user_edit" v-for="i in select_user.roles" size="small" style="margin-left: 5px">-->
    <!--      <router-link :to="{ path: '/home/setting/rbac_manage', query: { role_id: i } }" style="text-decoration: none">-->
    <!--        <el-text type="primary">{{i}}</el-text>-->
    <!--      </router-link>-->
    <!--    </el-tag>-->
    <!--    <el-select v-if="status_user_edit" v-model="select_user.roles" multiple size="small" class="input_descriptions" filterable>-->
    <!--      <el-option v-for="i in data_role_list" :key="i.role_id" :label="i.role_id" :value="i.role_id"/>-->
    <!--    </el-select>-->
    <!--  </el-descriptions-item>-->
    <!--  <el-descriptions-item label="更新时间">{{def_fromat_date(select_user.date_update!)}}</el-descriptions-item>-->
    <!--  <el-descriptions-item label="加入的组">-->
    <!--    &lt;!&ndash;<span v-if="!status_user_edit">{{select_user.role_id!.join(';')}}</span>&ndash;&gt;-->
    <!--    <el-tag v-if="!status_user_edit" v-for="i in select_user.groups" size="small" style="margin-left: 5px">-->
    <!--      <router-link :to="{ path: '/home/setting/group_manage', query: { group_id: i } }" style="text-decoration: none">-->
    <!--        <el-text type="primary">{{i}}</el-text>-->
    <!--      </router-link>-->
    <!--    </el-tag>-->
    <!--    <el-select v-if="status_user_edit" v-model="select_user.groups" multiple size="small" class="input_descriptions" filterable>-->
    <!--      <el-option v-for="i in data_res_group_list" :key="i.group_id" :label="i.group_id" :value="i.group_id"/>-->
    <!--    </el-select>-->
    <!--  </el-descriptions-item>-->
    <!--  <el-descriptions-item label="最近登录时间">{{def_fromat_date(select_user.date_latest_login!)}}</el-descriptions-item>-->
    <!--  <el-descriptions-item label="用户状态">-->
    <!--    <span v-if="!status_user_edit">{{select_user.status}}</span>-->
    <!--    &lt;!&ndash;<el-input v-if="status_user_edit" size="small" v-model="select_user.status" class="input_descriptions"/>&ndash;&gt;-->
    <!--    <el-radio-group size="small" v-if="status_user_edit" v-model="select_user.status" class="input_ous">-->
    <!--      <el-radio-button  value="on">正常</el-radio-button>-->
    <!--      <el-radio-button value="off">冻结</el-radio-button>-->
    <!--    </el-radio-group>-->
    <!--  </el-descriptions-item>-->
    <!--  &lt;!&ndash; ldap信息只有在用户为ldap类型时才展示 &ndash;&gt;-->
    <!--  <div v-if="select_user.befrom=='ldap'">-->
    <!--    <el-descriptions-item label="LDAP组">{{select_user.ldap_ou_name}}</el-descriptions-item>-->
    <!--    <el-descriptions-item label="dn">{{select_user.ldap_dn}}</el-descriptions-item>-->
    <!--  </div>-->
    <!--  <el-descriptions-item v-if="!status_user_edit" label="密码">-->
    <!--    <el-button v-if="!status_user_edit && !status_user_passwd" type="warning" size="small" @click="status_user_passwd=true">重置密码</el-button>-->
    <!--    <el-input-->
    <!--        v-if="status_user_passwd && !status_user_edit"-->
    <!--        type="password" show-password size="small"-->
    <!--        v-model="data_user_passwd" class="input_descriptions" placeholder="******"/>-->
    <!--    <el-button v-if="status_user_passwd && !status_user_edit" type="warning" size="small">确定-->
    <!--    </el-button>-->
    <!--    <el-button v-if="status_user_passwd && !status_user_edit" size="small" @click="def_user_cancel_passwd">取消</el-button>-->
    <!--  </el-descriptions-item>-->
    <!--</el-descriptions>-->

    <span class="title_user">{{ select_user.account }}</span>
    <!-- 修改功能的按钮图标 -->
    <el-link v-dcj="`编辑`" :underline="false"><el-icon color="#409EFF" @click="status_user_edit=true"><Edit /></el-icon></el-link>
    <el-row :gutter="20">
      <el-col :span="12" style="margin-top: 20px">
        <el-form>
          <el-form-item label="登录账号">{{select_user.account}}</el-form-item>
          <el-form-item label="用户类型">{{select_user.befrom}}</el-form-item>
          <el-form-item label="邮箱">
            <span v-if="!status_user_edit">{{select_user.email}}</span>
            <el-input v-if="status_user_edit" size="small" v-model="select_user.email" class="input_descriptions"/>
          </el-form-item>
          <el-form-item label="显示名">
            <span v-if="!status_user_edit">{{select_user.displayname}}</span>
            <el-input v-if="status_user_edit" size="small" v-model="select_user.displayname" class="input_descriptions"/>
          </el-form-item>
          <el-form-item label="手机号">
            <span v-if="!status_user_edit">{{select_user.tel}}</span>
            <el-input v-if="status_user_edit" size="small" v-model="select_user.tel" class="input_descriptions"/>
          </el-form-item>
          <el-form-item label="用户状态">
            <span v-if="!status_user_edit">{{select_user.status}}</span>
            <!--<el-input v-if="status_user_edit" size="small" v-model="select_user.status" class="input_descriptions"/>-->
            <el-radio-group size="small" v-if="status_user_edit" v-model="select_user.status" class="input_ous">
              <el-radio-button  value="on">正常</el-radio-button>
              <el-radio-button value="off">冻结</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item v-if="select_user.befrom=='ldap'" label="dn">{{select_user.ldap_dn}}</el-form-item>
          <el-form-item v-dcj="`编辑`" v-if="!status_user_edit" label="密码">
            <el-button v-dcj="`编辑`" v-if="!status_user_edit && !status_user_passwd" type="warning" size="small" @click="status_user_passwd=true">重置密码</el-button>
            <el-input
                v-if="status_user_passwd && !status_user_edit"
                type="password" show-password size="small"
                v-model="data_user_passwd" class="input_descriptions" placeholder="******"/>
            <el-button v-if="status_user_passwd && !status_user_edit" type="warning" size="small">确定
            </el-button>
            <el-button v-if="status_user_passwd && !status_user_edit" size="small" @click="def_user_cancel_passwd">取消</el-button>
          </el-form-item>
        </el-form>
      </el-col>
      <el-col :span="12">
        <el-form>
          <el-form-item label="创建时间">{{def_fromat_date(select_user.date_create!)}}</el-form-item>
          <el-form-item label="更新时间">{{def_fromat_date(select_user.date_update!)}}</el-form-item>
          <el-form-item label="最近登录时间">{{def_fromat_date(select_user.date_latest_login!)}}</el-form-item>
          <el-form-item label="角色">
            <!--<span v-if="!status_user_edit">{{select_user.role_id!.join(';')}}</span>-->
            <el-tag v-if="!status_user_edit" v-for="i in select_user.roles" size="small" style="margin-left: 5px">
              <router-link :to="{ path: '/home/setting/rbac_manage', query: { role_id: i } }" style="text-decoration: none">
                <el-text type="primary">{{i}}</el-text>
              </router-link>
            </el-tag>
            <el-select v-if="status_user_edit" v-model="select_user.roles" multiple size="small" class="input_descriptions" filterable>
              <el-option v-for="i in data_role_list" :key="i.role_id" :label="i.role_id" :value="i.role_id"/>
            </el-select>
          </el-form-item>
          <el-form-item label="加入的组">
            <!--<span v-if="!status_user_edit">{{select_user.role_id!.join(';')}}</span>-->
            <el-tag v-if="!status_user_edit" v-for="i in select_user.groups" size="small" style="margin-left: 5px">
              <router-link :to="{ path: '/home/setting/group_manage', query: { group_id: i } }" style="text-decoration: none">
                <el-text type="primary">{{i}}</el-text>
              </router-link>
            </el-tag>
            <el-select v-if="status_user_edit" v-model="select_user.groups" multiple size="small" class="input_descriptions" filterable>
              <el-option v-for="i in data_res_group_list" :key="i.group_id" :label="i.group_id" :value="i.group_id"/>
            </el-select>
          </el-form-item>
          <el-form-item v-if="select_user.befrom=='ldap'" label="LDAP组">{{select_user.ldap_ou_name}}</el-form-item>
        </el-form>
      </el-col>
    </el-row>


    <!--{{data_user_list}}-->
    <div v-if="status_user_edit">
      <el-button type="warning" @click="def_user_batch_update(select_user)" :loading="status_btn_users_update">提交</el-button>
      <el-button @click="def_user_cancel_edit()">取消</el-button>
    </div>
  </el-card>

  <!-- 批量新增本地用户的弹窗 -->
  <el-dialog v-model="status_win_users_create" width="90%">
    <el-table :data="batch_user_create.user_list" :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border>
      <el-table-column label="账号" width="150px">
        <template #default="scope">
          <el-input v-model="scope.row.account"/>
        </template>
      </el-table-column>
      <el-table-column label="显示名" width="150px">
        <template #default="scope">
          <el-input v-model="scope.row.displayname"/>
        </template>
      </el-table-column>
      <el-table-column label="角色" min-width="200px">
        <template #default="scope">
          <!--<el-input v-model="scope.row.displayname"/>-->
          <el-select v-model="scope.row.roles" multiple filterable>
            <el-option v-for="i in data_role_list" :key="i.role_id" :label="i.role_id" :value="i.role_id"/>
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="用户组" min-width="200px">
        <template #default="scope">
          <!--<el-input v-model="scope.row.displayname"/>-->
          <el-select v-model="scope.row.groups" multiple filterable>
            <el-option v-for="i in data_res_group_list" :key="i.group_id" :label="i.group_id" :value="i.group_id"/>
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="邮箱" min-width="150px">
        <template #default="scope">
          <el-input v-model="scope.row.email"/>
        </template>
      </el-table-column>
      <el-table-column label="手机号" width="150px">
        <template #default="scope">
          <el-input v-model="scope.row.tel"/>
        </template>
      </el-table-column>
      <el-table-column label="密码" width="150px">
        <template #default="scope">
          <el-input v-model="scope.row.password" type="password" show-password autocomplete="new-password"/>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="150px">
        <template #default="scope">
          <el-radio-group size="small" v-model="scope.row.status">
            <el-radio-button value="on">正常</el-radio-button>
            <el-radio-button value="off">冻结</el-radio-button>
          </el-radio-group>
        </template>
      </el-table-column>
      <el-table-column label="" width="150px">
        <template #default="scope">
          <el-button size="small" type="danger" @click="batch_user_create.user_list.splice(scope.$index, 1)">删除</el-button>
          <el-button size="small" type="info" @click="batch_user_create.user_list.push(scope.row)">克隆</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-button style="width: 100%;margin-top: 20px" @click="def_batch_add_new" :icon="CirclePlus" text type="primary">新增空白行</el-button>
    <!-- 操作按钮 -->
    <template #footer>
      <el-button type="success" @click="def_user_batch_create" :loading="status_btn_users_create">提交</el-button>
      <el-button @click="status_win_users_create=false">取消</el-button>
    </template>
    <!--<div class="div_batch_create_down">-->
    <!--</div>-->
  </el-dialog>

  <!-- 确认删除时的弹框 -->
  <el-dialog width="400px" v-model="status_win_users_delete" center>
    <el-text>确认删除用户: </el-text>
    <el-text type="danger">{{batch_user_delete.user_list.map(i=>i.account).join(', ')}}</el-text>
    <el-text>吗?</el-text>
    <template #footer>
      <el-button type="danger" @click="def_user_batch_delete" :loading="status_btn_users_delete">删除</el-button>
      <el-button @click="status_win_users_delete=false">取消</el-button>
    </template>
  </el-dialog>

  <!-- 批量修改用户的弹窗 -->
  <el-dialog  v-model="status_win_users_update" width="80%">
    <el-table :data="batch_user_update.user_list" :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border>
      <el-table-column label="账号" width="150px" >
        <template #default="scope">
          <el-input v-model="scope.row.account" disabled/>
        </template>
      </el-table-column>
      <el-table-column label="显示名" width="150px">
        <template #default="scope">
          <el-input v-model="scope.row.displayname" :disabled="scope.row.befrom=='ldap'"/>
        </template>
      </el-table-column>
      <el-table-column label="角色" min-width="200px">
        <template #default="scope">
          <!--<el-input v-model="scope.row.displayname"/>-->
          <el-select v-model="scope.row.roles" multiple filterable>
            <el-option v-for="i in data_role_list" :key="i.role_id" :label="i.role_id" :value="i.role_id"/>
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="用户组" min-width="200px">
        <template #default="scope">
          <!--<el-input v-model="scope.row.displayname"/>-->
          <el-select v-model="scope.row.groups" multiple filterable>
            <el-option v-for="i in data_res_group_list" :key="i.group_id" :label="i.group_id" :value="i.group_id"/>
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="邮箱" min-width="150px">
        <template #default="scope">
          <el-input v-model="scope.row.email" :disabled="scope.row.befrom=='ldap'"/>
        </template>
      </el-table-column>
      <el-table-column label="手机号" width="150px">
        <template #default="scope">
          <el-input v-model="scope.row.tel" :disabled="scope.row.befrom=='ldap'"/>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="120px">
        <template #default="scope">
          <el-radio-group size="small" v-model="scope.row.status">
            <el-radio-button value="on">正常</el-radio-button>
            <el-radio-button value="off">冻结</el-radio-button>
          </el-radio-group>
        </template>
      </el-table-column>
      <!--<el-table-column label="" width="150px">-->
      <!--  <template #default="scope">-->
      <!--    <el-button size="small" type="danger" @click="batch_user_create.user_list.splice(scope.$index)">删除</el-button>-->
      <!--    <el-button size="small" type="info" @click="batch_user_create.user_list.push(scope.row)">克隆</el-button>-->
      <!--  </template>-->
      <!--</el-table-column>-->
    </el-table>
    <!-- 操作按钮 -->
    <template #footer>
      <el-button type="success" @click="def_user_batch_update()" :loading="status_btn_users_update">提交</el-button>
      <el-button @click="status_win_users_update=false">取消</el-button>
    </template>
    <!--<div class="div_batch_create_down">-->
    <!--</div>-->
  </el-dialog>

  <!-- 批量修改密码的窗口 -->
  <el-dialog v-model="status_win_users_changepasswd" width="400px" center>
    <el-text>重置用户: </el-text>
    <el-text type="danger">{{select_user_list.map(i=>i.account).join(', ')}}</el-text>
    <el-text>的密码</el-text>
    <el-input v-model="input_batch_passwd" style="margin-top: 20px"/>
    <!-- 操作按钮 -->
    <template #footer>
      <el-button type="danger" @click="def_user_batch_passwd()" :loading="status_btn_users_changepasswd">提交</el-button>
      <el-button @click="status_win_users_changepasswd=false">取消</el-button>
    </template>
  </el-dialog>

  <!-- 导入ldap账户的弹框 -->
  <el-dialog v-model="status_win_ldap_search" width="90%" center>
    <div class="dialog_head">
      <el-button :icon="RefreshRight" @click="def_get_ous()" :loading="status_btn_ous"/>
      <el-select v-model="select_ous_name" style="width: 200px;" placeholder="选择LDAP组" :loading="status_btn_ous" filterable>
        <el-option v-for="i in Object.keys(data_res_ous)" :label="i" :value="i"/>
      </el-select>

      <el-button type="primary" @click="def_ldap_search()" :loading="status_btn_ous||status_btn_ldap_search" style="margin-left: 30px">检索用户</el-button>
    </div>
    <div class="dialog_head">
      <!--{{data_ldapUsers_list}}-->
      <el-table
          :data="data_ldapUsers_list" v-loading="status_btn_ldap_search" @selection-change="ldapUser_select_changed"
          :default-sort="{ prop: 'is_exists', order: 'descending' }" v-if="data_ldapUsers_list.length>0"
          :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border
      >
        <el-table-column type="selection" :selectable="selectable_ldap" width="55"/>
        <el-table-column :label="`登录账号(`+data_res_ldapUsers.attrs.account+`)`" width="150px">
          <template #default="scope">
            <el-input v-model="scope.row.account" :disabled="scope.row.is_exists"/>
          </template>
        </el-table-column>
        <el-table-column label="dn" prop="ldap_dn" min-width="250" show-overflow-tooltip>
          <template #default="scope">
            <el-text >{{scope.row.ldap_dn}}</el-text>
          </template>
        </el-table-column>
        <el-table-column :label="`显示名(`+data_res_ldapUsers.attrs.displayname+`)`" prop="displayname" min-width="100" />
        <el-table-column :label="`邮箱(`+data_res_ldapUsers.attrs.email+`)`" prop="email" width="150" show-overflow-tooltip/>
        <el-table-column :label="`手机号(`+data_res_ldapUsers.attrs.tel+`)`" prop="tel" width="120" />
        <el-table-column label="角色" min-width="110px">
          <template #default="scope">
            <!--<el-input v-model="scope.row.displayname"/>-->
            <el-select v-model="scope.row.roles" multiple :disabled="scope.row.is_exists" filterable>
              <el-option v-for="i in data_role_list" :key="i.role_id" :label="i.role_id" :value="i.role_id"/>
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="用户组" min-width="110px">
          <template #default="scope">
            <!--<el-input v-model="scope.row.displayname"/>-->
            <el-select v-model="scope.row.groups" multiple filterable :disabled="scope.row.is_exists">
              <el-option v-for="i in data_res_group_list" :key="i.group_id" :label="i.group_id" :value="i.group_id" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120px">
          <template #default="scope">
            <el-radio-group size="small" v-model="scope.row.status" :disabled="scope.row.is_exists">
              <el-radio-button value="on">正常</el-radio-button>
              <el-radio-button value="off">冻结</el-radio-button>
            </el-radio-group>
          </template>
        </el-table-column>
        <el-table-column label="存在性" width="80px" >
          <template #default="scope">
            <el-tag v-if="scope.row.is_exists" type="info">已导入</el-tag>
            <el-tag v-if="!scope.row.is_exists" type="success">未导入</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <template #footer>
      <el-button type="success" @click="def_ldapUsers_add()" :loading="status_btn_ldap_search">导入选中</el-button>
      <el-button @click="status_win_ldap_search=false" :disabled="status_btn_ldap_search">取消</el-button>
    </template>
    <!--{{data_ldapUsers_list}}<br>-->
    <!--{{select_ldapUser_list}}-->
  </el-dialog>

  <!--<el-card >-->
  <!--  &lt;!&ndash; 编辑区 &ndash;&gt;-->
  <!--  {{batch_user_create}}-->
  <!--</el-card>-->


</template>

<style scoped>
  .card_user_manage {
    /*height: 600px;*/
    overflow: auto;
    min-width: 800px;
    margin-bottom: 20px;
  }
  .alert_card_head {
    margin-bottom: 10px;
  }
  .breadcrumb_user {
    margin-bottom: 10px;
  }
  .title_user {
    line-height: 40px;
    font-size: 28px;
    font-weight: 500;
    margin-right: 15px;
  }
  .input_descriptions {
    /*min-width: 50px;*/
    margin-right: 20px;
    max-width: 200px;
  }
  .div_user_passwd_input {
    display: flex;
    justify-content: center;  /* 水平居中子元素 */
    align-items: center;      /* 垂直居中子元素 */
    width: 100px;
    /*max-width: 300px;*/
  }
  .div_batch_create_head {
    display: flex;
    justify-content: right;
  }
  .div_batch_create_down {
    display: flex;
    justify-content: left;
    margin-top: 20px;
  }
  .dialog_head {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 15px;
  }
  ::v-deep .el-table th.el-table__cell {
    background-color: #f5f5f5;
  }
</style>

<style>
  .table_head {
    background-color: #b13939;
  }
</style>