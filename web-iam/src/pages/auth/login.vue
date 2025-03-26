<script setup lang="ts">
  import {type Ref, ref, reactive} from 'vue'
  import {getServer} from '@/api/def_servers'
  import {global_window, window_right} from '@/api/def_feedback'
  import {type res_login, type req_login, type req_singup, type res_user_init, type res_ok} from '@/api/itf_auth'
  import {before_router, router_left} from '@/router/router'
  import {userInfo} from "@/pinia/envs";


  let user_info = userInfo()

  let ldap_auth_status = ref(true)
  // 获取初始化信息
  let data_config:Ref<res_user_init> = ref({
    list_ous: [],
    must_email: true,
    must_tel: true,
    ldap_status: true,
    forget_passwd_ldap: false,
    ldap_modify_oneself: false,
    image_auth: ''
  })

  def_init().then(()=>{
    ldap_auth_status.value = data_config.value.ldap_status && data_config.value.list_ous.length > 0;
  }).catch(()=>{})



  // 当前的操作类型
  let action_type: Ref<'login'|'singup'|'fPasswd'> = ref('login')
  // 获取本地缓存的用户类型
  let cache_user_type = localStorage.getItem('yukikaze_user_befrom') || 'local'
  if (!['ldap', 'local'].includes(cache_user_type)) {
    cache_user_type = 'local'
  }
  // 验证方式
  // let sign_type:Ref<'passwd'|'sms'> = ref('passwd')
  console.log(data_config)
  // 用户登录时的请求信息
  let data_request_login:req_login = reactive({
    user_account: '',
    user_password: '',
    user_type: cache_user_type as 'local'|'ldap',
    sign_type: 'passwd',
    ou_name: '',
  })

  // 登录中的等待状态
  let load_auth:Ref<boolean> = ref(false)
  // 标识注册状态的变量
  let status_singup:Ref<boolean> = ref(false)
  // 标识是否发送了短信验证码的变量
  let status_sendcode_sms:Ref<boolean> = ref(false)
  // 标识是否发送了邮箱验证码的变量
  let status_sendcode_email:Ref<boolean> = ref(false)


  // 获取初始化信息
  async function def_init() {
    let res_init:any = await getServer('/api/user/init', {"ok": 'ok'})
    data_config.value = res_init as res_user_init
    // 给组选项加上默认值
    data_request_login.ou_name = data_config.value.list_ous[0] || ''

    // 设置壁纸的路径
    let ele = document.getElementById('background');
    if (ele) {
      // console.log('更新了壁纸')
      if (data_config.value.image_auth) {
        ele.style.backgroundImage = "url('"+data_config.value.image_auth+"')"
      } else {
        // const imgPath = require('../../../public/monv.jpg');
        ele.style.backgroundImage = "url('/yaogun.jpg')"
      }

    }

  }

  // 发送邮箱验证码的函数
  async function def_sendcode_email(email:string) {
    await getServer('/api/email/send/code', {"email": email})
    global_window("success", '邮箱验证码发送成功')
  }

  // 发送短信验证码的函数
  async function def_sendcode_sms(tel:string) {
    await getServer('/api/sms/send/code', {"tel": tel})
    global_window("success", '短信验证码发送成功')
  }

  // 点击'返回登录'按钮的操作
  function def_to_login() {
    action_type.value = "login"
  }
  // 用户向后端发起登录请求的函数
  async function def_login() {
    let status_auth = false
    load_auth.value = true
    try {
      const res_login_tmp = await getServer('/api/user/login', data_request_login)
      // console.log('登录返回: ', res_login_tmp)
      let res_login = res_login_tmp as res_login
      // 将jwt和用户信息保存至浏览器本地
      localStorage.setItem('yukikaze_user_jwt', res_login.res_jwt||"")
      localStorage.setItem('yukikaze_user_account', res_login.user_info.account||"")
      localStorage.setItem('yukikaze_user_displayname', res_login.user_info.displayname||"")
      localStorage.setItem('yukikaze_user_photo', res_login.user_photo_base64||"")
      // 保存此次登录的用户类型
      localStorage.setItem('yukikaze_user_befrom', data_request_login.user_type)
      // 更新pinia
      user_info.update_jwt()
      // console.log("返回用户名: ", res_login.user_info.account)
      // console.log("pinia用户名: ", user_info.account)

      // const res_menus = await getServer('/api/manage/get/user/menus', {"ok": "ok"})
      // user_info.menus = res_menus as {[key:string]: Array<string>}
      // console.log("登录后已上传menus: ", user_info.menus)

      // 注册指令

      // app.use(dir)

      window_right("success", "欢迎归来, 我的大人")
      user_info.update_menus()
      await before_router()
      // 跳转到首页
      window.location.replace('/');
      // await router_left.push('/').then(()=>{
      //   window.location.reload()
      // }).catch(()=>{})
      // await router_left.replace('/')
      console.log(user_info.account, "登录成功")

    } catch (e) {
      load_auth.value = false
    }
    load_auth.value = false

    if (status_auth) {
      // 弹框庆祝
      }
    }

  // 登录成功的弹窗
  function hello() {

  }

  // 点击'注册用户'按钮的操作
  function def_to_singup() {
    // 这里要分辨是本地用户还是ldap, ldap需要去其他页面
    if (data_request_login.user_type=='local') {
      // window.location.href = '/#/auth/singup';
      router_left.push('/auth/singup')
    } else if (data_request_login.user_type=='ldap') {
      global_window('error', '暂时不支持注册ldap用户')
    } else {
      global_window('error', '暂时不支持的用户类型')
    }
  }

  // 点击'忘记密码'时做的动作
  function def_to_fPasswd() {
    // /auth/passwdForget
    // 这里要分辨是本地用户还是ldap, ldap需要去其他页面
    if (data_request_login.user_type=='local') {
      // window.location.href = '/#/auth/passwdForget';
      router_left.push('/auth/passwdForget')
    } else if (data_request_login.user_type=='ldap') {
      if (data_config.value.forget_passwd_ldap) {
        router_left.push('/auth/passwdForget')
      } else {
        global_window('error', '暂时不支持LDAP用户修改密码')
      }

    } else {
      global_window('error', '暂时不支持的用户类型')
    }
  }


</script>

<template>
  <!--{{ data_config }}-->
  <!--{{ data_request_login }}-->
  <div class="background_login" id="background">
    <el-card class="card_right" v-loading="load_auth">
      <div class="div_select">
        <el-radio-group v-model="data_request_login.user_type" fill="#67C23A" size="small">
          <el-radio-button label="本地用户" value="local"/>
          <el-radio-button label="LDAP用户" value="ldap"/>
        </el-radio-group>
      </div>

      <!-- 本地用户登录框 -->
      <!--{{ldap_auth_status}}-->
      <!--{{data_config}}-->
      <div class="div_ipput" v-if="data_request_login.user_type=='local'">
        <el-input size="large" v-model="data_request_login.user_account">
          <template #prefix><el-text>账号</el-text></template>
        </el-input>
        <el-input size="large" v-model="data_request_login.user_password" type="password" show-password @keyup.enter="def_login">
          <template #prefix><el-text>密码</el-text></template>
        </el-input>
      </div>
      <!-- ldap用户允许登录时 -->
      <div class="div_ipput" v-if="data_request_login.user_type=='ldap' && data_config.ldap_status">
        <el-input size="large" v-model="data_request_login.user_account">
          <template #prefix><el-text>账号</el-text></template>
        </el-input>
        <el-input size="large" v-model="data_request_login.user_password" type="password" show-password @keyup.enter="def_login">
          <template #prefix><el-text>密码</el-text></template>
        </el-input>
      </div>
      <!-- ldap用户不允许登录时 -->
      <div style="margin-bottom: 20px" v-if="data_request_login.user_type=='ldap' && !data_config.ldap_status">
        <el-alert center type="error" :closable="false">管理员没有开启LDAP登录</el-alert>
      </div>
      <!-- 管理员没有配置有效的LDAP组 -->
      <div style="margin-bottom: 20px" v-if="data_request_login.user_type=='ldap' && data_config.list_ous.length < 1 && data_config.ldap_status">
        <el-alert center type="error" :closable="false">管理员没有配置有效的LDAP组</el-alert>
      </div>

      <div class="div_action" v-if="data_request_login.user_type=='local' || ldap_auth_status">
        <el-button @click="def_to_singup" type="primary" size="large" plain style="width: 150px">注册</el-button>
        <el-button @click="def_login" type="primary" size="large" style="width: 150px">登录</el-button>
        <!--<el-button @click="def_to_fPasswd" type="danger">忘记密码</el-button>-->
      </div>

      <div class="div_forget">
        <el-text @click="def_to_fPasswd" type="danger" text cursor style="cursor:pointer">忘记密码?</el-text>
      </div>

      <!--{{ data_request_login }}-->

    </el-card>
  </div>

</template>

<style scoped>
  /* 右边操作区卡片样式 */
  .card_right {
    display: flex;
    justify-content: center;
    width: 400px;
    height: 400px;
    /*max-height: 80vh;*/
    margin-top: 200px;
    margin-left: 60%;
    /*padding: 20px;*/
    overflow-y: auto;
    z-index: 1;
    position: relative;
  }

  .div_select{
    margin-bottom: 20px;
    width: 100%;
    display: flex;
    justify-content: center;
  }

  .div_ipput {
    display: flex;
    flex-direction: column;
    gap: 10px;
    /*padding: 10px;*/
    margin-bottom: 10px;
  }

  .div_action {
    margin-bottom: 20px;
    width: 100%;
    display: flex;
    justify-content: space-between;
  }

  .div_forget {
    position: absolute; /* 设置子元素为绝对定位 */
    bottom: 0; /* 底部对齐 */
    right: 0; /* 右侧对齐 */
    width: 100px;
    height: 50px;
    /*background-color: coral;*/
    text-align: center;
    /*line-height: 20px;*/
    color: white;
  }

  /*.background_login {*/
  /*  height: calc(100vh);*/
  /*  background-attachment: fixed; !* local是随容器滚动, fixed是永远固定 *!*/
  /*  background-image: url("@/assets/monv.jpg");*/
  /*  background-size: cover;*/
  /*  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);*/
  /*  border-radius: 10px;*/
  /*  backdrop-filter: blur(10px);*/
  /*}*/

  .background_login {
    height: 100vh;
    /*background-color: #8c939d;*/
    /*background-image: url("@/assets/monv.jpg");*/
    display: flex;
    background-size: cover;
  }

  .background_login:before {
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 0;
    background-attachment: fixed;
    background-image: url("@/assets/shachuangkuai.png");
    /*background-image: url();*/
  }

</style>