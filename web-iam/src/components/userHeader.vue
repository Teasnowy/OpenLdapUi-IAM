<script setup lang="ts">
  import {ref, type Ref} from 'vue'
  import { ElNotification as notify } from 'element-plus'
  import {RouterLink} from 'vue-router'
  import {userInfo} from "@/pinia/envs";
  import {router_left} from '@/router/router'
  import {getServer} from '@/api/def_servers'
  import type {itfmyInfo} from '@/api/itf_manage'
  import type {res_user_init} from '@/api/itf_auth'
  // import { per } from '@/directive/permission'
  // import {app} from '@/main'


  let user_info = userInfo()

  // 初始化的后端配置信息
  let data_req_conf:res_user_init = {
    list_ous: [],
    must_email: true,
    must_tel: true,
    ldap_status: false,
    forget_passwd_ldap: false,
    ldap_modify_oneself: false,
  }

  // 立刻从服务器拉取一次自己的信息
  getMyInfo()

  // 从后端初始化配置信息
  def_init()

  const onBack = () => {
    notify('Back')
  }

  let status_photo:Ref<boolean> = ref(false)
  // let db_test:Ref<string> = ref(window.localStorage.getItem('test_1'))

  // 点击登录的操作
  function def_login() {
    router_left.push('/auth/login')
  }
  // 点击注销的操作
  async function def_logout() {
    // 成功了再清除
    await getServer("/api/user/logout", {"account": user_info.account}).then((res)=>{
      window.localStorage.removeItem("yukikaze_user_jwt")
      window.localStorage.removeItem("yukikaze_user_photo")
    }).catch(()=>{})
    await router_left.push('/auth/login')
  }
  // 点击个人信息的操作
  function def_my() {
    router_left.push('/home/myInfo')
  }

  function def_photo_undefined() {
    return "aaa"
  }

  // 获取自己的用户信息
  async function getMyInfo() {
    await getServer("/api/manage/get/user/my", {"ok": "ok"}).then((res)=>{
      let data_myinfo = res as itfmyInfo
      user_info.displayname = data_myinfo.displayname
      user_info.account = data_myinfo.account
      user_info.tel = data_myinfo.tel
      user_info.befrom = data_myinfo.befrom
      user_info.email = data_myinfo.email
      user_info.roles = data_myinfo.roles
      user_info.groups = data_myinfo.groups
      user_info.user_photo = data_myinfo.photo_base64
      // user_info.menus = data_myinfo.menus
      window.localStorage.setItem("yukikaze_user_photo", data_myinfo.photo_base64)
      console.log("在header拉取了一次个人信息: ", user_info)
      // app.directive('dcj', per)
    }).catch((err)=>{})
  }

  // 从后端获取初始化配置信息
  async function def_init() {
    let res_init:any = await getServer('/api/user/init', {"ok": 'ok'})
    data_req_conf = res_init as res_user_init
    user_info.inti_conf = data_req_conf
  }

  // console.log("头部的base64: ", user_info.user_photo)


</script>

<template>
  <div class="user_header">
    <!--<el-text>{{user_info.displayname}}</el-text>-->
    <el-dropdown>
      <el-avatar
          @click=""
          :size="32"
          class="mr-3"
          :src="user_info.user_photo||undefined"
          alt=""
          @error="def_photo_undefined()" style="cursor:pointer"
      >
        {{ user_info.displayname && user_info.displayname.length > 0 ? user_info.displayname.slice(0, 1) : '?' }}
        <!--{{user_info.displayname.slice(0, 1)}}-->
      </el-avatar>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item v-if="!user_info.account" @click="def_login()">登录</el-dropdown-item>
          <el-dropdown-item v-if="user_info.account&&Object.keys(user_info.menus).includes('/home/myInfo')" @click="def_my()">个人信息</el-dropdown-item>
          <el-dropdown-item v-if="user_info.account" @click="def_logout()">注销</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
    <!--<img :src="user_info.user_photo" alt="aaaaa">-->
    <!--{{ user_info.user_photo }}-->


  </div>
</template>

<style scoped>
  .user_header {
    display: flex;
    justify-content: flex-end; /* 使元素靠右对齐 */
    padding-right: 30px; /* 可选，增加内边距 */
    /*border: 1px solid #ccc; !* 可选，边框以便于观察 *!*/
    align-items: center;
    height: 100%;
  }
</style>