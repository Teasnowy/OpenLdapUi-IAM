<script setup lang="ts">
  import menuLeftOne from '@/components/menuLeftOne.vue'
  import userHeader from '@/components/userHeader.vue'
  import {RouterView} from "vue-router";
</script>

<template>
  <el-container style="height: 100vh">
    <el-header style="background-color: aliceblue;">
      <user-header/>
    </el-header>
    <el-container>
      <el-aside class="aside-one" width="200px">
        <menuLeftOne/>
      </el-aside>
      <el-main style="height: calc(100vh - 60px)">
        <RouterView/>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>

</style>