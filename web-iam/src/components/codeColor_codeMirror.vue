<template>
  <!-- :indent-with-tab="true" 是否自动获取焦点-->
  <codemirror v-model="code" placeholder="Code gose here..." :style="{ height: '100%' }" :autofocus="true"
              :tabSize="tabsize" :extensions="extensions" :disabled="readonly"/>
</template>

<script lang="ts" setup>

  import { Codemirror } from "vue-codemirror";
  import { javascript } from "@codemirror/lang-javascript";
  import { yaml,  } from "@codemirror/lang-yaml";
  import { sql } from "@codemirror/lang-sql";
  import { json } from "@codemirror/lang-json";
  import {defineModel, toRefs } from "vue";
  import { EditorView } from "@codemirror/view"

  // 来自父组件的传参
  let props = withDefaults(defineProps<{lang?:string, tabsize?:number, readonly?:boolean}>(), {
    lang:()=>"yaml",
    tabsize:()=>2,
    readonly:()=>false
  })
  let {lang, tabsize, readonly} = toRefs(props)

  let language = yaml()

  // 仅支持以下几种语言
  if (lang.value == "yaml") {
    language = yaml()
  } else if (lang.value == "javascript") {
    language = javascript()
  } else if (lang.value == "sql") {
    language = sql()
  } else if (lang.value == "json") {
    language = json()
  }

  // option 里写lineWrapping:true似乎没用
  let myTheme = EditorView.theme({
    ".cm-gutters": {
      backgroundColor: "#FFFFFF",
      color: "#ddd", //侧边栏文字颜色
      border: "none"
    }
  }, {})

  interface IProps {
    height?: string,
  }

  // defineModel 是vue3.4后的简写, 用于v-model
  const code:any = defineModel()
  const extensions = [yaml(), myTheme,];
  const Change = () => {

  }
</script>