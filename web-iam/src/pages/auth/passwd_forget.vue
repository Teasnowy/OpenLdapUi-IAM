<script setup lang="ts">
  import {type Ref, ref, reactive, toRefs} from 'vue'
  import {getServer, def_sendcode_email_fromUser, def_sendcode_sms_fromUser} from '@/api/def_servers'
  import {global_window} from '@/api/def_feedback'
  import zihao from '@/assets/zihao.jpg'
  import {type res_check_telEmail,} from '@/api/itf_auth'
  import {userInfo} from "@/pinia/envs";

  // 全局变量
  let user_info = userInfo()

  // 标识顶部进度的index
  let active:Ref<number> = ref(0)
  // 中部卡片的loading状态
  let load_card:Ref<boolean> = ref(false)
  // 最终修改密码成功与否的状态
  let status_update:Ref<boolean> = ref(false)
  // 重发验证码按钮的显示文本
  let btn_title_countdown:Ref<string> = ref("重新发送验证码")
  // 发送验证码的状态
  let isCounting:Ref<boolean> = ref(false)
  // 发送验证码的时间间隔
  let countdown_max:number = 60
  // 发送验证码当前倒计时的数字
  let countdown:Ref<number> = ref(countdown_max)
  // 输入的短信验证码
  let input_code:Ref<string> = ref("")
  // 输入的用户名
  let user_account:Ref<string> = ref(user_info.account)
  // 获取身份验证方式的返回信息
  let data_res_telEmail:Ref<res_check_telEmail> = ref({
    email_vague: null,
    tel_vague: null
  })
  // 手机验证确认标题
  let label_tel:Ref<string> = ref("")
  // 邮箱验证确认标题
  let label_email:Ref<string> = ref("")
  // 用户选择的验证方式
  let select_auth:Ref<"email"|"tel"|""> = ref("")
  // 用户输入的密码1
  let input_passwd_1:Ref<string> = ref("")
  // 用户输入的密码2
  let input_passwd_2:Ref<string> = ref("")

  // 点击下一步时的操作
  async function def_active_next() {
    load_card.value = true
    // 每一步做不同的动作
    if (active.value == 0) {
      // 输入用户名
      if (!user_account.value) {
        global_window('error', "至少要为勇者留下名字")
        load_card.value = false
        return
      }
       await def_get_telEmail().then(()=>{}).catch((err)=>{})
      console.log(data_res_telEmail.value)
    } else if (active.value == 1) {
      // 选择验证方式
      // 没选择验证方式不给通过
      if (!select_auth.value) {
        global_window('error', "至少选择一个验证方式")
        load_card.value = false
        return
      }
      if (select_auth.value=='email') {
        await def_sendcode_email_fromUser(user_account.value).then(()=>{}).catch((err)=>{})
        startCountdown()
      } else if (select_auth.value=='tel') {
        await def_sendcode_sms_fromUser(user_account.value).then(()=>{}).catch((err)=>{})
        startCountdown()
      } else {
        global_window('error', "至少选择一个验证方式")
        load_card.value = false
        return
      }
    } else if (active.value == 2) {
      // 输入验证码并重置密码
      if (!select_auth.value) {
        global_window('error', "至少选择一个验证方式")
        load_card.value = false
        return
      }
      if (input_passwd_1.value != input_passwd_2.value) {
        global_window('error', "两次密码输入不一致")
        load_card.value = false
        return
      }
      await user_passwd_update().then(()=>{}).catch((err)=>{})
    }

    // 数字索引加一
    if (active.value++ > 3) active.value = 3
    load_card.value = false
  }
  // 点击下一步时的操作
  function def_active_back() {
    // 去除成功修改密码的状态
    status_update.value = false
    // 数字索引减一
    if (active.value-- < 1) active.value = 0
  }

  // 提交用户名的函数, 获取可供验证身份的方式
  async function def_get_telEmail() {
    console.log("查找用户的可用验证方式")
    let data_res_telEmail_tmp = await getServer(
        '/api/user/check/telEmail', {"user_account": user_account.value},
    )
    data_res_telEmail.value = data_res_telEmail_tmp as res_check_telEmail
    // 修改手机验证确认标题
    if (data_res_telEmail.value.tel_vague) {
      console.log("用户的手机为: ", data_res_telEmail.value.tel_vague)
      label_tel.value = "使用 "+data_res_telEmail.value.tel_vague+" 短信验证"
    }
    // 邮箱验证确认标题
    if (data_res_telEmail.value.email_vague) {
      console.log("用户的邮箱为: ", data_res_telEmail.value.email_vague)
      label_email.value = "使用 "+data_res_telEmail.value.email_vague+" 邮件验证"
    }
  }

  // 根据用户名重新发送验证码
  async function code_send_fromUser() {
    if (select_auth.value=='email') {
      await def_sendcode_email_fromUser(user_account.value).then(()=>{
        startCountdown()
      })
    } else if (select_auth.value=='tel') {
      await def_sendcode_sms_fromUser(user_account.value).then(()=>{
        startCountdown()
      })
    } else {
      global_window('error', "至少选择一个验证方式")
      return
    }
  }

  // 根据用户名修改密码
  async function user_passwd_update() {
    let code_type:string = ""
    let url:string = ""
    if (select_auth.value=='email') {
      code_type = "code_email_input"
      url = "/api/user/update/passwd/local/useemail"
    } else if (select_auth.value=='tel') {
      code_type = "code_tel_input"
      url = "/api/user/update/passwd/local/usetel"
    } else {
      global_window('error', "至少选择一个验证方式")
      return
    }
    let data_request_update:object = {
      "user_account": user_account.value,
      [code_type]: input_code.value,
      "user_password_new": input_passwd_1.value
    }
    await getServer(url, data_request_update).then(()=>{
      status_update.value = true
    })
  }

  // 点击'返回登录'按钮的操作
  function def_to_login() {
    // action_type.value = "login"
    window.location.href = '/auth/login';
  }

  // 发送验证码的倒计时
  function startCountdown() {
    if (isCounting.value) return; // 如果正在倒计时，直接返回
    isCounting.value = true; // 设置为正在倒计时

    const interval = setInterval(() => {
      if (countdown.value > 0) {
        countdown.value--; // 每秒减少倒计时
        btn_title_countdown.value = countdown.value+" 秒后重发"
      } else {
        clearInterval(interval); // 倒计时结束，清除定时器
        isCounting.value = false; // 设置为未倒计时状态
        countdown.value = countdown_max; // 重置倒计时（可以根据需求调整）
        btn_title_countdown.value = "重新发送验证码"
      }
    }, 1000); // 每秒更新一次
  }


</script>

<template>

  <!-- 头部进度条 -->
  <div class="div_head">
    <el-steps style="height: 60px;" :active="active" finish-status="success" simple>
      <el-step title="输入用户名" />
      <el-step title="选择验证方式" />
      <el-step title="重置密码" />
      <el-step title="获取结果" />
    </el-steps>
  </div>
  <!-- 操作区 -->
  <div class="div_main" >

    <el-card class="card_center" v-loading="load_card">
      <el-button v-if="active>0" class="btn_back" type="warning" @click="def_active_back">上一步</el-button>
      <!-- 第一步输入用户名 -->
      <el-form v-if="active==0" class="form_center">
        <el-form-item label="用户名">
            <el-input v-model="user_account"/>
        </el-form-item>
      </el-form>
      <!--第二步选择验证方式-->
      <el-form v-if="active==1" class="form_center" >
        <!--v-if="data_res_telEmail.tel_vague || data_res_telEmail.email_vague"-->
        <el-form-item v-if="data_res_telEmail.tel_vague || data_res_telEmail.email_vague">
          <el-radio-group v-model="select_auth">
            <el-radio v-if="data_res_telEmail.email_vague" value="email">{{label_email}}</el-radio>
            <el-radio v-if="data_res_telEmail.tel_vague" value="tel">{{label_tel}}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-empty v-if="!data_res_telEmail.tel_vague && !data_res_telEmail.email_vague" :image="zihao" description="没有可验证的手段呢 ~"/>
      </el-form>
      <!--第三步输入验证码-->
      <el-form v-if="active==2" class="form_center" label-width="auto">
        <el-form-item label="输入验证码">
          <el-input v-model="input_code" style="width: 130px;margin-right: 20px" autocomplete="new-password"/>
          <el-button type="info" style="width: 130px" :loading="isCounting" @click="code_send_fromUser">{{btn_title_countdown}}</el-button>
        </el-form-item>
        <el-form-item label="输入新密码">
          <el-input v-model="input_passwd_1" type="password" show-password autocomplete="new-password"/>
        </el-form-item>
        <el-form-item label="重复新密码">
          <el-input v-model="input_passwd_2" type="password" show-password autocomplete="new-password"/>
        </el-form-item>
      </el-form>
      <!--第四步查看结果-->
      <el-form v-if="active==3" class="form_center" label-width="auto">
        <el-alert v-if="status_update" title="修改成功" type="success" center show-icon :closable="false"/>
        <el-alert v-if="!status_update" title="修改失败" type="error" center show-icon :closable="false"/>
        <el-button style="margin-top: 20px" type="primary" @click="def_to_login()">返回登录</el-button>
      </el-form>
      <el-button v-if="active<3" class="btn_login" type="info" @click="def_to_login()">返回登录</el-button>
      <el-button v-if="active<3" class="btn_next" type="success" @click="def_active_next">下一步</el-button>

    </el-card>
  </div>
</template>

<style scoped>
  .div_head {
    background-color: aliceblue;
    width: 100vw;
    height: 60px;
  }
  .div_main {
    display: flex;
    min-height: 600px;
    height: calc(100vh - 60px);
    justify-content: center;
    align-items: center;
    margin-top: -60px;
  }
  .card_center {
    width: 800px;
    height: 400px;
    position: relative;
    display: flex;            /* 设置为flex布局 */
    flex-direction: column;  /* 垂直方向布局 */
    justify-content: center;  /* 垂直居中 */
    align-items: center;
  }
  .btn_back {
    position: absolute;
    left: 20px;
    top: 20px;
  }
  .btn_next {
    position: absolute;
    right: 20px;
    bottom: 20px;
  }
  .btn_login {
    position: absolute;
    left: 20px;
    bottom: 20px;
  }
  .form_center {
    width: 400px;
    margin: auto;
  }
</style>