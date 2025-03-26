<script setup lang="ts">
import {computed, type Ref, ref} from 'vue'
  import {type LocationQueryValue, useRoute, useRouter, RouterLink} from 'vue-router'
import type {
  itfResUserList,
  itfResRoleObj,
  itfResGroupObj,
  itfResGroup,
  itfReqGroupAdd, itfResRole, itfResUserInfo
} from '@/api/itf_manage'
  import {Edit, CirclePlus, RefreshRight, ArrowLeftBold} from '@element-plus/icons-vue'
  import {userInfo} from "@/pinia/envs";
  import {global_window} from '@/api/def_feedback'
  import {getServer} from '@/api/def_servers'

  // 获取路由
  let route = useRoute();
  let router = useRouter()

  // 存储后端返回的对象
  let data_res_group_obj:Ref<itfResGroupObj> = ref({})
  // 存储后端返回的组列表
  let data_res_group_list:Ref<itfResGroup[]> = ref([])
  // 存储后端返回的用户列表
  let data_res_user_info:Ref<itfResUserList> = ref({})
  // 存储后端返回的权限列表
  let data_res_role_info:Ref<itfResRoleObj> = ref({})
  // 刷新组列表的按钮的状态
  let status_btn_group_get:Ref<boolean> = ref(false)
  // 刷新用户数据按钮的状态
  let status_btn_user_get:Ref<boolean> = ref(false)
  // 刷新权限数据按钮的状态
  let status_btn_role_get:Ref<boolean> = ref(false)
  // 更新单个组信息的按钮状态
  let status_btn_group_update:Ref<boolean> = ref(false)
  // 存储当前是否展示组的详情页
  let select_breadcrumb:Ref<string> = ref('groups')
  // 存储详情页的编辑状态
  let status_group_edit:Ref<boolean> = ref(false)
  // 控制组详情页下部标签页的状态
  let status_tab:Ref<"users"|"roles"> = ref("users")
  // 存储当前选择的组的index
  let select_group_index:Ref<number> = ref(0)
  // 存储当前选择的组的id
  let select_group_id:Ref<string> = ref("")

  // 存储当前新建组的弹框的状态
  let status_win_group_create:Ref<boolean> = ref(false)
  // 存储当前用户选择穿梭框的状态的变量
  let status_win_adduser:Ref<boolean> = ref(false)
  // 存储当前规则选择穿梭框的状态的变量
  let status_win_addrole:Ref<boolean> = ref(false)

  // 存储当前选择的组的数据
  let select_group:Ref<itfResGroup> = ref({
    group_id: "", group_desc: "", date_create: "", date_update: "",
    roles: [], users: []
  })
  // 存储当前选择的组的副本, 用来提交修改
  let select_group_tmp:Ref<itfReqGroupAdd> = ref({
    group_id: "", group_desc: "",
    roles: [], users: []
  })
  // 存储新建组的变量
  let data_req_create:Ref<itfReqGroupAdd> = ref({
    group_id: "", group_desc: "",
    roles: [], users: []
  })


  // 立刻获取一次组列表
  def_get_groups()

  let input_search_group:Ref<string> = ref("")
  // 筛选组的计算函数
  const filter_show_group = computed(() =>
      data_res_group_list.value.filter(
          (data:itfResGroup) =>
              (!input_search_group.value || data.group_id.toLowerCase().includes(input_search_group.value.toLowerCase())) ||
              (!input_search_group.value || data.group_desc.toLowerCase().includes(input_search_group.value.toLowerCase()))
          // console.log(select_date_work.value, data.date_work)
      )
  )

  let input_search_select_user:Ref<string> = ref("")
  // 筛选指定组的用户的计算函数
  const filter_show_select_user = computed(() =>
      select_group.value.users.filter(
          (data) =>
              (!input_search_select_user.value || data.account.toLowerCase().includes(input_search_select_user.value.toLowerCase())) ||
              (!input_search_select_user.value || data.displayname.toLowerCase().includes(input_search_select_user.value.toLowerCase()))
          // console.log(select_date_work.value, data.date_work)
      )
  )

  let input_search_select_role:Ref<string> = ref("")
  // 筛选指定组的角色的计算函数
  const filter_show_select_role = computed(() =>
      select_group.value.roles.filter(
          (data) =>
              (!input_search_select_role.value || data.role_id.toLowerCase().includes(input_search_select_role.value.toLowerCase())) ||
              (!input_search_select_role.value || data.role_desc.toLowerCase().includes(input_search_select_role.value.toLowerCase()))
          // console.log(select_date_work.value, data.date_work)
      )
  )

  // 获取一次组信息
  async function def_get_groups() {
    status_btn_group_get.value = true
    // 同时获取一次组信息
    await getServer("/api/group/get", {"ok":"ok"}).then((res)=>{
      data_res_group_obj.value = res as itfResGroupObj
      data_res_group_list.value = Object.values(data_res_group_obj.value)
      if (data_res_group_list.value.length > 0) {
        // 为当前选择的组信息赋值
        if ( select_group_id.value ) {
          select_group.value = data_res_group_obj.value[select_group_id.value]
        }
        // 看网页上有没有带的参数指明组
        to_groupinfo()
      }
    }).catch((err)=>{
    })
    status_btn_group_get.value = false
  }

  // 获取所有用户的列表
  async function def_get_users() {
    status_btn_user_get.value = true
    await getServer("/api/manage/get/user/all", {"ok":"ok"}).then((res)=>{
      data_res_user_info.value = res as itfResUserList
    }).catch((err)=>{
    })
    status_btn_user_get.value = false
  }

  // 获取一次权限信息
  async function def_get_roles() {
    status_btn_role_get.value = true
    await getServer("/api/manage/get/role/dict", {"ok":"ok"}).then((res)=>{
      data_res_role_info.value = res as itfResRoleObj
    }).catch((err)=>{
    })
    status_btn_role_get.value = false
  }

  // 检测url中是否传入了group_id参数, 有则跳转至该用户详情页
  function to_groupinfo() {
    let query_account:string | null | LocationQueryValue[] = route.query.group_id
    // console.log("url中带有参数: ", query_account)
    if (query_account && typeof query_account == 'string') {
      // console.log("识别query_account类型: ", typeof query_account, data_res_user_info.value)
      if (Object.keys(data_res_group_obj.value).includes(query_account)) {
        // console.log("触发进入组详情页: ", query_account)
        def_group_detail(data_res_group_obj.value[query_account])
      }
    }
  }

  // 修改url的query中group_id的函数
  function def_change_query_group_id(group_id:string="") {
    let tmp_query: { [key: string]: string | undefined } = { ...route.query, group_id: group_id}
    // 如果为空则删除这个group_id
    if (!group_id) {
      delete tmp_query.group_id
    }
    // push会被记录到浏览器历史记录, replace不会
    router.push({path: route.path, query: tmp_query})
  }

  // 点击单个组名或详情按钮时的操作
  function def_group_detail(group_info:itfResGroup) {
    console.log("选择的组: ", group_info)
    select_breadcrumb.value = 'detail'
    // 这里要用深度复制
    select_group.value = {...group_info}
    // 临时数据也来一份, 用于临时编辑
    def_user_init()
    // 更新选择的index
    // select_group_index.value = index
    select_group_id.value = group_info.group_id
    def_change_query_group_id(select_group_id.value)
  }

  // 点击单个组详情页编辑按钮的操作
  function def_group_edit(){
    status_group_edit.value = true
  }

  // 取消单个组更改的函数
  function def_group_cancel_edit() {
    // 取消修状态
    status_group_edit.value = false
    // 还原数据, 这里要用深度赋值
    // 临时数据还原, 用于再次临时编辑
    def_user_init()
  }

  // 还原用户列表的函数
  function def_user_init() {
    select_group_tmp.value.group_id = select_group.value.group_id
    select_group_tmp.value.group_desc = select_group.value.group_desc
    select_group_tmp.value.users = select_group.value.users.map(u => u.account)
    select_group_tmp.value.roles = select_group.value.roles.map(r => r.role_id)
  }

  // 点击克隆按钮时的操作
  async function def_groups_clone(group_info_tmp:itfResGroup) {
    // 将传入的信息覆盖初始新建信息
    // data_req_create.value.group_id = group_info_tmp.group_id
    data_req_create.value.group_desc = group_info_tmp.group_desc
    data_req_create.value.users = group_info_tmp.users.map(u => u.account)
    data_req_create.value.roles = group_info_tmp.roles.map(u => u.role_id)
    // 发起新增
    await def_groups_create_before()
  }

  // 点击新增组按钮时执行的操作
  async function def_groups_create_before() {
    status_btn_group_get.value = true
    // 获取一次用户列表和角色列表
    await def_get_roles()
    await def_get_users()
    // 弹框
    status_win_group_create.value = true
    status_btn_group_get.value = false
  }

  // 新增一个组的函数
  async function def_groups_create() {
    status_btn_group_get.value = true
    await getServer("/api/group/create", data_req_create.value).then((res)=>{
      global_window("success", "成功新建组")
      // 重新获取一次数据
      def_get_groups()
      status_win_group_create.value = false
    }).catch((err)=>{
    })
    status_btn_group_get.value = false
  }

  // 删除一个组的函数
  async function def_groups_delete(group_id:string) {
    status_btn_group_get.value = true
    await getServer("/api/group/delete", {"group_id": group_id}).then((res)=>{
      global_window("success", "成功删除组")
      // 重新获取一次数据
      def_get_groups()
      status_win_group_create.value = false
    }).catch((err)=>{
    })
    status_btn_group_get.value = false
  }

  // 更新单个组信息的函数
  async function def_groups_update() {
    status_btn_group_get.value = true
    await getServer("/api/group/update", select_group_tmp.value).then((res)=>{
      global_window("success", "修改组信息成功")
      // 重新获取一次数据
      def_get_groups()
    }).catch((err)=>{
    })
    // 回到组首页 (先不回)
    // def_to_groups()
    status_btn_group_get.value = false
    status_group_edit.value = false
    // 关闭更新组的相关弹框
    status_win_adduser.value = false
    status_win_addrole.value = false

  }

  // 点击添加用户按钮时的操作
  async function def_adduser_begin() {
    status_win_adduser.value = true
    await def_get_users()
  }

  // 点击添加角色按钮时的操作
  async function def_addrole_begin() {
    status_win_addrole.value = true
    await def_get_roles()
  }

  // 回到组列表页的函数
  function def_to_groups() {
    // 同时取消编辑状态
    def_group_cancel_edit()
    select_breadcrumb.value = 'groups'
    def_change_query_group_id()
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
  <!-- 用户组本身管理 -->
  <el-card v-if="select_breadcrumb=='groups'" v-loading="status_btn_group_get">
    <!--style="&#45;&#45;el-table-border-color: white"-->
    <div style="margin-bottom: 20px">
      <el-button type="primary" @click="def_get_groups()">刷新</el-button>
      <el-button v-dcj="`新增`" type="success" @click="def_groups_create_before()">新建组</el-button>
      <el-input v-model="input_search_group" clearable style="width: 400px; margin-left: 20px"/>
    </div>
    <el-table
        :data="filter_show_group" height="500px" show-overflow-tooltip
        :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border
    >
      <el-table-column label="组名">
        <template #default="scope">
          <el-link @click="def_group_detail(scope.row)"><el-text type="primary">{{scope.row.group_id}}</el-text></el-link>
        </template>
      </el-table-column>
      <el-table-column label="用户数量">
        <template #default="scope">
          <el-link @click="def_group_detail(scope.row)"><el-text type="primary">{{scope.row.users.length}}</el-text></el-link>
        </template>
      </el-table-column>
      <el-table-column label="描述" prop="group_desc"/>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button plain size="small" type="primary" @click="def_group_detail(scope.row)">详情</el-button>
          <el-button v-dcj="`新增`" plain size="small" type="warning" @click="def_groups_clone(scope.row)">克隆</el-button>
          <el-button v-dcj="`删除`" plain size="small" type="danger" @click="def_groups_delete(scope.row.group_id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!--{{select_group_tmp}}-->
  </el-card>


  <!-- 单个用户组详情展示部分 -->
  <el-card v-if="select_breadcrumb=='detail'" v-loading="status_btn_group_get" style="min-height: 700px">
    <!-- 面包屑部分 -->
    <el-breadcrumb separator="/" class="breadcrumb_user">
      <el-breadcrumb-item>
        <a @click="def_to_groups"><el-text type="primary"><el-icon><ArrowLeftBold /></el-icon>组列表</el-text></a>
      </el-breadcrumb-item>
      <el-breadcrumb-item>{{select_group.group_id}}</el-breadcrumb-item>
    </el-breadcrumb>
    <!--{{select_group_tmp}}-->
    <!-- 详情部分-->
    <!--<el-descriptions :column="2" style="min-height: 200px">-->
    <!--  &lt;!&ndash; 自定义标题 &ndash;&gt;-->
    <!--  <template #title>-->
    <!--    <span class="title_user">{{ select_group.group_id }}</span>-->
    <!--    &lt;!&ndash; 修改功能的按钮图标 &ndash;&gt;-->
    <!--    <el-link :underline="false"><el-icon color="#409EFF" @click="def_group_edit()"><Edit /></el-icon></el-link>-->
    <!--  </template>-->
    <!--  &lt;!&ndash;<el-descriptions-item v-for="(v, k) in data_res_user_info[select_user_id]" :label="k">{{v}}</el-descriptions-item>&ndash;&gt;-->
    <!--  <el-descriptions-item label="组名">{{select_group.group_id}}</el-descriptions-item>-->
    <!--  <el-descriptions-item label="创建日期">{{def_fromat_date(select_group.date_create)}}</el-descriptions-item>-->
    <!--  <el-descriptions-item label="备注">-->
    <!--    <span v-if="!status_group_edit">{{select_group.group_desc}}</span>-->
    <!--    <el-input v-if="status_group_edit" size="small" type="textarea" v-model="select_group_tmp.group_desc" class="input_descriptions_long"/>-->
    <!--  </el-descriptions-item>-->
    <!--  <el-descriptions-item label="更新日期">{{def_fromat_date(select_group.date_update)}}</el-descriptions-item>-->
    <!--</el-descriptions>-->

    <span class="title_user">{{ select_group.group_id }}</span>
    <!-- 修改功能的按钮图标 -->
    <el-link v-dcj="`编辑`" :underline="false"><el-icon color="#409EFF" @click="def_group_edit()"><Edit /></el-icon></el-link>

    <el-row :gutter="20">
      <el-col :span="12" style="margin-top: 20px">
        <el-form>
          <el-form-item label="组名">
            {{select_group.group_id}}
          </el-form-item>
          <el-form-item label="备注">
            <span v-if="!status_group_edit">{{select_group.group_desc}}</span>
            <el-input v-if="status_group_edit" size="small" type="textarea" v-model="select_group_tmp.group_desc" :autosize="{ minRows: 3, maxRows: 8 }"/>
          </el-form-item>
        </el-form>
      </el-col>
      <el-col :span="12">
        <el-form>
          <el-form-item label="创建日期">
            {{def_fromat_date(select_group.date_create)}}
          </el-form-item>
          <el-form-item label="更新日期">
            {{def_fromat_date(select_group.date_update)}}
          </el-form-item>
        </el-form>
      </el-col>
    </el-row>

    <!--{{data_user_list}}-->
    <div v-if="status_group_edit" style="margin-bottom: 20px">
      <el-button type="warning" @click="def_groups_update()" :loading="status_btn_group_update">提交</el-button>
      <el-button @click="def_group_cancel_edit()">取消</el-button>
    </div>
    <!--{{select_group_tmp}}-->

    <!-- 选择角色和组成员的卡片区 -->
    <el-tabs type="card" v-model="status_tab" class="tabs_user_role" >
      <el-tab-pane label="用户管理" name="users" :lazy="true">
        <div style="margin-bottom: 20px">
          <el-button v-dcj="`编辑`" round type="primary" @click="def_adduser_begin">成员调整</el-button>
          <!--<el-button round type="info">移除</el-button>-->
          <el-input v-model="input_search_select_user" clearable style="width: 400px; margin-left: 20px"/>
        </div>
        <el-table
            :data="filter_show_select_user" height="300px" scrollbar-always-on
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
      <el-tab-pane label="权限管理" name="rbac" :lazy="true">
        <div style="margin-bottom: 20px">
          <el-button v-dcj="`编辑`" round type="primary" @click="def_addrole_begin">角色调整</el-button>
          <!--<el-button round type="info">移除</el-button>-->
          <el-input v-model="input_search_select_role" clearable style="width: 400px; margin-left: 20px"/>
        </div>
        <el-table
            :data="filter_show_select_role" height="300px"
            :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border
        >
          <el-table-column label="权限名" prop="role_id">
            <template #default="scope">
              <router-link :to="{ path: '/home/setting/rbac_manage', query: { role_id: scope.row.role_id } }" >
                <el-link>
                  <el-text type="primary">{{scope.row.role_id}}</el-text>
                </el-link>
              </router-link>
            </template>
          </el-table-column>
          <el-table-column label="备注" prop="role_desc"/>
        </el-table>
      </el-tab-pane>
    </el-tabs>

  </el-card>

  <!-- 修改用户的弹窗 -->
  <el-dialog v-model="status_win_adduser" :before-close="def_user_init()" align-center >
    <!--{{select_group_tmp.users}}-->
    <el-container class="div_transfer" v-loading="status_btn_group_get">
      <el-transfer
          :data="Object.values(data_res_user_info)" v-model="select_group_tmp.users" v-loading="status_btn_user_get"
          :props="{key: 'account'}" :left-default-checked="select_group_tmp.users" filterable destroy-on-close
          :button-texts="['移除', '添加']" :titles="['未添加', '已添加']" style="" class="transfer_user_role"
      >
        <template #default="{ option }">
        <span>
          <el-text>{{ option.account }}</el-text>
          <el-tooltip placement="right-start" effect="light" :content="option.displayname">
            <el-text size="small" type="info">&nbsp;&nbsp;&nbsp;&nbsp;{{ option.displayname }}</el-text>
          </el-tooltip>

        </span>

        </template>
      </el-transfer>
    </el-container>

    <!--底部按钮-->
    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" @click="def_groups_update()" :loading="status_btn_group_get">应用</el-button>
        <el-button @click="status_win_adduser=false" :loading="status_btn_group_get">取消</el-button>
      </div>
    </template>
  </el-dialog>


  <!-- 修改权限的弹窗 -->
  <el-dialog v-model="status_win_addrole" :before-close="def_user_init()" align-center >
    <!--{{select_group_tmp.users}}-->
    <el-container class="div_transfer" v-loading="status_btn_group_get">
      <el-transfer
          :data="Object.values(data_res_role_info)" v-model="select_group_tmp.roles" v-loading="status_btn_role_get"
          :props="{key: 'role_id'}" :left-default-checked="select_group_tmp.roles" filterable destroy-on-close
          :button-texts="['移除', '添加']" :titles="['未添加', '已添加']" style="" class="transfer_user_role"
      >
        <template #default="{ option }">
        <span>
          <el-text>{{ option.role_id }}</el-text>
          <el-tooltip placement="right-start" effect="light" :content="option.role_desc">
            <el-text size="small" type="info">&nbsp;&nbsp;&nbsp;&nbsp;{{ option.role_desc }}</el-text>
          </el-tooltip>

        </span>

        </template>
      </el-transfer>
    </el-container>

    <!--底部按钮-->
    <template #footer>
      <div class="dialog-footer">

        <el-button type="primary" @click="def_groups_update()" :loading="status_btn_group_get">应用</el-button>
        <el-button @click="status_win_addrole=false" :loading="status_btn_group_get">取消</el-button>
      </div>
    </template>
  </el-dialog>

  <!--新增用户组的弹窗-->
  <el-dialog v-model="status_win_group_create">
    <el-form label-width="auto" v-model="data_req_create" v-loading="status_btn_role_get||status_btn_user_get||status_btn_group_get">
      <el-form-item label="组名">
        <el-input v-model="data_req_create.group_id" style="width: 200px"/>
      </el-form-item>
      <el-form-item label="详细描述">
        <el-input v-model="data_req_create.group_desc" type="textarea"/>
      </el-form-item>
      <el-form-item label="选择用户">
        <el-select multiple filterable v-model="data_req_create.users">
          <el-option v-for="(v, k) in data_res_user_info" :label="v.displayname" :value="k" :key="k">
            <span style="float: left">{{ v.displayname }}</span>
            <span style="float: right;color: var(--el-text-color-secondary);font-size: 13px;">
              {{ k }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="选择角色">
        <el-select multiple filterable v-model="data_req_create.roles">
          <el-option v-for="i in Object.keys(data_res_role_info)" :label="i" :value="i" :key="i"/>
        </el-select>
      </el-form-item>
      <el-button v-loading="status_btn_group_get" type="success" @click="def_groups_create()">新建</el-button>
      <el-button v-loading="status_btn_group_get" @click="status_win_group_create=false">取消</el-button>
    </el-form>

  </el-dialog>

  <!--{{ data_res_group_obj }}-->


</template>

<style scoped>
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
    /*margin-bottom: 40px;*/
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