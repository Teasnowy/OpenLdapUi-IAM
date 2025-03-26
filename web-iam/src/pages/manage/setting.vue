<script setup lang="ts">
  import {type Ref, ref} from 'vue'
  import ldap_group from '@/pages/manage/ldap_group.vue'
  import user_manage from '@/pages/manage/user_manage.vue'
  import rbac_manage from '@/pages/manage/rbac_manage.vue'


  // 控制当前标签页的变量
  let status_tab:Ref<string> = ref("users")


</script>

<template>
  <!-- 通过标签页来切换不同的设置项 , 启用了延迟渲染, 选中才加载数据 -->
  <el-tabs type="card" v-model="status_tab" class="tabs_setting" >
    <el-tab-pane label="用户管理" name="users" :lazy="true">
      <user_manage/>
    </el-tab-pane>
    <el-tab-pane label="LDAP设置" name="ldap" :lazy="true">
      <ldap_group/>
    </el-tab-pane>
    <el-tab-pane label="权限管理" name="rbac" :lazy="true">
      <rbac_manage/>
    </el-tab-pane>
  </el-tabs>

</template>

<style scoped>

.tabs_setting {
  /* 减去 头部横条60, main内边距20, tabs标题栏39 */
  min-height: calc(100vh - 60px - 20px - 39px);
}

</style>