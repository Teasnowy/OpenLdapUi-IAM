<script setup lang="ts">
  import {type Ref, ref, reactive} from 'vue'
  import {getServer} from '@/api/def_servers'
  import {global_window} from '@/api/def_feedback'
  import photoUpload from '@/components/photoUpload.vue'
  import photoUploadZip from '@/components/photoUploadZip.vue'
  import {blob_to_base64} from '@/api/currency'
  import type {res_login, req_login, req_singup, res_user_init, res_ok} from '@/api/itf_auth'
  import {router_left} from '@/router/router'


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
  console.log(data_config)

  // 头像选择组件绑定的Blob对象
  let user_photo_blob:Ref<Blob|null> = ref(null)
  // 头像选择组件绑定的base64
  let user_photo_base64:Ref<string|null> = ref(null)
  // 注册时的请求信息
  let data_request_singup:req_singup = reactive({
    "user_photo_base64": null,
    "user_account": '',
    "user_displayname": '',
    "password": '',
    "password_1": '',
    "tel": '',
    "email": '',
    "code_tel_input": '',
    "code_email_input": '',
    "user_type": 'local'
  })

  // 标识注册按钮状态的按钮
  let status_btn_singup:Ref<boolean> = ref(false)
  // 标识注册成功预防的变量
  let status_singup:Ref<boolean> = ref(false)
  // 标识是否发送了短信验证码的变量
  let status_sendcode_sms:Ref<boolean> = ref(false)
  // 标识是否发送了邮箱验证码的变量
  let status_sendcode_email:Ref<boolean> = ref(false)

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


  // 获取初始化信息
  async function def_init() {
    let res_init:any = await getServer('/api/user/init', {"ok": 'ok'})
    data_config.value = res_init as res_user_init
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

  // 点击'返回登录'按钮的操作
  function def_to_login() {
    // action_type.value = "login"
    // window.location.href = '/#/auth/login';
    router_left.push('/auth/login')
  }

  // 注册功能函数
  async function def_singup() {
    status_btn_singup.value = true
    // 如果头像的blob对象不为空, 则将其转化为base64
    // if (user_photo_blob.value) {
    //   await blob_to_base64(user_photo_blob.value).then((res)=>{
    //     data_request_singup.user_photo_base64 = res as string || ""
    //   })
    // }
    if (user_photo_base64.value) {
      data_request_singup.user_photo_base64 = user_photo_base64.value
    }

    let res_singup_tmp:any = await getServer('/api/user/signup', data_request_singup).then((res)=>{
      status_singup.value = true
      status_btn_singup.value = false
    }).catch(()=>{
      status_btn_singup.value = false
    })
    // console.log('登录返回: ', res_login_tmp)
    let res_singup = res_singup_tmp as res_ok
    if (res_singup.ok == 'ok') {
      status_singup.value = true
    }
    status_btn_singup.value = false
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

</script>

<template>
  <div class="div_fri">
    <el-card class="card_center">
      <el-form v-if="!status_singup" label-width="auto" :model="data_request_singup">
        <!-- 头像选择 -->
        <!--<photoUpload v-model="user_photo_blob" :upload="false"/>-->
        <photoUploadZip v-model="user_photo_base64" :upload="false"/>
        <el-form-item label="账号">
          <el-input v-model="data_request_singup.user_account" ></el-input>
        </el-form-item>
        <el-form-item label="显示名">
          <el-input v-model="data_request_singup.user_displayname" ></el-input>
        </el-form-item>
        <!-- 如果获取的init配置中需要强制验证手机号, 则增加发送短信的按钮 -->
        <el-form-item label="手机号码" v-if="data_config.must_tel">
          <el-col :span="16">
            <el-input v-model="data_request_singup.tel" ></el-input>
          </el-col>
          <el-col :span="8">
            <el-button @click="def_sendcode_sms(data_request_singup.tel)" :disabled="status_btn_sms" :loading="isCounting_sms" type="warning">{{btn_title_countdown_sms}}</el-button>
          </el-col>
        </el-form-item>
        <el-form-item label="手机号码" v-if="!data_config.must_tel">
          <el-input v-model="data_request_singup.tel" ></el-input>
        </el-form-item>
        <el-form-item label="手机验证码" v-if="data_config.must_tel">
          <el-input v-model="data_request_singup.code_tel_input" ></el-input>
        </el-form-item>
        <!-- 如果获取的init配置中需要强制验证手机号, 则增加发送短信的按钮 -->
        <el-form-item label="邮箱地址" v-if="data_config.must_email">
          <el-col :span="16">
            <el-input v-model="data_request_singup.email" ></el-input>
          </el-col>
          <el-col :span="8">
            <el-button @click="def_sendcode_email(data_request_singup.email)" :disabled="status_btn_email" :loading="isCounting_email" type="warning">{{btn_title_countdown_email}}</el-button>
          </el-col>
        </el-form-item>
        <el-form-item label="邮箱地址" v-if="!data_config.must_email">
          <el-input v-model="data_request_singup.email" ></el-input>
        </el-form-item>
        <el-form-item label="邮箱验证码" v-if="data_config.must_email">
          <el-input v-model="data_request_singup.code_email_input" ></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="data_request_singup.password" type="password" show-password autocomplete="new-password"/>
        </el-form-item>
        <el-form-item label="重复密码" >
          <el-input v-model="data_request_singup.password_1" type="password" show-password autocomplete="new-password"/>
        </el-form-item>

        <el-button @click="def_singup" type="success" :loading="status_btn_singup">注册</el-button>
        <el-button @click="def_to_login">返回登录</el-button>
      </el-form>

      <!-- 注册成功的表单 -->
      <el-form v-if="status_singup" label-width="auto">
        <el-form-item>
          <el-alert title="注册成功" type="success" center show-icon :closable="false"/>
        </el-form-item>
        <el-button @click="def_to_login" type="success">返回登录</el-button>
        <el-button @click="status_singup=false" type="primary">再次注册</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
  .div_fri {
    display: flex;
    justify-content: center
  }
  .card_center {
    width: 700px;
    margin-top: 5vh;
    min-height: 90vh;
  }
</style>