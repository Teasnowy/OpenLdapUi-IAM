<script setup lang="ts">
import { ref, watch, toRefs, h, onMounted } from 'vue';
import {ElNotification} from 'element-plus'

// 来自父组件的传参
type lang_v = "yaml" | "sql" | "json" | "log"
type background_v = "white" | "black"

// 需要传入的参数
// lang 语言类型
// background 主题类型
// btn_copy 是否显示复制按钮
// wrap 是否自动换行
// line_number 是否显示行号

let props = withDefaults(defineProps<{lang?:lang_v, background?:background_v, line_number?:boolean, wrap?:boolean, btn_copy?:boolean, modelValue: string}>(), {
  lang:()=>"yaml",
  background:()=>"white",
  btn_copy:()=>true,
  wrap:()=>true,
  line_number:()=>false,
})
let {lang, btn_copy, wrap, modelValue, background, line_number} = toRefs(props)
let code = ref(props.modelValue)
// let code = modelValue

const emits = defineEmits(['update:modelValue'])
// emits('update:modelValue', code)
// 存储获取到的div标签
let textElement:any = ref(null)
// 控制复制按钮状态的变量
let btn_copy_status = ref(false)
// 行号的动态宽度
let line_number_width = ref(0)

code.value = language_select(code.value, lang.value)
// 计算行号宽度
def_getNumWidth()

// 改变code变量中的特定字符的样式, 使他们被带特定class的span标签包围
function language_select(c:string, l:lang_v="yaml") {
  // console.log("开始检测语言类型")
  // 如果是列表则用\n转为字符串
  if (Array.isArray(c)) {
    c = c.join('\n')
  }
  if (l=='sql'){
    c = color_sql(c)
  } else if (l=='log') {
    c = color_log(c)
  }


  c = c.replace(/\n/g, '<br>')
  // console.log(c)
  return c
}

// log日志的函数
function color_log(c:string) {
  // 日志级别
  c = c.replace(/\sINFO\s/gi, (match)=>{
    return `<span class="dcj_code_logInfo">${match}</span>`
  })
  c = c.replace(/\sDEBUG\s/gi, (match)=>{
    return `<span class="dcj_code_logDebug">${match}</span>`
  })
  c = c.replace(/\sERROR\s/gi, (match)=>{
    return `<span class="dcj_code_logError">${match}</span>`
  })
  c = c.replace(/\sWARN\s/gi, (match)=>{
    return `<span class="dcj_code_logWarn">${match}</span>`
  })

  // 匹配日期
  // let regex_datetime = /\b\d{4}[-\\/]\d{2}[-\\/]\d{2} \d{2}:\d{2}:\d{2}\b/g
  let regex_datetime = /\b\d{4}.\d{2}.\d{2} \d{2}.\d{2}.\d{2}(?:.\d{1,6})?\b/g
  c = c.replace(regex_datetime, (match)=>{
    return `<span class="dcj_code_riQi">${match}</span>`
  })

  // 纯数字和小数, 蓝色
  // let regex_int = new RegExp(/\b\d+(\.\d+)?\b/ , "g")
  // c = c.replace(regex_int, (match)=>{
  //   return `<span class="dcj_code_shuZi">${match}</span>`
  // })

  // 线程号
  let regex_thread = new RegExp(/\[.*?#(.*?)]/ , "g")
  c = c.replace(regex_thread, (match)=>{
    return `<span class="dcj_code_thread">${match}</span>`
  })

  // 类名
  let regex_class = new RegExp(/\s([a-zA-Z0-9_.]+)\s-/ , "g")
  c = c.replace(regex_class, (match)=>{
    return `<span class="dcj_code_class">${match}</span>`
  })

  // 引号内, 包括引号, 淡红 (有时候引号不全, 这里就不高亮引号内容了)
  // let regex_quotationMark = /('[^']+')|("[^"]+")/g
  // c = c.replace(regex_quotationMark, (match)=>{
  //   // 如果引号内的是如dcj_code_blue这样的类名, 那么就跳过
  //   if (/^"dcj_code_[^"]+"/.test(match)) {
  //     // console.log("引号跳过: ", match)
  //     return match
  //   } else {
  //     // 去掉引号内其他的class为dcj_code开头的标签
  //     match = match.replace(/class="dcj_code_\w+"/g, '')
  //   }
  //   return `<span class="dcj_code_yinHao" style="color: #ec6c7e !important;">${match}</span>`
  // })

  return c
}

// sql语言的函数
function color_sql(c:string) {
  // 关键词, 染红,
  let list_keyword = [
    'SELECT', 'INSERT', 'INTO', 'UPDATE', 'DELETE', 'WHERE', 'JOIN', 'ON',
    'GROUP BY', 'ORDER BY', 'HAVING', 'DISTINCT', 'LIMIT', 'OFFSET',
    'UNION', 'CREATE', 'DROP', 'ALTER', 'TABLE', 'INDEX', 'VIEW',
    'INSERT INTO', 'VALUES', 'SET', 'SHOW', 'TRUNCATE', 'RENAME',
    'USE', 'DESCRIBE', 'EXPLAIN', 'CALL', 'GRANT', 'REVOKE',
    'COMMIT', 'ROLLBACK', 'TRANSACTION', 'BEGIN', 'END',
    'LOCK', 'UNLOCK', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'ELSE',
    'END', 'DEFAULT', 'AUTO_INCREMENT', 'PRIMARY KEY', 'FOREIGN KEY',
    'UNIQUE', 'CHECK', 'NOT NULL', 'NULL', 'REFERENCES', 'NONE',
  ]
  // console.log("开始检测sql关键词")
  // for (let i of list_keyword){
  //   let regex_keyword = new RegExp(`\b${i}\b`, "ig");
  //   c = c.replace(regex_keyword, ` <span class="dcj_code_red">${i}</span> `)
  // }
  const str_keyword = '\\b(' + list_keyword.join('|').replace(/ /g, '\\s') + ')\\b';
  const regex_keyword = new RegExp(str_keyword, 'gi');
  c = c.replace(regex_keyword, (match)=>{
    return `<span class="dcj_code_guanJianZi">${match}</span>`
  })

  // console.log("开始检测日期")
  // 匹配日期
  let regex_datetime = /\b\d{4}[-\\/]\d{2}[-\\/]\d{2} \d{2}:\d{2}:\d{2}\b/g
  c = c.replace(regex_datetime, (match)=>{
    return `<span class="dcj_code_riQi">${match}</span>`
  })

  // console.log("开始检测数字")
  // 纯数字和小数, 蓝色
  let regex_int = new RegExp(/\b\d+(\.\d+)?\b/ , "g")
  c = c.replace(regex_int, (match)=>{
    return `<span class="dcj_code_shuZi">${match}</span>`
  })

  // console.log("开始检测引号内")
  // 引号内, 包括引号, 绿色
  let regex_quotationMark = /('[^']+')|("[^"]+")/g
  c = c.replace(regex_quotationMark, (match)=>{
    // 如果引号内的是如dcj_code_blue这样的类名, 那么就跳过
    if (/^"dcj_code_[^"]+"/.test(match)) {
      // console.log("引号跳过: ", match)
      return match
    } else {
      // 去掉引号内其他的class为dcj_code开头的标签
      match = match.replace(/class="dcj_code_\w+"/g, '')
    }
    return `<span class="dcj_code_yinHao" style="color: #66a45c !important;">${match}</span>`
  })
  console.log("高亮加载完毕")

  return c
}

function btn_copy_sql() {
  // 创建一个临时 textarea 元素
  const tempTextArea = document.createElement("textarea");
  // 设置 textarea 的值为要复制的文本
  tempTextArea.value = modelValue.value;
  // 将 textarea 添加到文档中
  document.body.appendChild(tempTextArea);
  // 选中 textarea 中的文本
  tempTextArea.select();
  // 执行复制命令
  const successful = document.execCommand("copy");
  // 从文档中移除 textarea 元素
  document.body.removeChild(tempTextArea);
  if (successful) {
    ElNotification({
      title: '复制成功',
      message: h('i', { style: 'color: teal' }, `所有文本已复制`),
    })
  } else {
    ElNotification({
      title: '复制失败',
      message: h('i', { style: 'color: red' }, `可能是你鼠标坏了`),
    })
  }
}

// 组件挂载时检测id为code_dcj的div, 用来操作class
onMounted(()=>{
  textElement.value = document.getElementById('code_dcj')
  // console.log("获取到div: ", textElement.value)
  // 检测换行
  if (!wrap.value) {
    textElement.value.classList.add("dcj_line_not_wrap")
  }
  // 检测背景色
  if (background.value == 'black') {
    textElement.value.classList.add("dcj_background_shen")
  } else if (background.value == 'white') {
    textElement.value.classList.add("dcj_background_qian")
  } else {
    textElement.value.classList.add("dcj_background_qian")
  }
})

watch(modelValue,(v_new)=>{
  // 重新读取新值并染色
  code.value = language_select(v_new, lang.value)
})

// 动态获取最大行号的宽度
function def_getNumWidth() {
  // 创建一个虚拟的 span 元素来计算宽度
  const testSpan = document.createElement('span');
  testSpan.style.visibility = 'hidden'; // 不显示
  testSpan.style.position = 'absolute'; // 不占用布局空间
  document.body.appendChild(testSpan);

  // 测量行号的宽度，取最长的数字（即最大行号）
  const longestNumber = code.value.split('<br>').length;  // 计算行数，假设每行一个行号
  testSpan.textContent = longestNumber.toString(); // 测量最大行号的宽度

  // 获取最大行号宽度
  line_number_width.value = testSpan.offsetWidth;

  // 清理临时元素
  document.body.removeChild(testSpan);
}


</script>

<template>
  <div id="code_dcj" class="dcj_code_default" >
    <div style="text-align: right;">
      <!--<el-button v-if="btn_copy" size="small" type="info" :icon="CopyDocument" @click="btn_copy_sql" class="dcj_btn_copy"></el-button>-->
      <button class="dcj_btn_copy" v-if="btn_copy" @click="btn_copy_sql">复制</button>
      <!--<el-icon><CopyDocument /></el-icon>-->
    </div>
    <!--<div class="" v-html="code"></div>-->
    <div v-if="line_number">
      <div v-for="(i, index) in code.split('<br>')" :key="index" class="dcj_line_number_show">
        <div v-if="line_number" class="dcj_line_number_div" :style="{ width: line_number_width + 'px' }">{{ index + 1 }}</div>
        <!--{{ index }}-->
        <div v-html="i"></div>
      </div>
    </div>
    <div v-else>
      <div v-html="code"></div>
    </div>

  </div>

  <!--<p class="code_red">INSERT</p>-->
</template>

<style>
/* 复制按钮的样式 */
.dcj_btn_copy {
  /*text-align: right;*/
  user-select: none; /* 禁止文本选择 */
  -webkit-user-select: none; /* 兼容 Safari 和 Chrome */
  -moz-user-select: none; /* 兼容 Firefox */
  -ms-user-select: none; /* 兼容 IE 和 Edge */
  cursor: pointer; /* 可被点击 */
  font-size: 12px;
  background-color: #eecbf1;      /* 淡紫色背景 */
  color: white;                   /* 文字颜色为黑色 */
  border: none;      /* 深紫色的边框，2px solid #d28ffa */
  border-radius: 5px;             /* 四周略微圆滑的角 */
  padding: 2px 3px;              /* 按钮的内边距，给文字留空间 */
  transition: background-color 0.3s ease;  /* 添加过渡效果 */
}

/* 显示行号时相关的样式 */
.dcj_line_number_show {
  display: flex;
  /*flex: 1 1 auto; !* 自动调整宽度 *!*/
  /*width: 0;*/
  /*border: 1px solid #ddd; !* 边框 *!*/
}
.dcj_line_number_div {
  display: flex;           /* 启用 flexbox 布局 */
  justify-content: center; /* 水平居中 */
  /*flex: 0 0 50%;*/
  color: #c8c9cc;
  padding-right: 5px;
  margin-right: 10px;
  user-select: none; /* 禁止文本选择 */
  -webkit-user-select: none; /* 兼容 Safari 和 Chrome */
  -moz-user-select: none; /* 兼容 Firefox */
  -ms-user-select: none; /* 兼容 IE 和 Edge */
  border-right: 1px solid #c8c9cc;
  flex-shrink: 0; /* 防止宽度收缩 */
  /*width: auto; !* 让行号部分自适应宽度 *!*/
}
/* 不换行时应用的样式 */
.dcj_line_not_wrap {
  white-space: nowrap;
  overflow-x: auto;
}
/*浅色主题*/
.dcj_background_qian {
  /*flex: 0 0 50%;*/
  /*min-width: 0;*/
  /*overflow: hidden;*/
  background-color: #f2f2f2;
  color: #434343;
  padding: 10px;
}
/*深色主题*/
.dcj_background_shen {
  background-color: #2a2e36;
  /*word-wrap: break-word; !* 这里是防止有时文字溢出div范围 *!*/
  color: #ffffff;
}

/* 最外层div的默认样式 */
.dcj_code_default {
  margin-top: 10px;
  word-break: break-all; /*为了flex布局让子div不溢出父div*/
  word-wrap: break-word; /* 这里是防止有时文字溢出div范围 */
  padding: 10px;
  /*font-family: Arial, sans-serif;*/
  font-family: "JetBrains Mono", source-code-pro, Menlo, Monaco, Consolas, "Courier New", monospace;
  line-height: 1.6;
  font-size: .875em;
}

.dcj_code_guanJianZi {
  color: #ff4745;
}
.dcj_code_yinHao {
  color: #66a45c
}
.dcj_code_shuZi {
  color: #5dbad9;
}
.dcj_code_riQi {
  /*color: #eda806;*/
  color: #5dbad9;
}

.dcj_code_thread {
  /*color: #87CEFA;*/
  color: #FF69B4;
}

.dcj_code_class {
  color: #6495ED;
}

.dcj_code_logInfo {
  color: #a4da35;
}

.dcj_code_logDebug {
  color: #87CEFA;
}
.dcj_code_logError {
  color: #ec6c7e;
}
.dcj_code_logWarn {
  color: #F4A460;
}

</style>