<script setup lang="ts">
  import {type Ref, ref} from 'vue'
  import photoUpload from '@/components/photoUpload.vue'
  import photoUploadZip from '@/components/photoUploadZip.vue'
  import type {req_update_userinfo, res_user_init, req_update_passwd} from '@/api/itf_auth'
  import {userInfo} from "@/pinia/envs";
  import {global_window} from '@/api/def_feedback'
  import {getServer} from '@/api/def_servers'
  import {router_left} from '@/router/router'


  // 初始化全局变量
  let user_info = userInfo()
  // 获取初始化信息
  let data_config:Ref<res_user_init> = ref({
    list_ous: [],
    must_email: true,
    must_tel: true,
    ldap_status: false,
    forget_passwd_ldap: false,
    ldap_modify_oneself: false,
  })
  def_init()

  // 修改个人信息按钮的状态
  let status_btn_userinfo:Ref<boolean> = ref(false)
  // 修改密码按钮的状态
  let status_btn_passwd:Ref<boolean> = ref(false)

  // 发送邮箱验证码的按钮的状态
  let status_btn_email:Ref<boolean> = ref(false)
  // 重发邮箱验证码按钮的显示文本
  let btn_title_countdown_email:Ref<string> = ref("发送验证码")
  // 发送邮箱验证码的状态
  let isCounting_email:Ref<boolean> = ref(false)
  // 发送邮箱验证码的时间间隔
  let countdown_max_email:number = 60
  // 发送邮箱验证码当前倒计时的数字
  let countdown_email:Ref<number> = ref(countdown_max_email)

  // 发送短信验证码的按钮的状态
  let status_btn_sms:Ref<boolean> = ref(false)
  // 重发短信验证码按钮的显示文本
  let btn_title_countdown_sms:Ref<string> = ref("发送验证码")
  // 发送短信验证码的状态
  let isCounting_sms:Ref<boolean> = ref(false)
  // 发送短信验证码的时间间隔
  let countdown_max_sms:number = 60
  // 发送短信验证码当前倒计时的数字
  let countdown_sms:Ref<number> = ref(countdown_max_sms)

  // 用户修改密码时, 输入的密码1
  let input_passwd_1:Ref<string> = ref("")
  // 用户修改密码时, 输入的密码2
  let input_passwd_2:Ref<string> = ref("")

  // 更新个人信息用的请求信息
  let data_request_update:Ref<req_update_userinfo> = ref({
    user_account: user_info.account,
    user_displayname: user_info.displayname,
    tel: user_info.tel,
    email: user_info.email,
    code_tel_input: "",
    code_email_input: "",
    user_type: user_info.befrom
  })

  // 更新密码的请求信息
  let data_req_passwd:Ref<req_update_passwd> = ref({
    "user_type": user_info.befrom,
    "user_account": user_info.account,
    "user_password_old": "",
    "user_password_new": ""
  })

  // 更新个人信息的函数
  async function def_update_userinfo() {
    let url_path = ''
    if (user_info.befrom == 'local') {
      url_path = '/api/user/update/info/local'
    } else if (user_info.befrom == 'ldap' && data_config.value.ldap_modify_oneself) {
      url_path = '/api/user/update/info/local'
    } else {
      global_window("error", "仅本地用户支持直接修改个人信息")
      return
    }
    status_btn_userinfo.value = true
    await getServer(url_path, data_request_update.value).then(()=>{
      global_window("success", "个人信息修改成功")
      user_info.displayname = data_request_update.value.user_displayname
      user_info.tel = data_request_update.value.tel
      user_info.email = data_request_update.value.email
      status_btn_userinfo.value = false
    }).catch(()=>{
      global_window("error", "个人信息修改失败")
      status_btn_userinfo.value = false
    })
  }

  // 更新本地用户密码的函数
  async function def_update_passwd() {

    // 基本的校验
    if (input_passwd_1.value !== input_passwd_2.value) {
      global_window("error", "两次密码不一致")
      return
    }

    let url_path = ''
    if (user_info.befrom == 'local') {
      url_path = '/api/user/update/passwd/local/useold'
      data_req_passwd.value.user_password_new = input_passwd_2.value
    } else if (user_info.befrom == 'ldap' && data_config.value.ldap_modify_oneself) {
      url_path = '/api/user/update/passwd/local/useold'
      data_req_passwd.value.user_password_new = input_passwd_2.value
    } else {
      global_window("error", "仅本地用户支持直接修改密码")
      return
    }

    status_btn_passwd.value = true
    await getServer(url_path, data_req_passwd.value).then(()=>{
      global_window("success", "密码修改成功")
      status_btn_passwd.value = false
    }).catch(()=>{
      global_window("error", "密码修改失败")
      status_btn_passwd.value = false
    })
  }

  // 发送邮箱验证码的函数
  async function def_sendcode_email(email:string) {
    status_btn_email.value = true
    await getServer('/api/email/send/code', {"email": email}).then(()=>{
      global_window("success", '邮箱验证码发送成功')
      startCountdown_email()
    }).catch(()=>{
      // 发送失败则立刻解开按钮
      status_btn_email.value = false
    })
  }

  // 发送短信验证码的函数
  async function def_sendcode_sms(tel:string) {
    status_btn_sms.value = true
    await getServer('/api/sms/send/code', {"tel": tel}).then(()=>{
      startCountdown_sms()
      global_window("success", '短信验证码发送成功')
    }).catch(()=>{
      // 发送失败则立刻解开按钮
      status_btn_sms.value = false
    })
  }

  // 发送短信验证码的倒计时
  function startCountdown_sms() {
    if (isCounting_sms.value) return; // 如果正在倒计时，直接返回
    isCounting_sms.value = true; // 设置为正在倒计时

    const interval = setInterval(() => {
      if (countdown_sms.value > 0) {
        countdown_sms.value--; // 每秒减少倒计时
        btn_title_countdown_sms.value = countdown_sms.value+" 秒后重发"
      } else {
        clearInterval(interval); // 倒计时结束，清除定时器
        isCounting_sms.value = false; // 设置为未倒计时状态
        countdown_sms.value = countdown_max_sms; // 重置倒计时（可以根据需求调整）
        btn_title_countdown_sms.value = "发送验证码"
        // 解开按钮
        status_btn_sms.value = false
      }
    }, 1000); // 每秒更新一次
  }

  // 发送邮箱验证码的倒计时
  function startCountdown_email() {
    if (isCounting_email.value) return; // 如果正在倒计时，直接返回
    isCounting_email.value = true; // 设置为正在倒计时

    const interval = setInterval(() => {
      if (countdown_email.value > 0) {
        countdown_email.value--; // 每秒减少倒计时
        btn_title_countdown_email.value = countdown_email.value+" 秒后重发"
      } else {
        clearInterval(interval); // 倒计时结束，清除定时器
        isCounting_email.value = false; // 设置为未倒计时状态
        countdown_email.value = countdown_max_email; // 重置倒计时（可以根据需求调整）
        btn_title_countdown_email.value = "发送验证码"
        // 解开按钮
        status_btn_email.value = false
      }
    }, 1000); // 每秒更新一次
  }

  // 获取初始化信息
  async function def_init() {
    let res_init:any = await getServer('/api/user/init', {"ok": 'ok'})
    data_config.value = res_init as res_user_init
  }

</script>

<template>
  <!--{{data_request_update}}-->
  <!-- 修改头像的卡片 -->
  <el-card class="card_main">
    <el-alert show-icon type="info" class="alert_card_head" :closable="false">修改头像</el-alert>
    <photoUploadZip/>
  </el-card>

  <!-- 修改个人信息的卡片 -->
  <el-card class="card_main">
    <el-alert show-icon type="info" class="alert_card_head" :closable="false">更新个人信息</el-alert>
    <el-form label-width="auto" class="form_userinfo" :disabled="user_info.befrom!='local' && !data_config.ldap_modify_oneself">
      <el-form-item label="账号">
        <el-input v-model="data_request_update.user_account" disabled></el-input>
      </el-form-item>
      <el-form-item label="显示名">
        <el-input v-model="data_request_update.user_displayname" ></el-input>
      </el-form-item>
      <!-- 如果获取的init配置中需要强制验证手机号, 则增加发送短信的按钮 -->
      <el-form-item label="&nbsp;&nbsp;&nbsp;&nbsp;手机号码" v-if="data_config.must_tel">
        <el-col :span="16">
          <el-input v-model="data_request_update.tel" ></el-input>
        </el-col>
        <el-col :span="8">
          <el-button
              v-if="data_request_update.email!=user_info.email"
              @click="def_sendcode_sms(data_request_update.tel)" :disabled="status_btn_sms"
              :loading="isCounting_sms" type="warning"
          >{{btn_title_countdown_sms}}</el-button>
        </el-col>
      </el-form-item>
      <el-form-item label="&nbsp;&nbsp;&nbsp;&nbsp;手机号码" v-if="!data_config.must_tel">
        <el-input v-model="data_request_update.tel" ></el-input>
      </el-form-item>
      <el-form-item label="手机验证码" v-if="data_config.must_tel && data_request_update.email!=user_info.email">
        <el-input v-model="data_request_update.code_tel_input" ></el-input>
      </el-form-item>
      <!-- 如果获取的init配置中需要强制验证邮箱号, 则增加发送短信的按钮 -->
      <el-form-item label="&nbsp;&nbsp;&nbsp;&nbsp;邮箱地址" v-if="data_config.must_email">
        <el-col :span="16">
          <el-input v-model="data_request_update.email" ></el-input>
        </el-col>
        <el-col :span="8">
          <el-button
              v-if="data_request_update.email!=user_info.email"
              @click="def_sendcode_email(data_request_update.email)"
              :disabled="status_btn_email" :loading="isCounting_email" type="warning"
          >{{btn_title_countdown_email}}</el-button>
        </el-col>
      </el-form-item>
      <el-form-item label="&nbsp;&nbsp;&nbsp;&nbsp;邮箱地址" v-if="!data_config.must_email">
        <el-input v-model="data_request_update.email" ></el-input>
      </el-form-item>
      <el-form-item label="邮箱验证码" v-if="data_config.must_email && data_request_update.email!=user_info.email">
        <el-input v-model="data_request_update.code_email_input" ></el-input>
      </el-form-item>

    </el-form>
    <el-button
        type="primary" :loading="status_btn_userinfo"
        v-if="!(user_info.befrom!='local' && !data_config.ldap_modify_oneself)" @click="def_update_userinfo"
    >
      提交修改
    </el-button>
    <!--<el-button type="success" v-if="user_info.befrom=='ldap'">ldap修改入口</el-button>-->
  </el-card>

  <!-- 修改密码的卡片 -->
  <el-card class="card_main">
    <el-alert show-icon type="info" class="alert_card_head" :closable="false">修改密码</el-alert>
    <el-form class="form_userinfo" label-width="auto" :disabled="user_info.befrom!='local' && !data_config.ldap_modify_oneself">
      <el-form-item label="旧密码">
        <el-input v-model="data_req_passwd.user_password_old" type="password" show-password/>
      </el-form-item>
      <el-form-item label="新密码">
        <el-input v-model="input_passwd_1" type="password" show-password/>
      </el-form-item>
      <el-form-item label="重复新密码">
        <el-input v-model="input_passwd_2" type="password" show-password/>
      </el-form-item>
    </el-form>
    <div v-if="!(user_info.befrom!='local' && !data_config.ldap_modify_oneself)">
      <el-button type="primary" :loading="status_btn_passwd" @click="def_update_passwd()">提交修改</el-button>
      <el-button type="danger" :loading="status_btn_passwd" @click="router_left.push('/auth/passwdForget')">忘记密码</el-button>
    </div>
    <!--<el-button type="primary" v-if="user_info.befrom=='local'" :loading="status_btn_passwd" @click="def_update_passwd">提交修改</el-button>-->
    <!--<el-button type="danger" v-if="user_info.befrom=='local'" :loading="status_btn_passwd" @click="router_left.push('/auth/passwdForget')">忘记密码</el-button>-->
    <!--<el-button type="success" v-if="user_info.befrom=='ldap'">ldap修改入口</el-button>-->
  </el-card>

</template>

<style scoped>
  .card_main {
    margin-bottom: 20px;
  }
  .alert_card_head {
    margin-bottom: 10px;
  }
  .form_userinfo {
    max-width: 400px;
  }

</style>