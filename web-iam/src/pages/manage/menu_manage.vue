<script setup lang="ts">
  import {type Ref, ref, computed} from 'vue'
  import {useRoute, useRouter, type LocationQueryValue, RouterLink} from 'vue-router'
  import type {itfResWebObj, itfResWeb, itfReqCtrAdd, itfResCtr, itfReqWebAdd, itfReqCtrUpd} from '@/api/itf_manage'
  import {Edit, CirclePlus, RefreshRight, ArrowLeftBold} from '@element-plus/icons-vue'
  import {userInfo} from "@/pinia/envs";
  import {global_window} from '@/api/def_feedback'
  import {getServer} from '@/api/def_servers'

  let route = useRoute();
  let router = useRouter()


  // 当前获取菜单时的状态
  let status_btn_web_get:Ref<boolean> = ref(false)
  // 存储后端返回的web信息
  let data_res_web_info:Ref<itfResWebObj> = ref({})
  // 存储后端返回的web列表
  let data_res_web_list:Ref<itfResWeb[]> = ref([])
  // 存储当前选择的web的id
  let select_web_route:Ref<string> = ref("")
  // 当前选中的web的container列表
  let select_web_container:Ref<itfResCtr[]> = ref([])
  // 当前页面展示哪些卡片
  let select_breadcrumb:Ref<"webs"|"detail"> = ref('webs')
  // 单个web详情页的编辑状态
  let status_web_edit:Ref<boolean> = ref(false)
  // 当前选定页面的更新状态
  let status_btn_web_update:Ref<boolean> = ref(false)
  // 详情页选定的tab页
  let status_tab:Ref<"container"> = ref('container')
  // 新增页面时的弹框状态
  let status_win_web_create:Ref<boolean> = ref(false)
  // 删除页面时的弹框状态
  let status_win_web_delete:Ref<boolean> = ref(false)
  // 批量新增指定页面的container的弹框状态
  let status_win_container_create:Ref<boolean> = ref(false)
  // 批量新增指定页面的container的列表
  let data_req_containers_create:Ref<itfReqCtrAdd[]> = ref([])
  // 修改单个container块时的弹窗状态
  let status_win_container_update:Ref<boolean> = ref(false)

  // 存储新增web的信息
  let data_req_web_create:Ref<itfReqWebAdd> = ref({
    "web_name": "",
    "web_route": "",
    "web_desc": "",
  })

  // 存储当前选择的web的详细信息, 用来展示
  let select_web_info:Ref<itfResWeb> = ref({
    "date_create": "",
    "date_update": "",
    "web_desc": "",
    "web_id": 0,
    "web_name": "",
    "web_route": "",
    "container_list": {}
  })
  // 存储当前选择的web的详细信息, 用来临时修改
  let select_web_info_tmp:Ref<itfResWeb> = ref({
    "date_create": "",
    "date_update": "",
    "web_desc": "",
    "web_id": 0,
    "web_name": "",
    "web_route": "",
    "container_list": {}
  })

  // 存储修改单个container时的临时信息
  let data_req_container_update:Ref<itfReqCtrUpd> = ref({
    "web_route": "",
    "container_desc": "",
    "container_name": "",
  })

  let input_search_web:Ref<string> = ref("")
  // 筛选指定web的container的计算函数
  const filter_show_web = computed(() =>
      data_res_web_list.value.filter(
          (data:itfResWeb) =>
              (!input_search_web.value || data.web_route.toLowerCase().includes(input_search_web.value.toLowerCase())) ||
              (!input_search_web.value || data.web_name.toLowerCase().includes(input_search_web.value.toLowerCase()))
          // console.log(select_date_work.value, data.date_work)
      )
  )

  let input_search_container:Ref<string> = ref("")
  // 筛选指定web的container的计算函数
  const filter_show_container = computed(() =>
      select_web_container.value.filter(
          (data:itfResCtr) =>
              (!input_search_container.value || data.container_name.toLowerCase().includes(input_search_container.value.toLowerCase())) ||
              (!input_search_container.value || data.container_desc.toLowerCase().includes(input_search_container.value.toLowerCase()))
          // console.log(select_date_work.value, data.date_work)
      )
  )

  //初始化数据
  def_get_webs()

  // 获取一次全部页面信息
  async function def_get_webs() {
    status_btn_web_get.value = true
    await getServer("/api/manage/web/get/dict", {"ok":"ok"}).then((res)=>{
      data_res_web_info.value = res as itfResWebObj
      data_res_web_list.value = Object.values(data_res_web_info.value)
      to_webinfo()
    }).catch((err)=>{
    })
    status_btn_web_get.value = false
  }

  // 新增单个页面的信息
  async function def_web_create(close:boolean=false) {
    status_btn_web_get.value = true
    await getServer("/api/manage/web/create", data_req_web_create.value).then((res)=>{
      global_window("success", "新增页面成功")
      // 重新获取一次数据
      def_get_webs()
    }).catch((err)=>{
    })
    // 还原编辑状态和数据
    def_web_cancel_edit()
    // 取消卡片转圈
    status_btn_web_get.value = false
    // 视情况关窗口
    if (close) {
      status_win_web_create.value = false
    }
  }

  // 更新单个页面的信息
  async function def_web_update() {
    status_btn_web_get.value = true
    await getServer("/api/manage/web/update", select_web_info_tmp.value).then((res)=>{
      global_window("success", "修改组信息成功")
      // 重新获取一次数据
      def_get_webs()
    }).catch((err)=>{
    })
    // 还原编辑状态和数据
    def_web_cancel_edit()
    // 取消卡片转圈
    status_btn_web_get.value = false
  }

  // 检测url中是否传入了web_route参数, 有则跳转至该用户详情页
  function to_webinfo() {
    let query_account:string | null | LocationQueryValue[] = route.query.web_route
    // console.log("url中带有参数: ", query_account)
    if (query_account && typeof query_account == 'string') {
      // console.log("识别query_account类型: ", typeof query_account, data_res_user_info.value)
      if (Object.keys(data_res_web_info.value).includes(query_account)) {
        // console.log("触发进入组详情页: ", query_account)
        def_web_detail(data_res_web_info.value[query_account])
      }
    }
  }

  // 修改url的query中web_route的函数
  function def_change_query_web_id(web_route:string="") {
    let tmp_query: { [key: string]: string | undefined } = { ...route.query, web_route: web_route}
    // 如果为空则删除这个group_id
    if (!web_route) {
      delete tmp_query.web_route
    }
    // push会被记录到浏览器历史记录, replace不会
    router.push({path: route.path, query: tmp_query})
  }

  // 点击单个组名或详情按钮时的操作
  function def_web_detail(web_info:itfResWeb) {
    console.log("选择的角色: ", web_info)
    select_breadcrumb.value = 'detail'
    // 这里要用深度复制
    select_web_info.value = {...web_info}
    // 再分析出一份当前选定web的container列表
    select_web_container.value = Object.values(select_web_info.value.container_list)
    // select_web_info.value = web_info
    // console.log("select_web_info: ", select_web_info)
    // 临时数据也来一份, 用于临时编辑
    def_web_info_init()
    // 更新选择的index
    // select_group_index.value = index
    select_web_route.value = web_info.web_route
    def_change_query_web_id(select_web_route.value)
  }

  // 点击删除按钮时做的操作
  function def_web_delete_before(web_info:itfResWeb) {
    // 更改选定的web
    select_web_info.value = web_info
    select_web_route.value = web_info.web_route
    // 弹框
    status_win_web_delete.value = true
  }

  // 删除指定的单个web的函数
  async function def_web_delete(web_route_tmp:string) {
    status_btn_web_get.value = true
    await getServer("/api/manage/web/delete", {"web_route": web_route_tmp}).then((res)=>{
      global_window("success", "删除web: "+web_route_tmp+" 成功")
      // 重新获取一次数据
      def_get_webs()
    }).catch((err)=>{
    })
    // 还原编辑状态和数据
    def_web_cancel_edit()
    // 取消卡片转圈
    status_btn_web_get.value = false
    // 关闭弹窗
    status_win_web_delete.value = false
  }

  // 初始化单个web编辑信息的函数
  function def_web_info_init() {
    select_web_info_tmp.value = {...select_web_info.value}
  }

  // 点击单个web详情页编辑按钮的操作
  function def_group_edit(){
    status_web_edit.value = true
  }

  // 取消单个web更改的函数
  function def_web_cancel_edit() {
    // 取消修状态
    status_web_edit.value = false
    // 还原数据, 这里要用深度赋值
    // 临时数据还原, 用于再次临时编辑
    def_web_info_init()
  }

  // 重置批量新增块数据
  function def_container_create_init() {
    data_req_containers_create.value = [{"container_name": "", "container_desc": ""}]
  }

  // 点击批量新增container按钮的操作
  function def_container_create_before() {
    // 重置为只有一行空数据
    def_container_create_init()
    // 弹框
    status_win_container_create.value = true
  }

  // 批量新增container时新增一行
  function def_container_create_addline() {
    data_req_containers_create.value.push({"container_name": "", "container_desc": ""})
  }

  // 批量新增container
  async function def_container_create() {
    status_btn_web_get.value = true
    let tmp_data = {
      "web_route": select_web_route.value,
      "container_list": data_req_containers_create.value
    }
    await getServer("/api/manage/containers/create", tmp_data).then((res)=>{
      global_window("success", "批量新增成功")
      // 重新获取一次数据
      def_get_webs()
      // 重置新增的临时数据
      def_container_create_init()
    }).catch((err)=>{
    })
    // 还原编辑状态和数据
    def_web_cancel_edit()
    // 取消卡片转圈
    status_btn_web_get.value = false
    // 关闭弹框
    status_win_container_create.value = false
  }

  // 点击单个container修改按钮时的动作
  function def_container_update_before(tmp_data:itfReqCtrUpd) {
    // 装填选中行的数据
    data_req_container_update.value.web_route = select_web_route.value
    data_req_container_update.value.container_name = tmp_data.container_name
    data_req_container_update.value.container_desc = tmp_data.container_desc
    // 弹框
    status_win_container_update.value = true
  }

  // 修改单个container
  async function def_container_update() {
    status_btn_web_get.value = true
    await getServer("/api/manage/container/update", data_req_container_update.value).then((res)=>{
      global_window("success", "更新块 '"+data_req_container_update.value.container_name+"' 成功")
      // 重新获取一次数据
      def_get_webs()
      // 关闭弹窗
      status_win_container_update.value = false
    }).catch((err)=>{
    })
    // 还原编辑状态和数据
    def_web_cancel_edit()
    // 取消卡片转圈
    status_btn_web_get.value = false
  }

  // 删除指定的多个container
  async function def_container_delete(l:Array<string>) {
    status_btn_web_get.value = true
    let tmp_data = {
      "web_route": select_web_route.value,
      "list_container_name": l
    }
    await getServer("/api/manage/containers/delete", tmp_data).then((res)=>{
      global_window("success", "删除块 '"+l+"' 成功")
      // 重新获取一次数据
      def_get_webs()
    }).catch((err)=>{
    })
    // 还原编辑状态和数据
    def_web_cancel_edit()
    // 取消卡片转圈
    status_btn_web_get.value = false
  }

  // 回到组列表页的函数
  function def_to_webs() {
    // 同时取消编辑状态
    def_web_cancel_edit()
    select_breadcrumb.value = 'webs'
    def_change_query_web_id()
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
  <el-card v-if="select_breadcrumb=='webs'">
    <!--style="&#45;&#45;el-table-border-color: white"-->
    <div style="margin-bottom: 20px">
      <el-button type="primary" @click="def_get_webs()">刷新</el-button>
      <el-button v-dcj="`新增`" type="success" @click="status_win_web_create=true">新增页面</el-button>
      <el-input v-model="input_search_web" clearable style="width: 400px; margin-left: 20px"/>
    </div>
    <el-table
        :data="filter_show_web" height="500px" show-overflow-tooltip
        :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border
    >
      <el-table-column label="路径" min-width="200px">
        <template #default="scope">
          <el-link @click="def_web_detail(scope.row)"><el-text type="primary">{{scope.row.web_route}}</el-text></el-link>
        </template>
      </el-table-column>
      <!--<el-table-column label="别名">-->
      <!--  <template #default="scope">-->
      <!--    <el-link @click="def_web_detail(scope.row)"><el-text type="primary">{{scope.row.web_name}}</el-text></el-link>-->
      <!--  </template>-->
      <!--</el-table-column>-->
      <el-table-column label="别名" prop="web_name"/>
      <el-table-column label="描述" prop="web_desc" min-width="300px"/>
      <el-table-column label="操作" width="200px">
        <template #default="scope">
          <el-button plain size="small" type="primary" @click="def_web_detail(scope.row)">详情</el-button>
          <el-button v-dcj="`删除`" plain size="small" type="danger" @click="def_web_delete_before(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <!-- 单个角色的展示页 -->
  <el-card v-if="select_breadcrumb=='detail'" v-loading="status_btn_web_get" style="min-height: 700px">
    <!--{{select_web_info}}-->
    <!-- 面包屑部分 -->
    <el-breadcrumb separator="/" class="breadcrumb_user">
      <el-breadcrumb-item>
        <a @click="def_to_webs()"><el-text type="primary"><el-icon><ArrowLeftBold /></el-icon>页面列表</el-text></a>
      </el-breadcrumb-item>
      <el-breadcrumb-item>{{select_web_info.web_route}}</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 详情部分 -->
    <!--<el-descriptions :column="2" style="min-height: 200px">-->
    <!--  &lt;!&ndash; 自定义标题 &ndash;&gt;-->
    <!--  <template #title>-->
    <!--    <span class="title_user">{{ select_web_info.web_route }}</span>-->
    <!--    &lt;!&ndash; 修改功能的按钮图标 &ndash;&gt;-->
    <!--    <el-link :underline="false"><el-icon color="#409EFF" @click="def_group_edit()"><Edit /></el-icon></el-link>-->
    <!--  </template>-->
    <!--  &lt;!&ndash;<el-descriptions-item v-for="(v, k) in data_res_user_info[select_user_id]" :label="k">{{v}}</el-descriptions-item>&ndash;&gt;-->
    <!--  <el-descriptions-item label="路由">{{select_web_info.web_route}}</el-descriptions-item>-->
    <!--  <el-descriptions-item label="创建日期">{{def_fromat_date(select_web_info.date_create)}}</el-descriptions-item>-->
    <!--  <el-descriptions-item label="别名">-->
    <!--    <span v-if="!status_web_edit">{{select_web_info.web_name}}</span>-->
    <!--    <el-input v-if="status_web_edit" size="small" v-model="select_web_info_tmp.web_name" class="input_descriptions"/>-->
    <!--  </el-descriptions-item>-->
    <!--  <el-descriptions-item label="更新日期">{{def_fromat_date(select_web_info.date_update)}}</el-descriptions-item>-->
    <!--  <el-descriptions-item label="描述" width="50%">-->
    <!--    &lt;!&ndash;<div class="input_descriptions_long">&ndash;&gt;-->
    <!--    &lt;!&ndash;  <span v-if="!status_web_edit" >{{select_web_info.web_desc}}</span>&ndash;&gt;-->
    <!--    &lt;!&ndash;  <el-input v-if="status_web_edit" size="small" type="textarea" v-model="select_web_info_tmp.web_desc"/>&ndash;&gt;-->
    <!--    &lt;!&ndash;</div>&ndash;&gt;-->
    <!--    <span v-if="!status_web_edit" style="width: 200px">{{select_web_info.web_desc}}</span>-->
    <!--    <el-input v-if="status_web_edit" size="small" type="textarea" v-model="select_web_info_tmp.web_desc" class="input_descriptions_long"/>-->
    <!--  </el-descriptions-item>-->
    <!--  <el-descriptions-item>-->

    <!--  </el-descriptions-item>-->
    <!--</el-descriptions>-->
    <span class="title_user">{{ select_web_info.web_route }}</span>
    <el-link v-dcj="`编辑`" :underline="false"><el-icon color="#409EFF" @click="def_group_edit()"><Edit /></el-icon></el-link>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-form>
          <el-form-item label="路由">
            {{select_web_info.web_route}}
          </el-form-item>
          <el-form-item label="别名">
            <!--{{select_web_info.web_name}}-->
            <span v-if="!status_web_edit" >{{select_web_info.web_name}}</span>
            <el-input v-if="status_web_edit" size="small" v-model="select_web_info_tmp.web_name" :maxlength="30" style="max-width: 300px"/>
          </el-form-item>
          <el-form-item label="描述">
            <span v-if="!status_web_edit" >{{select_web_info.web_desc}}</span>
            <el-input v-if="status_web_edit" size="small" type="textarea" v-model="select_web_info_tmp.web_desc" :autosize="{ minRows: 3, maxRows: 8 }"/>
          </el-form-item>
        </el-form>
      </el-col>
      <el-col :span="12">
        <el-form>
          <el-form-item label="创建日期">
            {{def_fromat_date(select_web_info.date_create)}}
          </el-form-item>
          <el-form-item label="更新日期">
            {{def_fromat_date(select_web_info.date_update)}}
          </el-form-item>
        </el-form>
      </el-col>
    </el-row>

    <!--{{data_user_list}}-->
    <div v-if="status_web_edit" style="margin-bottom: 20px">
      <el-button type="warning" @click="def_web_update()" :loading="status_btn_web_update">提交</el-button>
      <el-button @click="def_web_cancel_edit()">取消</el-button>
    </div>

    <!-- 展示块列表 -->
    <el-tabs type="card" v-model="status_tab" class="tabs_user_role" >
      <el-tab-pane label="块管理" name="container" :lazy="true">
        <div style="margin-bottom: 20px">
          <!--<el-button round type="danger" @click="">批量删除</el-button>-->
          <el-button v-dcj="`编辑`" round type="primary" @click="def_container_create_before()">批量新增</el-button>
          <el-input v-model="input_search_container" clearable style="width: 400px; margin-left: 20px"></el-input>
          <!--<el-button round type="info">移除</el-button>-->
        </div>
        <el-table
            :data="filter_show_container" height="300px" scrollbar-always-on
            :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border
        >
          <el-table-column label="唯一标识" prop="account">
            <template #default="scope">
              <el-link>
                <el-text type="primary">{{scope.row.container_name}}</el-text>
              </el-link>
            </template>
          </el-table-column>
          <el-table-column label="备注" prop="container_desc"/>
          <el-table-column label="操作" width="150px">
            <template #default="scope">
              <el-button v-dcj="`编辑`" plain size="small" type="warning" @click="def_container_update_before(scope.row)">修改</el-button>
              <el-button v-dcj="`编辑`" plain size="small" type="danger" @click="def_container_delete([scope.row.container_name])">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </el-card>

  <!-- 新增web页面时的弹窗 -->
  <el-dialog v-model="status_win_web_create" title="新增页面" center>
    <!--<el-alert title="新增页面" :closable="false" center style="margin-bottom: 20px;"/>-->
    <el-form v-model="data_req_web_create" label-width="auto">
      <el-form-item label="页面名称">
        <el-input v-model="data_req_web_create.web_name"/>
      </el-form-item>
      <el-form-item label="唯一路径">
        <el-input v-model="data_req_web_create.web_route"/>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="data_req_web_create.web_desc" type="textarea" :autosize="{ minRows: 3, maxRows: 8 }"/>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="status_win_web_create = false">取消</el-button>
        <el-button type="success" @click="def_web_create(true)">新增并关闭</el-button>
        <el-button type="warning" @click="def_web_create()">新增并继续</el-button>
      </div>
    </template>
  </el-dialog>

  <el-dialog v-model="status_win_web_delete" center title="删除页面" width="500px">
    <div style="display: flex;flex-direction: column">
      <div style="display: flex;justify-content: center;">
        <el-text>确认删除路径为'</el-text>
        <el-text type="danger">{{select_web_route}}</el-text>
        <el-text>'的页面吗?</el-text>
      </div>
      <el-text type="warning">所属的菜单块也会一并被删除</el-text>
    </div>
    <template #footer>
      <el-text type="info">* 仅删除配置信息, 不会删除实际页面</el-text>
      <div class="dialog-footer">
        <el-button @click="status_win_web_create = false">取消</el-button>
        <el-button type="danger" @click="def_web_delete(select_web_route)">删除</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 批量新增指定web页面container的弹窗 -->
  <el-dialog v-model="status_win_container_create" title="批量新增块" center>
    <el-table
        :data="data_req_containers_create"
        :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border
    >
      <el-table-column label="唯一标识" width="350px">
        <template #default="scope">
          <el-input v-model="scope.row.container_name" size="large"/>
        </template>
      </el-table-column>
      <el-table-column label="备注">
        <template #default="scope">
          <el-input v-model="scope.row.container_desc" type="textarea" :autosize="{ minRows: 1.4, maxRows: 4 }"/>
        </template>
      </el-table-column>
    </el-table>
    <el-button style="width: 100%;margin-top: 20px" @click="def_container_create_addline" :icon="CirclePlus" text type="primary">新增空白行</el-button>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="status_win_container_create = false">取消</el-button>
        <el-button type="success" @click="def_container_create()">批量新增</el-button>
      </div>
    </template>
  </el-dialog>

  <el-dialog v-model="status_win_container_update" title="修改块" center>
    <el-form v-model="data_req_container_update" label-width="auto">
      <el-form-item label="页面唯一路径">
        <el-input v-model="data_req_container_update.web_route" disabled/>
      </el-form-item>
      <el-form-item label="块唯一标识">
        <el-input v-model="data_req_container_update.container_name" disabled/>
      </el-form-item>
      <el-form-item label="块备注">
        <el-input v-model="data_req_container_update.container_desc" type="textarea" :autosize="{ minRows: 3, maxRows: 8 }"/>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="status_win_container_update = false">取消</el-button>
        <el-button type="warning" @click="def_container_update()">提交修改</el-button>
      </div>
    </template>
  </el-dialog>


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
    max-width: 80%;
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