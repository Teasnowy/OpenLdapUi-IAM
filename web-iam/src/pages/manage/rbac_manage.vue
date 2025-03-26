<script setup lang="ts">
import {computed, type Ref, ref} from 'vue'
import {useRoute, useRouter, type LocationQueryValue, RouterLink} from 'vue-router'
import type {
  itfResRoleObj,
  itfResRole,
  itfReqRoleAdd,
  itfResUserList,
  itfResGroupObj,
  itfResWeb, itfResWebObj, itfResApi, itfResApiObj, itfResGroup
} from '@/api/itf_manage'
  import {Edit, CirclePlus, RefreshRight, ArrowLeftBold} from '@element-plus/icons-vue'
  import type { TableInstance } from 'element-plus'
  import {userInfo} from "@/pinia/envs";
  import {global_window} from '@/api/def_feedback'
  import {getServer} from '@/api/def_servers'

  let route = useRoute();
  let router = useRouter()


  // 当前获取角色信息时的状态
  let status_btn_role_get:Ref<boolean> = ref(false)
  // 存储后端返回的角色信息
  let data_res_role_info:Ref<itfResRoleObj> = ref({})
  // 存储后端返回的角色列表
  let data_res_role_list:Ref<itfResRole[]> = ref([])
  // 存储后端返回的用户信息
  let data_res_user_info:Ref<itfResUserList> = ref({})
  // 存储后端返回的组信息
  let data_res_group_obj:Ref<itfResGroupObj> = ref({})
  // 存储后端返回的菜单库信息
  let data_res_web_info:Ref<itfResWebObj> = ref({})
  // 存储后端返回的后端接口对象
  let data_res_api_obj:Ref<itfResApiObj> = ref({})
  // 存储后端返回的后端接口信息
  let data_res_api_list:Ref<itfResApi[]> = ref([])

  // 存储当前选择的role的id
  let select_role_id:Ref<string> = ref("")
  // 当前页面展示哪些卡片
  let select_breadcrumb:Ref<"roles"|"detail"> = ref('roles')
  // 单个角色详情页的编辑状态
  let status_role_edit:Ref<boolean> = ref(false)
  // 新建角色的弹框的状态
  let status_win_role_create:Ref<boolean> = ref(false)
  // 克隆角色的弹框
  let status_win_role_clone:Ref<boolean> = ref(false)
  // 新建角色成功后询问是否进一步赋权的弹窗状态
  let status_win_role_update_ask:Ref<boolean> = ref(false)
  // 更新角色信息的右侧弹出框状态
  let status_win_role_update:Ref<boolean> = ref(false)
  // 更新角色信息的右侧弹出框状态的加载状态
  let load_win_role_update:Ref<boolean> = ref(false)
  // 后端接口列表的多选的回调
  let select_apis_before = ref<TableInstance>()
  // 删除角色的确认弹框的状态
  let status_win_role_delete:Ref<boolean> = ref(false)
  // 详情页中选择的标签
  let status_tab:Ref<"users"|"groups"|"containers"|"webs"> = ref("webs")

  // 存储新建单个角色时的临时信息
  let data_req_role_create:Ref<itfReqRoleAdd> = ref({
    "role_id": "",
    "role_desc": "",
    "groups": [],
    "users": [],
    "apis": [],
    "webs": [],
    "containers": []
  })

  // 存储当前选择的role的详细信息, 用来展示
  let select_role_info:Ref<itfResRole> = ref({
    role_id: "",
    role_desc: "",
    date_update: "",
    date_create: "",
    groups: [],
    users: [],
    "webs": [],
    containers: [],
    apis: [],
  })
  // 存储当前选择的role的详细信息, 用来临时修改
  let select_role_info_tmp:Ref<itfReqRoleAdd> = ref({
    role_id: "",
    role_desc: "",
    groups: [],
    apis: [],
    users: [],
    "webs": [],
    containers: []
  })

  //初始化数据
  def_get_roles()

  let input_search_role:Ref<string> = ref("")
  // 筛选角色的计算函数
  const filter_show_role = computed(() =>
      data_res_role_list.value.filter(
          (data:itfResRole) =>
              (!input_search_role.value || data.role_id.toLowerCase().includes(input_search_role.value.toLowerCase())) ||
              (!input_search_role.value || data.role_desc.toLowerCase().includes(input_search_role.value.toLowerCase()))
          // console.log(select_date_work.value, data.date_work)
      )
  )

  let input_search_group:Ref<string> = ref("")
  // 筛选组的计算函数
  const filter_show_group = computed(() =>
      select_role_info.value.groups.filter(
          (data) =>
              (!input_search_group.value || data.group_id.toLowerCase().includes(input_search_group.value.toLowerCase())) ||
              (!input_search_group.value || data.group_desc.toLowerCase().includes(input_search_group.value.toLowerCase()))
          // console.log(select_date_work.value, data.date_work)
      )
  )

  let input_search_api:Ref<string> = ref("")
  // 筛选指定api的计算函数
  const filter_show_api = computed(() =>
      select_role_info.value.apis.filter(
          (data) =>
              (!input_search_api.value || data.api_url.toLowerCase().includes(input_search_api.value.toLowerCase())) ||
              (!input_search_api.value || data.api_endpoint.toLowerCase().includes(input_search_api.value.toLowerCase()))
          // console.log(select_date_work.value, data.date_work)
      )
  )

  let input_search_select_user:Ref<string> = ref("")
  // 筛选指定组的用户的计算函数
  const filter_show_select_user = computed(() =>
      select_role_info.value.users.filter(
          (data) =>
              (!input_search_select_user.value || data.account.toLowerCase().includes(input_search_select_user.value.toLowerCase())) ||
              (!input_search_select_user.value || data.displayname.toLowerCase().includes(input_search_select_user.value.toLowerCase()))
          // console.log(select_date_work.value, data.date_work)
      )
  )

  let input_search_web:Ref<string> = ref("")
  // 筛选指定web的计算函数
  const filter_show_web = computed(() =>
      select_role_info.value.webs.filter(
          (data) =>
              (!input_search_web.value || data.web_route.toLowerCase().includes(input_search_web.value.toLowerCase())) ||
              (!input_search_web.value || data.web_name.toLowerCase().includes(input_search_web.value.toLowerCase()))
          // console.log(select_date_work.value, data.date_work)
      )
  )

  let input_search_containers:Ref<string> = ref("")
  // 筛选指定web的container的计算函数
  const filter_show_containers = computed(() =>
      select_role_info.value.containers.filter(
          (data) =>
              (!input_search_web.value || data.web_route.toLowerCase().includes(input_search_web.value.toLowerCase())) ||
              (!input_search_web.value || data.container_name.toLowerCase().includes(input_search_web.value.toLowerCase()))
          // console.log(select_date_work.value, data.date_work)
      )
  )

  // 勾选web页面的状态发生改变时, 用以在取消读权限时, 放弃选取所有该页面的菜单块
  function def_select_web_change(web_info:itfResWeb) {
    console.log("checkbox传入的值: ", web_info)
    // 将当前行的已选组件置空
    select_role_info_tmp.value.containers = select_role_info_tmp.value.containers.filter(item => item.web_route !== web_info.web_route)
  }

  // 获取一次权限信息
  async function def_get_roles() {
    status_btn_role_get.value = true
    await getServer("/api/manage/get/role/dict", {"ok":"ok"}).then((res)=>{
      console.log("返回的所有角色: ", res)
      data_res_role_info.value = res as itfResRoleObj
      data_res_role_list.value = Object.values(data_res_role_info.value)
      to_roleinfo()
    }).catch((err)=>{
    })
    status_btn_role_get.value = false
  }

  // 获取所有用户的列表
  async function def_get_users() {
    status_btn_role_get.value = true
    await getServer("/api/manage/get/user/all", {"ok":"ok"}).then((res)=>{
      data_res_user_info.value = res as itfResUserList
    }).catch((err)=>{
    })
    status_btn_role_get.value = false
  }

  // 获取一次组信息
  async function def_get_groups() {
    status_btn_role_get.value = true
    // 同时获取一次组信息
    await getServer("/api/group/get", {"ok":"ok"}).then((res)=>{
      data_res_group_obj.value = res as itfResGroupObj
    }).catch((err)=>{
    })
    status_btn_role_get.value = false
  }

  // 获取所有菜单块的信息
  async function def_get_webs() {
    status_btn_role_get.value = true
    await getServer("/api/manage/web/get/dict", {"ok":"ok"}).then((res)=>{
      data_res_web_info.value = res as itfResWebObj
    }).catch((err)=>{
    })
    status_btn_role_get.value = false
  }

  // 获取所有后端接口
  async function def_get_apis() {
    status_btn_role_get.value = true
    await getServer("/api/manage/interface/get/dict", {"ok":"ok"}).then((res)=>{
      data_res_api_obj.value = res as itfResApiObj
      data_res_api_list.value = Object.values(data_res_api_obj.value).sort()
    }).catch((err)=>{
    })
    status_btn_role_get.value = false
  }

  // 检测url中是否传入了role_id参数, 有则跳转至该用户详情页
  function to_roleinfo() {
    let query_account:string | null | LocationQueryValue[] = route.query.role_id
    // console.log("url中带有参数: ", query_account)
    if (query_account && typeof query_account == 'string') {
      // console.log("识别query_account类型: ", typeof query_account, data_res_user_info.value)
      if (Object.keys(data_res_role_info.value).includes(query_account)) {
        // console.log("触发进入组详情页: ", query_account)
        def_role_detail(data_res_role_info.value[query_account])
      }
    }
  }

  // 修改url的query中group_id的函数
  function def_change_query_role_id(role_id:string="") {
    let tmp_query: { [key: string]: string | undefined } = { ...route.query, role_id: role_id}
    // 如果为空则删除这个group_id
    if (!role_id) {
      delete tmp_query.role_id
    }
    // push会被记录到浏览器历史记录, replace不会
    router.push({path: route.path, query: tmp_query})
  }

  // 点击新增角色按钮后做的准备工作
  function def_role_create_before() {
    // 置空数据
    data_req_role_create.value = {
      "role_id": "",
      "role_desc": "",
      "groups": [],
      "users": [],
      "apis": [],
      "webs": [],
      "containers": []
    }
    // 弹框
    status_win_role_create.value = true
  }

// 点击克隆角色按钮后做的准备工作
function def_role_clone_before(role_info:itfResRole) {
  // 克隆传入的角色的数据
  data_req_role_create.value = {
    "role_id": "",
    "role_desc": "",
    groups: role_info.groups.map(g => g.group_id),
    apis: role_info.apis.map(a => a.api_url),
    users: role_info.users.map(u => u.account),
    containers: role_info.containers.map(m => ({"web_route":m.web_route,"container_name":m.container_name})),
    webs: role_info.webs.map(w => w.web_route),
  }
  select_role_id.value = role_info.role_id
  // 弹框
  status_win_role_clone.value = true
}

  // 新增单个角色
  async function def_role_create() {
    status_btn_role_get.value = true
    await getServer("/api/manage/role/create", data_req_role_create.value).then((res)=>{
      // 弹框提示
      global_window("success", "新建角色 '"+data_req_role_create.value.role_id+" '成功")
      // 成功了就刷新一下数据
      def_get_roles()
      // 开启询问是否继续授权的弹窗
      status_win_role_update_ask.value = true
    }).catch((err)=>{
    })
    status_btn_role_get.value = false
    // 关弹窗
    status_win_role_create.value = false
  }

  // 新增角色成功后顺势前往赋权的函数
  function def_to_update() {
    select_breadcrumb.value = 'detail'
    // 这里要用深度复制
    select_role_info.value = {...data_res_role_info.value[data_req_role_create.value.role_id]}
    // 临时数据也来一份, 用于临时编辑
    def_role_info_init()
    // 更新选择的index
    // select_group_index.value = index
    select_role_id.value = select_role_info.value.role_id
    def_change_query_role_id(select_role_id.value)
    // 改为编辑状态
    def_role_edit()
    // 关闭弹窗
    status_win_role_update_ask.value = false
  }

  // 点击单个角色名或详情按钮时的操作
  function def_role_detail(role_info:itfResRole) {
    console.log("选择的角色: ", role_info)
    select_breadcrumb.value = 'detail'
    // 这里要用深度复制
    select_role_info.value = {...role_info}
    // 临时数据也来一份, 用于临时编辑 (这里不编辑, 就先不点了)
    // def_role_info_init()
    // 更新选择的index
    // select_group_index.value = index
    select_role_id.value = role_info.role_id
    def_change_query_role_id(select_role_id.value)
  }

  // 初始化单个角色编辑信息的函数
  function def_role_info_init() {
    // select_role_info_tmp.value = {...select_role_info.value}
    // 赋予临时变量值
    load_win_role_update.value = true
    select_role_info_tmp.value = {
      role_id: select_role_info.value.role_id,
      role_desc: select_role_info.value.role_desc,
      groups: select_role_info.value.groups.map(g => g.group_id),
      apis: select_role_info.value.apis.map(a => a.api_url),
      users: select_role_info.value.users.map(u => u.account),
      webs: select_role_info.value.webs.map(w => w.web_route),
      containers: select_role_info.value.containers.map(m => ({"web_route":m.web_route,"container_name":m.container_name})),
    }
    // 预选用户已有的api(如果有的话, 这里是针对的"还原数据"按钮)
    if (select_apis_before.value) {
      // 先清空
      select_apis_before.value!.clearSelection()
      // 再选则
      for (let i of select_role_info.value.apis) {
        select_apis_before.value!.toggleRowSelection(
            data_res_api_obj.value[i.api_url],
        )
      }
    }
    load_win_role_update.value = false
  }

  // 点击单个角色详情页编辑按钮的操作
  async function def_role_edit(){
    load_win_role_update.value = true
    // 开启编辑状态
    status_role_edit.value = true
    // 初始化需要编辑的数据
    def_role_info_init()
    // 获取用户信息和组信息和菜单块和后端接口
    await def_get_users()
    await def_get_groups()
    await def_get_webs()
    await def_get_apis()
    // 预选用户已有的api
    for (let i of select_role_info.value.apis) {
      select_apis_before.value!.toggleRowSelection(
          data_res_api_obj.value[i.api_url]
      )
    }
    load_win_role_update.value = false
  }

  // 取消单个组更改的函数
  function def_role_cancel_edit() {
    // 取消修状态
    status_role_edit.value = false
    // 还原数据, 这里要用深度赋值
    // 临时数据还原, 用于再次临时编辑
    def_role_info_init()
  }

  // 更新单个角色
  async function def_role_update() {
    status_btn_role_get.value = true
    await getServer("/api/manage/role/update", select_role_info_tmp.value).then((res)=>{
      // 弹框成功
      global_window("success", "更新角色 '"+select_role_info_tmp.value.role_id+"' 成功")
      // 成功了就刷新一下数据
      def_get_roles()
      // 成功了才关右侧弹窗
      status_role_edit.value = false
    }).catch((err)=>{
    })
    status_btn_role_get.value = false
  }

  // 点击单个角色的删除按钮的动作
  function def_role_delete_before(role_id:string) {
    select_role_id.value = role_id
    status_win_role_delete.value = true
  }

  // 删除单个角色
  async function def_role_delete() {
    status_btn_role_get.value = true
    await getServer("/api/manage/role/delete", {role_id: select_role_id.value}).then((res)=>{
      // 弹框成功
      global_window("success", "删除角色 '"+select_role_id.value+"' 成功")
      // 成功了就刷新一下数据
      def_get_roles()
      // 关闭弹窗
      status_win_role_delete.value = false
    }).catch((err)=>{
    })
    status_btn_role_get.value = false
  }

  // 回到组列表页的函数
  function def_to_roles() {
    // 同时取消编辑状态
    def_role_cancel_edit()
    select_breadcrumb.value = 'roles'
    def_change_query_role_id()
  }

  // 后端接口选择列表变化时的执行函数
  function def_select_change_apis(val:itfResApi[]) {
    select_role_info_tmp.value.apis = val.map(a => a.api_url)
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

  <!-- 角色总览 -->
  <el-card v-if="select_breadcrumb=='roles'" v-loading="status_btn_role_get">
    <!--style="&#45;&#45;el-table-border-color: white"-->
    <div style="margin-bottom: 20px">
      <el-button type="primary" @click="def_get_roles()">刷新</el-button>
      <el-button v-dcj="`新增`" type="success" @click="def_role_create_before()">新建角色</el-button>
      <el-input v-model="input_search_role" clearable style="width: 400px; margin-left: 20px"/>
    </div>
    <el-table
        :data="filter_show_role" height="500px" show-overflow-tooltip
        :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border
    >
      <el-table-column label="组名">
        <template #default="scope">
          <el-link @click="def_role_detail(scope.row)"><el-text type="primary">{{scope.row.role_id}}</el-text></el-link>
        </template>
      </el-table-column>
      <el-table-column label="被引用次数">
        <template #default="scope">
          <el-link @click="def_role_detail(scope.row)">
            <el-text type="primary">{{scope.row.users.length+scope.row.groups.length}}</el-text>
          </el-link>
        </template>
      </el-table-column>
      <el-table-column label="描述" prop="role_desc"/>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button plain size="small" type="primary" @click="def_role_detail(scope.row)">详情</el-button>
          <el-button v-dcj="`新增`" plain size="small" type="warning" @click="def_role_clone_before(scope.row)">克隆</el-button>
          <el-button v-dcj="`删除`" plain size="small" type="danger" @click="def_role_delete_before(scope.row.role_id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <!-- 新增角色的弹框, 这里不进行赋权, 而是询问进入详情页面 -->
  <el-dialog v-model="status_win_role_create" center title="新增角色">
    <el-form v-model="data_req_role_create" label-width="auto">
      <el-form-item label="角色名">
        <el-input v-model="data_req_role_create.role_id"/>
      </el-form-item>
      <el-form-item label="备注信息">
        <el-input v-model="data_req_role_create.role_desc" type="textarea" :autosize="{ minRows: 3, maxRows: 8 }"/>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="status_win_role_create = false" v-loading="status_btn_role_get">取消</el-button>
        <el-button type="success" @click="def_role_create()" v-loading="status_btn_role_get">新增</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 克隆角色的弹框, 这里不进行赋权, 而是询问进入详情页面 -->
  <el-dialog v-model="status_win_role_clone" center title="克隆角色">
    <el-form v-model="data_req_role_create" label-width="auto">
      <el-form-item label="角色名">
        <el-input v-model="data_req_role_create.role_id"/>
      </el-form-item>
      <el-form-item label="备注信息">
        <el-input v-model="data_req_role_create.role_desc" type="textarea" :autosize="{ minRows: 3, maxRows: 8 }"/>
      </el-form-item>
    </el-form>
    <template #footer>
      <div style="margin-bottom: 20px">
        <el-text type="info">*菜单块、后端接口将与 '{{select_role_id}}' 一致*</el-text>
      </div>
      <div class="dialog-footer">
        <el-button @click="status_win_role_clone = false" v-loading="status_btn_role_get">取消</el-button>
        <el-button type="success" @click="def_role_create()" v-loading="status_btn_role_get">新增</el-button>
      </div>
    </template>
  </el-dialog>

  <el-dialog v-model="status_win_role_update_ask" center title="是否前往授权">
    <el-alert title="创建角色成功, 是否继续对此角色授权" center :closable="false" type="success"/>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="status_win_role_update_ask = false" v-loading="status_btn_role_get">取消</el-button>
        <el-button type="primary" @click="def_to_update()" v-loading="status_btn_role_get">前往</el-button>
      </div>
    </template>
  </el-dialog>

  <el-dialog v-model="status_win_role_delete" title="删除角色" center width="400px">
    <div style="display: flex;justify-content: center">
      <el-text>确定删除角色 '</el-text>
      <el-text type="danger">{{select_role_id}}</el-text>
      <el-text>' 吗</el-text>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="status_win_role_delete = false" v-loading="status_btn_role_get">取消</el-button>
        <el-button type="danger" @click="def_role_delete()" v-loading="status_btn_role_get">确认删除</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 单个角色的展示页 -->
  <el-card v-if="select_breadcrumb=='detail'" v-loading="status_btn_role_get" style="min-height: 700px">
    <!-- 面包屑部分 -->
    <el-breadcrumb separator="/" class="breadcrumb_user">
      <el-breadcrumb-item>
        <a @click="def_to_roles"><el-text type="primary"><el-icon><ArrowLeftBold /></el-icon>角色列表</el-text></a>
      </el-breadcrumb-item>
      <el-breadcrumb-item>{{select_role_info.role_id}}</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 详情部分 -->
    <!--<el-descriptions :column="2" style="min-height: 200px">-->
    <!--  &lt;!&ndash; 自定义标题 &ndash;&gt;-->
    <!--  <template #title>-->
    <!--    <span class="title_user">{{ select_role_info.role_id }}</span>-->
    <!--    &lt;!&ndash; 修改功能的按钮图标 &ndash;&gt;-->
    <!--    <el-link :underline="false"><el-icon color="#409EFF" @click="def_group_edit()"><Edit /></el-icon></el-link>-->
    <!--  </template>-->
    <!--  &lt;!&ndash;<el-descriptions-item v-for="(v, k) in data_res_user_info[select_user_id]" :label="k">{{v}}</el-descriptions-item>&ndash;&gt;-->
    <!--  <el-descriptions-item label="组名">{{select_role_info.role_id}}</el-descriptions-item>-->
    <!--  <el-descriptions-item label="创建日期">{{def_fromat_date(select_role_info.date_create)}}</el-descriptions-item>-->
    <!--  <el-descriptions-item label="描述">-->
    <!--    <span v-if="!status_role_edit">{{select_role_info.role_desc}}</span>-->
    <!--    <el-input v-if="status_role_edit" size="small" type="textarea" v-model="select_role_info_tmp.role_desc" class="input_descriptions_long"/>-->
    <!--  </el-descriptions-item>-->
    <!--  <el-descriptions-item label="更新日期">{{def_fromat_date(select_role_info.date_update)}}</el-descriptions-item>-->
    <!--</el-descriptions>-->

    <span class="title_user">{{ select_role_info.role_id }}</span>
    <!-- 修改功能的按钮图标 -->
    <el-link v-dcj="`编辑`" :underline="false"><el-icon color="#409EFF" @click="def_role_edit()"><Edit /></el-icon></el-link>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-form>
          <el-form-item label="角色名">
            {{select_role_info.role_id}}
          </el-form-item>
          <el-form-item label="描述">
            <span>{{select_role_info.role_desc}}</span>
            <!--<el-input v-if="status_role_edit" size="small" type="textarea" v-model="select_role_info_tmp.role_desc" :autosize="{ minRows: 3, maxRows: 8 }"/>-->
          </el-form-item>
        </el-form>
      </el-col>
      <el-col :span="12">
        <el-form>
          <el-form-item label="创建日期">
            {{def_fromat_date(select_role_info.date_create)}}
          </el-form-item>
          <el-form-item label="更新日期">
            {{def_fromat_date(select_role_info.date_update)}}
          </el-form-item>
        </el-form>
      </el-col>
    </el-row>

    <!--{{data_user_list}}-->
    <!--<div v-if="status_role_edit" style="margin-bottom: 20px">-->
    <!--  &lt;!&ndash;<el-button type="warning" @click="def_groups_update()" :loading="status_btn_group_update">提交</el-button>&ndash;&gt;-->
    <!--  <el-button @click="def_role_cancel_edit()">取消</el-button>-->
    <!--</div>-->

    <el-tabs type="card" v-model="status_tab" class="tabs_user_role" >
      <el-tab-pane label="页面权限" name="webs" :lazy="true">
        <div style="margin-bottom: 20px">
          <el-button v-dcj="`编辑`" round type="primary" @click="def_role_edit()">调整</el-button>
          <!--<el-button round type="info">移除</el-button>-->
          <el-input v-model="input_search_web" clearable style="width: 400px; margin-left: 20px"/>
        </div>
        <el-table
            :data="filter_show_web" height="300px" scrollbar-always-on show-overflow-tooltip
            :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border
        >
          <el-table-column label="菜单路径" prop="web_route">
            <template #default="scope">
              <!--<el-link :href="`/home/setting/user_manage?account=`+scope.row.account">-->
              <!--  <el-text type="primary">{{scope.row.account}}</el-text>-->
              <!--</el-link>-->
              <router-link :to="{ path: '/home/setting/menu_manage', query: { web_route: scope.row.web_route } }" style="text-decoration: none">
                <el-link>
                  <el-text type="primary">{{scope.row.web_route}}</el-text>
                </el-link>
              </router-link>
            </template>
          </el-table-column>
          <el-table-column label="备注" prop="web_name"/>
          <el-table-column label="详细描述" prop="web_desc" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="菜单块" name="containers" :lazy="true">
        <div style="margin-bottom: 20px">
          <el-button v-dcj="`编辑`" round type="primary" @click="def_role_edit()">调整</el-button>
          <!--<el-button round type="info">移除</el-button>-->
          <el-input v-model="input_search_containers" clearable style="width: 400px; margin-left: 20px"/>
        </div>
        <el-table
            :data="filter_show_containers" height="300px" scrollbar-always-on show-overflow-tooltip
            :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border
        >
          <el-table-column label="菜单路径" prop="web_route">
            <template #default="scope">
              <!--<el-link :href="`/home/setting/user_manage?account=`+scope.row.account">-->
              <!--  <el-text type="primary">{{scope.row.account}}</el-text>-->
              <!--</el-link>-->
              <router-link :to="{ path: '/home/setting/menu_manage', query: { web_route: scope.row.web_route } }" style="text-decoration: none">
                <el-link>
                  <el-text type="primary">{{scope.row.web_route}}</el-text>
                </el-link>
              </router-link>
            </template>
          </el-table-column>
          <el-table-column label="唯一标识" prop="container_name">
            <template #default="scope">
              <!--<el-link :href="`/home/setting/user_manage?account=`+scope.row.account">-->
              <!--  <el-text type="primary">{{scope.row.account}}</el-text>-->
              <!--</el-link>-->
              <router-link :to="{ path: '/home/setting/menu_manage', query: { web_route: scope.row.web_route } }" style="text-decoration: none">
                <el-link>
                  <el-text type="primary">{{scope.row.container_name}}</el-text>
                </el-link>
              </router-link>
            </template>
          </el-table-column>
          <el-table-column label="详细描述" prop="container_desc" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="后端接口" name="apis" :lazy="true">
        <div style="margin-bottom: 20px">
          <el-button v-dcj="`编辑`" round type="primary" @click="def_role_edit()">调整</el-button>
          <!--<el-button round type="info">移除</el-button>-->
          <el-input v-model="input_search_api" clearable style="width: 400px; margin-left: 20px"/>
        </div>
        <el-table
            :data="filter_show_api" height="300px" scrollbar-always-on show-overflow-tooltip
            :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border
        >
          <el-table-column label="接口说明" prop="api_endpoint">
            <template #default="scope">
              <!--<el-link :href="`/home/setting/user_manage?account=`+scope.row.account">-->
              <!--  <el-text type="primary">{{scope.row.account}}</el-text>-->
              <!--</el-link>-->
              <el-link>
                <el-text type="primary">{{scope.row.api_endpoint}}</el-text>
              </el-link>
            </template>
          </el-table-column>
          <el-table-column label="接口路径" prop="api_url"/>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="所属组" name="groups" :lazy="true">
        <div style="margin-bottom: 20px">
          <el-button v-dcj="`编辑`" round type="primary" @click="def_role_edit()">调整</el-button>
          <!--<el-button round type="info">移除</el-button>-->
          <el-input v-model="input_search_group" clearable style="width: 400px; margin-left: 20px"/>
        </div>
        <el-table
            :data="filter_show_group" height="300px" scrollbar-always-on show-overflow-tooltip
            :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border
        >
          <el-table-column label="组名" prop="group_id">
            <template #default="scope">
              <!--<el-link :href="`/home/setting/user_manage?account=`+scope.row.account">-->
              <!--  <el-text type="primary">{{scope.row.account}}</el-text>-->
              <!--</el-link>-->
              <router-link :to="{ path: '/home/setting/group_manage', query: { group_id: scope.row.group_id } }" style="text-decoration: none">
                <el-link>
                  <el-text type="primary">{{scope.row.group_id}}</el-text>
                </el-link>
              </router-link>
            </template>
          </el-table-column>
          <el-table-column label="详细描述" prop="group_desc"/>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="所属用户" name="users" :lazy="true">
        <div style="margin-bottom: 20px">
          <el-button v-dcj="`编辑`" round type="primary" @click="def_role_edit()">调整</el-button>
          <!--<el-button round type="info">移除</el-button>-->
          <el-input v-model="input_search_select_user" clearable style="width: 400px; margin-left: 20px"/>
        </div>
        <el-table
            :data="filter_show_select_user" height="300px" scrollbar-always-on show-overflow-tooltip
            :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border
        >
          <el-table-column label="账号" prop="account">
            <template #default="scope">
              <!--<el-link :href="`/home/setting/user_manage?account=`+scope.row.account">-->
              <!--  <el-text type="primary">{{scope.row.account}}</el-text>-->
              <!--</el-link>-->
              <router-link :to="{ path: '/home/setting/user_manage', query: { account: scope.row.account } }" style="text-decoration: none">
                <el-link>
                  <el-text type="primary">{{scope.row.account}}</el-text>
                </el-link>
              </router-link>
            </template>
          </el-table-column>
          <el-table-column label="显示名" prop="displayname"/>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-drawer v-model="status_role_edit" size="90%" :title="`编辑 `+select_role_id" :loading="status_btn_role_get||load_win_role_update">
      <div v-loading="status_btn_role_get||load_win_role_update">
        <div style="float: right" >
          <el-button type="info" @click="def_role_info_init()">还原数据</el-button>
          <el-button type="success" @click="def_role_update()">提交修改</el-button>
        </div>
        <div class="title_edit_role">基本信息</div>
        <el-form v-model="select_role_info_tmp" label-width="auto">
          <el-form-item label="角色名">
            <el-input v-model="select_role_info_tmp.role_id" disabled/>
          </el-form-item>
          <el-form-item label="备注信息">
            <el-input v-model="select_role_info_tmp.role_desc" type="textarea" :autosize="{ minRows: 3, maxRows: 8 }"/>
          </el-form-item>
          <el-form-item label="赋予用户">
            <el-select multiple filterable v-model="select_role_info_tmp.users" clearable>
              <el-option v-for="(v, k) in data_res_user_info" :value="v.account" :key="v.account">
                <span style="float: left">{{ v.account }}</span>
                <span style="float: right;color: var(--el-text-color-secondary);font-size: 13px;">
                {{ v.displayname }}
              </span>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="赋予组">
            <el-select multiple filterable v-model="select_role_info_tmp.groups" clearable>
              <el-option v-for="(v, k) in data_res_group_obj" :label="v.group_id" :value="k" :key="k">
                <!--<span style="float: left">{{ k }}</span>-->
                <!--<span style="float: right;color: var(--el-text-color-secondary);font-size: 13px;">-->
                <!--  {{ v.group_desc }}-->
                <!--</span>-->
              </el-option>
            </el-select>
          </el-form-item>
        </el-form>

        <div class="title_edit_role">菜单块</div>
        <el-table
            :data="Object.values(data_res_web_info)" border scrollbar-always-on
            :header-cell-style="style_table_header"
        >
          <el-table-column label="页面" width="300px">
            <template #default="scope">
              <span>{{scope.row.web_name}}</span>
              <br>
              <span style="color: var(--el-text-color-secondary);font-size: 13px;">{{scope.row.web_route}}</span>
            </template>
          </el-table-column>
          <el-table-column label="读" width="60px">
            <template #default="scope">
              <el-checkbox-group v-model="select_role_info_tmp.webs">
                <el-checkbox :value="scope.row.web_route" @change="def_select_web_change(scope.row)"/>
              </el-checkbox-group>
            </template>
          </el-table-column>
          <el-table-column label="组件">
            <template #default="scope">
              <el-checkbox-group v-model="select_role_info_tmp.containers" >
                <el-checkbox
                    style="min-width: 200px" v-for="(v, k) in scope.row.container_list"
                    :value="{container_name:v.container_name,web_route:scope.row.web_route}"
                    :disabled="!select_role_info_tmp.webs.includes(scope.row.web_route)"
                >
                  <template #default="scope">
                    <el-tooltip v-if="v.container_desc" effect="light" placement="top-start">
                      <template #content>
                        <div style="max-width: 400px">
                          <div style="margin-bottom: 5px">
                            <el-text type="warning" size="large">{{k}}:</el-text>
                          </div>
                          <div style="margin-left: 10px">
                            <el-text type="warning">{{v.container_desc}}</el-text>
                          </div>
                        </div>
                      </template>
                      <span>{{k}}</span>
                    </el-tooltip>
                    <span v-else>{{k}}</span>
                  </template>
                </el-checkbox>
              </el-checkbox-group>
            </template>
          </el-table-column>
        </el-table>

        <!--<span>select_role_info_tmp</span><br>-->
        <!--<span>{{select_role_info_tmp}}</span><br>-->
        <!--<span>select_role_info</span><br>-->
        <!--<span>{{select_role_info}}</span><br>-->

        <div class="title_edit_role">后端接口</div>
        <el-table
            :data="data_res_api_list" border scrollbar-always-on ref="select_apis_before" max-height="700px"
            :header-cell-style="style_table_header" @selection-change="def_select_change_apis"
            style="width: 80%" show-overflow-tooltip
        >
          <el-table-column type="selection" width="55" />
          <el-table-column label="接口名" min-width="300px">
            <template #default="scope">
              <span>{{scope.row.api_endpoint}}</span>
            </template>
          </el-table-column>
          <el-table-column label="接口路径" min-width="400px">
            <template #default="scope">
              <span>{{scope.row.api_url}}</span>
            </template>
          </el-table-column>
        </el-table>

        <!--<span>data_res_role_info</span><br>-->
        <!--<span>{{data_res_role_info}}</span><br>-->
      </div>
    </el-drawer>

  </el-card>




</template>

<style scoped>
  .title_edit_role {
    font-size: 26px;
    margin-bottom: 20px;
    margin-top: 20px;
  }

  /*详情或备注的input框*/
  .input_descriptions {
    /*min-width: 50px;*/
    margin-right: 20px;
    max-width: 200px;
  }
  /*详情或备注的input框(长)*/
  .input_descriptions_long {
    /*min-width: 50px;*/
    margin-right: 20px;
    max-width: 500px;
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
  .tabs_user_role {
    height: 400px;
  }
  .transfer_user_role{
    --el-transfer-panel-width: 300px
  }
  .div_transfer {
    display: flex;
    justify-content: center;
  }

</style>