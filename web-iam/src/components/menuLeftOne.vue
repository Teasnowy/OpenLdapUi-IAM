<template>
  <el-row class="tac" >
    <el-col >
      <!---->
      <el-menu :default-active="$route.path" class="el-menu-vertical-demo" @open="handleOpen" @close="handleClose"
          router style="height: calc(100vh - 60px);">
        <!--<el-menu-item index="/" enable>-->
        <!--  <el-icon><icon-menu /></el-icon>-->
        <!--  <span>首页</span>-->
        <!--</el-menu-item>-->
        <!-- v-if="Object.keys(user_info.menus).includes('/home/ldapServers')" -->
        <el-menu-item index="/home/ldapServers" >
          <el-icon><OfficeBuilding /></el-icon>
          <span>LDAP远程管理</span>
        </el-menu-item>
        <!--{{user_info.menus}}-->
        <!--{{menu_setting}}-->
        <!-- 系统设置的分组 -->
        <el-sub-menu index="2" v-if="menu_setting.length > 0">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </template>
          <el-menu-item class="menu_item_sec" index="/home/setting/user_manage" v-if="isCan('/home/setting/user_manage')">用户管理</el-menu-item>
          <el-menu-item class="menu_item_sec" index="/home/setting/ldap_group" v-if="isCan('/home/setting/ldap_group')">LDAP组管理</el-menu-item>
          <el-menu-item class="menu_item_sec" index="/home/setting/group_manage" v-if="isCan('/home/setting/group_manage')">用户组管理</el-menu-item>
          <el-menu-item class="menu_item_sec" index="/home/setting/rbac_manage" v-if="isCan('/home/setting/rbac_manage')">角色管理</el-menu-item>
          <el-menu-item class="menu_item_sec" index="/home/setting/menu_manage" v-if="isCan('/home/setting/menu_manage')">菜单管理</el-menu-item>
        </el-sub-menu>
        <!--{{menu_setting}}-->
      </el-menu>
    </el-col>
  </el-row>

</template>

<script lang="ts" setup>
import {
  Document,
  Menu as IconMenu,
  OfficeBuilding,
  Setting,
  Service,
  Memo,
  SuitcaseLine,
  Refresh,
} from '@element-plus/icons-vue'
import {useRoute, useRouter, type LocationQueryValue, RouterLink} from 'vue-router'
import {userInfo} from "@/pinia/envs";
import {computed, type Ref, ref} from 'vue'
import type {itfResRole} from "@/api/itf_manage";

let user_info = userInfo()

// let menus = user_info.menus


// let router = useRouter()
// let menus_tmp = ref(Object.keys(user_info.menus))

// let menu_setting:Ref<Array<string>> = ref([])
//
// let menus:Ref<Array<string>> = ref([])
// for (let i of menus_tmp.value) {
//   menus.value.push(i)
// }
console.log("在左侧栏获取了一次权限信息: ", user_info.menus)
//
// console.log('左侧栏生成最终列表: ', menus)

// 判断设置组是否全部都没有权限
// menu_setting.value = Object.keys(user_info.menus).filter(i => i.match('/home/setting'))
const menu_setting = computed(() => Object.keys(user_info.menus).filter(i => i.match('/home/setting/')))

// 判断业务修复是否全部都没有权限
const menu_yewu = computed(() => Object.keys(user_info.menus).filter(i => i.match('/home/yewu/')))



const handleOpen = (key: string, keyPath: string[]) => {
  // console.log(key, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
  // console.log(key, keyPath)
}

function isCan(path:string) {
  return Object.keys(user_info.menus).includes(path);
}


</script>

<style scoped>

.menu_item_sec {
  padding-left: 100px;
}

</style>