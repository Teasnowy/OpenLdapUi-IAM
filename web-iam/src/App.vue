
<template>
  <div id="main">
    <RouterView/>
  </div>
</template>

<script lang="ts" setup>

import {RouterView, useRoute} from 'vue-router'
import {userInfo} from "@/pinia/envs";
import {before_router } from '@/router/router'

// import {userInfo} from "@/pinia/envs";
let user_info = userInfo()
// user_info.update_menus().then(()=>{
//     before_router()
// })

console.log("加载了app")


</script>

<style>
 * {
   margin: 0;
   padding: 0;
 }

</style>