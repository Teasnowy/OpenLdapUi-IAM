<script setup lang="ts">
  import {type Ref, ref} from 'vue'
  import type {itfResLdapOus, itfResLdapOu, itfReqLdapOuUsers, itfResLdapOuUser, itfResLdapOuUsers, itfResLdapAttrs} from '@/api/itf_manage'
  import {userInfo} from "@/pinia/envs";
  import {global_window} from '@/api/def_feedback'
  import {getServer} from '@/api/def_servers'
  // import router from '@/router/router'
  import zihao from '@/assets/zihao.jpg'

  // 初始化全局变量
  let user_info = userInfo()


  // 获取当前所有组的信息的按钮状态
  let status_btn_get_ous:Ref<boolean> = ref(false)
  // 测试获取临时组的成员列表按钮的状态
  let status_btn_test_ous:Ref<boolean> = ref(false)
  // 更新ldap组信息按钮的状态
  let status_btn_update_ous:Ref<boolean> = ref(false)
  // 测试获取临时组成员后的弹出框状态
  let status_win_test_ous:Ref<boolean> = ref(false)
  // 新建ldap组的弹框状态
  let status_win_create_ous:Ref<boolean> = ref(false)
  // 新建ldap组的按钮状态(弹框内)
  let status_btn_create_ous:Ref<boolean> = ref(false)
  // 删除ldap组的弹框状态
  let status_win_delete_ous:Ref<boolean> = ref(false)
  // 删除ldap组的按钮状态(弹框内)
  let status_btn_delete_ous:Ref<boolean> = ref(false)


  // 存储当前所有组的变量
  let data_res_ous:Ref<itfResLdapOus> = ref({})
  // 存储供table展示的ldap用户列表
  let data_res_ldapUserList_tmp:Ref<itfResLdapOuUsers> = ref({
    users: {},
    attrs: {}
  })
  // 存储ldap属性映射关系的对象
  let obj_attrs:Ref<itfResLdapAttrs> = ref({})


  // 存储临时编辑现有组的信息的变量
  let data_ou_tmp_update:Ref<itfResLdapOu> = ref({})
  // 存储临时新建现有组的信息的变量
  let data_ou_tmp_create:Ref<itfResLdapOu> = ref({
    "as_account": "uid",
    "as_displayname": "displayname",
    "as_email": "mail",
    "as_password": "userpassword",
    "as_tel": "mobile",
    "can_login_directly": "",
    "description": "屹创研发部",
    "ou_base": "ou=Users,ou=yc,o=dusto,dc=dusto-yc,dc=com",
    "ou_name": "研发部",
    "ou_search": "(objectClass=inetOrgPerson)"
  })


  // 立刻获取一次当前所有组
  def_ous_get()
  // 当前选定的ldap组的名字
  let select_ou_name:Ref<string> = ref("")

  // 请求某搜索组中有效用户的请求信息
  let data_req_ouUsers:Ref<itfReqLdapOuUsers> = ref({
    ou_name: ""
  })
  // 后端返回某搜索组中有效用户的请求信息
  let data_res_ouUsers:Ref<itfResLdapOuUsers> = ref({
    users: {},
    attrs: {}
  })


  // 向后端请求当前所有组的函数
  async function def_ous_get() {
    status_btn_get_ous.value = true
    await getServer("/api/user/ldap/ous/manage/check", {"ok":"ok"}).then((res)=>{
      data_res_ous.value = res as itfResLdapOus
      console.log("获取到组列表: ", data_res_ous)
      // 如果当前已选定了某组, 则更新编辑区的临时信息
      if (select_ou_name.value) {
        def_create_ou_tmp(select_ou_name.value)
      }
    }).catch(()=>{
    })
    status_btn_get_ous.value = false
  }

  // 发起新建ldap组的函数
  async function def_ous_create() {
    status_btn_create_ous.value = true
    await getServer("/api/user/ldap/ous/manage/create", data_ou_tmp_create.value).then((res)=>{
      console.log("成功创建ldap组: ", data_ou_tmp_update.value.ou_name)
      // 更新一次所有组的信息
      def_ous_get()
      // 关闭弹窗
      status_win_create_ous.value = false
      global_window("success", "更新成功")
    }).catch(()=>{
    })
    status_btn_create_ous.value = false
  }

  // 发起更新ldap组的函数
  async function def_ous_update() {
    status_btn_update_ous.value = true
    await getServer("/api/user/ldap/ous/manage/update", data_ou_tmp_update.value).then((res)=>{
      console.log("成功更新ldap组: ", data_ou_tmp_update.value.ou_name)
      // 更新一次所有组的信息
      def_ous_get()
      global_window("success", "更新成功")
    }).catch(()=>{
    })
    status_btn_update_ous.value = false
  }

  // 删除ldap组的函数
  async function def_ous_delete(user_clear:boolean=false) {
    status_btn_delete_ous.value = true
    // if (user_clear) {
    //   let data_req_tmp = {ou_name: select_ou_name.value, user_clear}
    // } else {
    //   let data_req_tmp = {ou_name: select_ou_name.value}
    // }
    let data_req_tmp = {ou_name: select_ou_name.value, user_clear: user_clear}
    await getServer("/api/user/ldap/ous/manage/delete", data_req_tmp).then((res)=>{
      console.log("成功删除ldap组: ", select_ou_name.value)
      // 更新一次所有组的信息
      def_ous_get()
      global_window("success", "删除成功")
      status_win_delete_ous.value = false
    }).catch(()=>{
    })
    status_btn_delete_ous.value = false
  }

  // 克隆一个临时的ldap组的信息, 以供临时编辑方案信息
  // 这里使用函数被传入的值, 因为@click会运行在el-radio的v-model更新值之前, 造成报错
  function def_create_ou_tmp(ou_name:string) {
    console.log("赋予临时更新的值")
    // 将所选组的数据赋值给临时编辑的变量, 这里使用深度复制
    data_ou_tmp_update.value = {...data_res_ous.value[ou_name]}
  }

  // 根据输入的信息临时获取当前ldap组用户列表的函数
  async function def_test_ous(data_tmp:object) {
    status_btn_test_ous.value = true
    await getServer("/api/user/ldap/ous/manage/searchTmp", data_tmp).then((res)=>{
      data_res_ldapUserList_tmp.value = res as itfResLdapOuUsers
      obj_attrs.value = data_res_ldapUserList_tmp.value.attrs
      // 成功了才弹窗显示结果
      status_win_test_ous.value = true
    }).catch(()=>{
      // status_btn_test_ous.value = false
    })

    status_btn_test_ous.value = false
    console.log("结束测试")
  }



  // 排序函数, 对后端传来的ldap用户列表排序
  function userSort(obj1:itfResLdapOuUser, obj2:itfResLdapOuUser){
    // 按 a 属性排序
    if (obj1.is_exists !== obj2.is_exists) {
      return obj1.is_exists ? 1 : -1; // true 排前面，false 排后面 // 升序排序，a 数字越小越排在前面
    }

    // 如果 a 相同，按 b 属性排序
    // 按字母升序排序
    return obj1.dn.localeCompare(obj2.dn);
  }

  // ldap用户列表展示列表行

  let a = "aaa"
  let b = "bb"

</script>

<template>
  <!--{{data_ou_tmp_update}}-->
  <!--<br>-->
  <!--{{select_ou_name}}-->
  <!--<br>-->
  <!--{{data_res_ous}}-->
  <!--<br>-->

  <el-card class="card_ous_manage">
    <el-alert show-icon type="info" class="alert_card_head" :closable="false">LDAP方案组管理</el-alert>
    <el-form label-width="auto">
      <el-form-item label="选择已有方案" v-if="Object.keys(data_res_ous).length>0">
        <el-radio-group v-model="select_ou_name" fill="#E6A23C" :disabled="!user_info.inti_conf.ldap_status">
          <el-radio-button @click="def_create_ou_tmp(i.ou_name!)" v-for="i in data_res_ous" :value="i.ou_name">{{i.ou_name}}</el-radio-button>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="操作">
        <el-button v-dcj="`新增`" size="small" type="primary" @click="status_win_create_ous=true" :disabled="!user_info.inti_conf.ldap_status">新建ldap组</el-button>
        <el-button size="small" type="success" @click="def_ous_get" :loading="status_btn_get_ous" :disabled="!user_info.inti_conf.ldap_status">刷新</el-button>
      </el-form-item>
      <el-divider>编辑区</el-divider>
    </el-form>

    <el-empty v-if="!select_ou_name" :image="zihao" description="没有选择ldap组呢 ~"/>

    <el-form v-if="Object.keys(data_ou_tmp_update).length>0" inline label-width="auto">
      <el-form-item label="组名" >
        <el-input v-model="data_ou_tmp_update.ou_name" disabled class="input_ous"/>
      </el-form-item>
      <el-tooltip placement="bottom-end" content="在LDAP服务器中搜索的起始位置">
        <el-form-item label="搜索域" >
          <el-input v-model="data_ou_tmp_update.ou_base" class="input_ous"/>
        </el-form-item>
      </el-tooltip>
      <el-tooltip placement="bottom-end" content="搜索表达式, 与命令行中-b参数的格式一致">
        <el-form-item label="搜索表达式" >
          <el-input v-model="data_ou_tmp_update.ou_search" class="input_ous"/>
        </el-form-item>
      </el-tooltip>
      <el-form-item label="备注" >
        <el-input v-model="data_ou_tmp_update.description" class="input_ous"/>
      </el-form-item>
      <el-tooltip placement="bottom-end" content="如果为 '是' (暂不支持), 则不经管理员导入用户也能直接登录, 但只有登录一次后才会被收录至数据库">
        <el-form-item label="允许直接登录" >
          <el-radio-group v-model="data_ou_tmp_update.can_login_directly" class="input_ous">
            <!-- 这个选项先关了, 没有意义, 后端功能还没做, 没想好直接登录用dn还是账号名-->
            <el-radio-button value="yes" disabled>是</el-radio-button>
            <el-radio-button value="no">否</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-tooltip>
      <el-tooltip placement="bottom-end" content="账号在LDAP对应的属性名, 这个账号的值只有在导入用户时用作参考, 不具备使用价值">
        <el-form-item label="账号映射" >
          <el-input v-model="data_ou_tmp_update.as_account" class="input_ous"/>
        </el-form-item>
      </el-tooltip>
      <el-tooltip placement="bottom-end" content="显示名在LDAP对应的属性名">
        <el-form-item label="显示名映射" >
          <el-input v-model="data_ou_tmp_update.as_displayname" class="input_ous"/>
        </el-form-item>
      </el-tooltip>
      <el-tooltip placement="bottom-end" content="密码在LDAP对应的属性名">
        <el-form-item label="密码映射" >
          <el-input v-model="data_ou_tmp_update.as_password" class="input_ous"/>
        </el-form-item>
      </el-tooltip>
      <el-tooltip placement="bottom-end" content="手机号在LDAP对应的属性名">
        <el-form-item label="手机号映射" >
          <el-input v-model="data_ou_tmp_update.as_tel" class="input_ous"/>
        </el-form-item>
      </el-tooltip>
      <el-tooltip placement="bottom-end" content="邮箱在LDAP对应的属性名">
        <el-form-item label="邮箱映射" >
          <el-input v-model="data_ou_tmp_update.as_email" class="input_ous"/>
        </el-form-item>
      </el-tooltip>
    </el-form>
    <div v-if="select_ou_name">
      <el-button type="info" @click="def_create_ou_tmp(select_ou_name)">还原数据</el-button>
      <el-button type="success" :loading="status_btn_test_ous" @click="def_test_ous(data_ou_tmp_update)">测试连接</el-button>
      <el-button v-dcj="`编辑`" type="warning" :loading="status_btn_update_ous" @click="def_ous_update">提交修改</el-button>
      <el-button v-dcj="`删除`" type="danger" @click="status_win_delete_ous=true">删除方案</el-button>
    </div>
  </el-card>

  <!--<el-card>-->
  <!--  <el-alert show-icon type="info" class="alert_card_head">LDAP用户管理</el-alert>-->
  <!--</el-card>-->

  <!-- 弹框集合 -->

  <!-- 测试ldap组连通性时的弹框 -->
  <el-dialog v-model="status_win_test_ous" class="dialog_test_ou" width="80%">
    <!--{{data_res_ldapUserList_tmp}}-->
    <el-table :data="Object.values(data_res_ldapUserList_tmp.users).sort(userSort)" max-height="60vh">
      <el-table-column fixed width="200" prop="account" :label="`账号 (`+obj_attrs.account+`)`"/>
      <el-table-column show-overflow-tooltip min-width="500" prop="dn" label="dn" />
      <el-table-column show-overflow-tooltip width="200" prop="displayname" :label="`显示名 (`+obj_attrs.displayname+`)`"/>
      <el-table-column show-overflow-tooltip width="200" prop="email" :label="`邮箱 (`+obj_attrs.email+`)`"/>
      <el-table-column show-overflow-tooltip width="200" prop="tel" :label="`手机号 (`+obj_attrs.tel+`)`"/>
      <el-table-column show-overflow-tooltip width="200" prop="is_exists" label="是否已导入"/>
    </el-table>
  </el-dialog>

  <!-- 新建ldap组的弹框 -->
  <!-- 测试ldap组连通性时的弹框 -->
  <el-dialog v-model="status_win_create_ous" class="" width="50%">
    <!--{{data_ou_tmp_create}}-->
    <el-form label-width="auto" :model="data_ou_tmp_create">
      <el-form-item label="组名" >
        <el-input v-model="data_ou_tmp_create.ou_name" class="input_ous"/>
      </el-form-item>
      <el-form-item label="搜索域" >
        <el-tooltip placement="right-end" content="在LDAP服务器中搜索的起始位置">
          <el-input v-model="data_ou_tmp_create.ou_base" class="input_ous"/>
        </el-tooltip>
      </el-form-item>
      <el-form-item label="搜索表达式" >
        <el-tooltip placement="right-end" content="搜索表达式, 与命令行中-b参数的格式一致">
          <el-input v-model="data_ou_tmp_create.ou_search" class="input_ous"/>
        </el-tooltip>
      </el-form-item>
      <el-form-item label="备注" >
        <el-input v-model="data_ou_tmp_create.description" class="input_ous"/>
      </el-form-item>
      <el-form-item label="允许直接登录" >
        <el-tooltip placement="right-end" content="如果为 '是' (暂不支持), 则不经管理员导入用户也能直接登录, 但只有登录一次后才会被收录至数据库">
        <!--<el-input v-model="data_ou_tmp_update.can_login_directly" class="input_ous"/>-->
          <el-radio-group v-model="data_ou_tmp_create.can_login_directly" class="input_ous">
            <el-radio-button value="yes" disabled>是</el-radio-button>
            <el-radio-button value="no">否</el-radio-button>
          </el-radio-group>
        </el-tooltip>
      </el-form-item>
      <el-form-item label="账号映射" >
        <el-tooltip placement="right-end" content="账号在LDAP对应的属性名, 这个账号的值只有在导入用户时用作参考, 不具备使用价值">
          <el-input v-model="data_ou_tmp_create.as_account" class="input_ous"/>
        </el-tooltip>
      </el-form-item>
      <el-form-item label="显示名映射" >
        <el-tooltip placement="right-end" content="显示名在LDAP对应的属性名">
          <el-input v-model="data_ou_tmp_create.as_displayname" class="input_ous"/>
        </el-tooltip>
      </el-form-item>
      <el-form-item label="密码映射" >
        <el-tooltip placement="right-end" content="密码在LDAP对应的属性名">
          <el-input v-model="data_ou_tmp_create.as_password" class="input_ous"/>
        </el-tooltip>
      </el-form-item>
      <el-form-item label="手机号映射" >
        <el-tooltip placement="right-end" content="手机号在LDAP对应的属性名">
          <el-input v-model="data_ou_tmp_create.as_tel" class="input_ous"/>
        </el-tooltip>
      </el-form-item>
      <el-form-item label="邮箱映射" >
        <el-tooltip placement="right-end" content="邮箱在LDAP对应的属性名">
          <el-input v-model="data_ou_tmp_create.as_email" class="input_ous"/>
        </el-tooltip>
      </el-form-item>
      <el-button type="success" :loading="status_btn_test_ous" @click="def_test_ous(data_ou_tmp_create)">测试连接</el-button>
      <el-button type="primary" :loading="status_btn_create_ous" @click="def_ous_create()">创建</el-button>
      <el-button @click="status_win_create_ous=false">取消</el-button>
    </el-form>
  </el-dialog>

  <el-dialog v-model="status_win_delete_ous" class="dialog_delete_ou" width="400px" top="35vh">
    <div class="div_delete_ou_text">
      <el-text size="large">确定删除方案《</el-text>
      <el-text size="large" type="danger">{{select_ou_name}}</el-text>
      <el-text size="large">》吗 </el-text>
    </div>
    <div class="div_delete_ou_btn">
      <el-button type="danger" @click="def_ous_delete()">仅删除组</el-button>
      <el-button type="danger" @click="def_ous_delete(true)">一并删除该组用户</el-button>
      <el-button @click="status_win_delete_ous=false">取消</el-button>
    </div>
  </el-dialog>


</template>

<style scoped>

  .alert_card_head {
    margin-bottom: 10px;
  }

  .dialog_test_ou {
    /*height: 40vh;*/
    /*max-height: 80vh;*/
    overflow: auto;
  }

  .div_delete_ou_text {
    display: flex;            /* 设置为 Flex 容器 */
    justify-content: center;  /* 水平居中子元素 */
    align-items: center;      /* 垂直居中子元素 */
    /*margin: 20px;*/
    margin-bottom: 30px;
    /*flex-direction: column;   !* 子元素竖直排列 *!*/
  }

  .div_delete_ou_btn {
    display: flex;              /* 设置为 Flex 容器 */
    justify-content: space-between; /* 子元素分散在左右两边 */
    align-items: center;        /* 子元素上下居中 */
    padding-left: 40px;
    padding-right: 40px;
  }

  .input_ous {
    width: 300px;
  }

  .card_ous_manage {
    height: 600px;
    overflow: auto;
  }
  .div_collapse_title {
    background-color: #c5c1c1;
    /*color: coral;*/
    width: 100%;
  }
</style>