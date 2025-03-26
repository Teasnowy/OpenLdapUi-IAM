<script setup lang="ts">
  import {ref, type Ref, toRefs} from 'vue'
  import {global_window} from '@/api/def_feedback'
  import type {req_photo_update} from '@/api/itf_auth'
  import { Plus } from '@element-plus/icons-vue'
  import { genFileId } from 'element-plus'
  import type { UploadProps, UploadUserFile, UploadInstance, UploadRawFile, UploadRequestHandler} from 'element-plus'
  import {getServer} from '@/api/def_servers'
  import {userInfo} from '@/pinia/envs'
  import {compressAndCropBase64Image} from '@/api/currency'
  import { storeToRefs } from 'pinia'
  // import photo_defult from '@/assets/photo_defult.jpg'
  import halou from '@/assets/photo_default/halou.jpg'
  import sanwu from '@/assets/photo_default/sanwu.jpg'
  import tianzhen from '@/assets/photo_default/tianzhen.jpg'
  import huaixiao from '@/assets/photo_default/huaixiao.jpg'
  import kaixin from '@/assets/photo_default/kaixin.jpg'
  import keai from '@/assets/photo_default/keai.jpg'
  import mojing from '@/assets/photo_default/mojing.jpg'
  import tuosai from '@/assets/photo_default/tuosai.jpg'
  import yiwen from '@/assets/photo_default/yiwen.jpg'

  // 此组件为先预览, 上传时才压缩裁剪

  // 引入全局变量, 并读取为响应式
  // let {befrom, test_1, account} = storeToRefs(userInfo())
  let user_info = userInfo()

  // 接收值, upload为是否显示上传按钮
  let props = withDefaults(defineProps<{modelValue?:Blob|null, upload?:boolean}>(),{
    upload:()=>true
  })
  // 回传哪些值
  const emit = defineEmits(['update:modelValue'])


  // 预选头像列表
  let photo_list_default:Ref<Array<string>> = ref([halou, sanwu, tianzhen, huaixiao, kaixin, keai, mojing, yiwen,tuosai])
  // 选择预选图片库后生成的blob对象
  let photo_default_blob:Blob|null = null
  // 上传按钮的loading状态
  let status_btn_upload = ref(false)
  // 选择框中图片的url
  const imageUrl = ref(user_info.user_photo)
  // 当前用户上传图片的对象(不包含预选图片)
  const upload = ref<UploadInstance>()
  // 当前用户上传图片的列表(不包含预选图片)
  let photo_list:Ref<UploadUserFile[]> = ref([])

  let data_request:req_photo_update = {
    user_account: user_info.account!,
    user_type: user_info.befrom!,
    user_photo_base64: null
  }

  // 点击预选图片的操作, 替换当前图片
  function btn_replace(path:string) {
    fetch(path)
        .then(response => {
          if (!response.ok) {
            throw new Error("Failed to fetch the image");
          }
          return response.blob();  // 获取 Blob 对象
        })
        .then(blob => {
          // 使用 Blob 创建 File 对象
          photo_default_blob = new File([blob], "photo_default.jpg", { type: blob.type });
          // 回传父组件当前文件的blob
          emit('update:modelValue', photo_default_blob)
          // 这里可以将 file 传递给上传接口或其他操作
        })
        .catch(error => {
          console.error("Error fetching image:", error);
        })
    imageUrl.value = path
    photo_list.value = []
  }

  // 上传数量突破限制时触发的操作
  const handleExceed: UploadProps['onExceed'] = (files) => {
    // 清空当前列表
    upload.value!.clearFiles()
    // 获取本次上传的第一个文件
    const file = files[0] as UploadRawFile
    // 获取文件ID
    // console.log("file.uid: ", file.uid)
    file.uid = genFileId()
    // console.log("file.uid: ", file.uid)
    // 重新向文件列表填写数据
    upload.value!.handleStart(file)
  }

  // 文件状态发生变动时的操作, 添加文件、上传成功和上传失败时都会被调用
  const handleChange: UploadProps['onChange'] = (uploadFile, uploadFiles) => {
    let image_white_list = ["image/jpeg", "image/png", "image/gif"]
    console.log(uploadFile.raw?.type!)
    // 判断文件是否符合
    if (!image_white_list.includes(uploadFile.raw?.type!)) {
      global_window("error", "仅允许上传 jpg | png | gif")
      return
    }
    // if (uploadFile.size! > 102400) {
    //   global_window("error", "不可以上传大于100k的图片")
    //   return
    // }
    status_btn_upload.value = true
    imageUrl.value = URL.createObjectURL(uploadFile.raw!)
    console.log("预览原图: ", imageUrl.value)
    // imageUrl.value = uploadFile.url!
    status_btn_upload.value = false
    // 清空用户手动上传的图片的blob
    photo_default_blob = null
    // 回传父组件当前文件的blob
    emit('update:modelValue', uploadFile.raw!)
  }

  // 上传文件按钮
  async function btn_upload() {
    // 正常来说是这样上传的, 但这样后端没办法用json接收正常数据
    // upload.value!.submit()
    status_btn_upload.value = true
    // 所以改为传输base64
    if (photo_list.value.length > 0) {
      console.log("启用用户选择的图片: ", photo_list.value[0].raw)
      data_request.user_photo_base64 = await file_to_base64(photo_list.value[0].raw).catch(()=>{
        status_btn_upload.value = false
      }) as string || ""
    } else {
      console.log("启用预选列表的图片: ", photo_default_blob)
      data_request.user_photo_base64 = await file_to_base64(photo_default_blob).catch(()=>{
        status_btn_upload.value = false
      }) as string || ""
    }

    // 尝试压缩
    await compressAndCropBase64Image(data_request.user_photo_base64, 100).then((res)=>{
      data_request.user_photo_base64 = res as string || ""
      imageUrl.value = data_request.user_photo_base64
      console.log("替换为压缩后的图片: ", imageUrl.value)
    }).catch(()=>{})

    // console.log("aa: ", aa)
    console.log(data_request)
    await getServer('/api/user/update/photo', data_request).then(()=>{
      status_btn_upload.value = false
      window.localStorage.setItem("yukikaze_user_photo", data_request.user_photo_base64!)
      user_info.update_jwt()
      global_window("success", "上传成功 ~")
    }).catch(()=>{
      status_btn_upload.value = false
      global_window("error", "上传失败 ~")
    })
    status_btn_upload.value = false
  }


  // 图片的blob对象转为base64
  function file_to_base64(blob:Blob|null|undefined) {
    // upload.value?.clearFiles()
    return new Promise((resolve, reject) => {
      if (!(blob instanceof Blob)) {
        console.log(typeof blob, blob)
        if (!blob) {
          global_window("error", "你似乎没有选择或上传图片")
        } else {
          global_window("error", "图片未能成功转化为blob格式")
        }
        // 清空所有相关元素
        photo_default_blob = null
        upload.value?.clearFiles()
        imageUrl.value = ""
        reject("")
      }

      const reader = new FileReader();

      reader.onloadend = () => {
        resolve(reader.result);  // 返回 Base64 编码
      };
      reader.onerror = () => {
        global_window("error", "读取文件失败")
        reject(new Error('读取文件失败'));
      };
      // 读取 Blob 为 Data URL（Base64编码）
      reader.readAsDataURL(blob!);
    });
  }

  // 自定义http请求的函数
  function modify_http (option: UploadRequestHandler) {
    console.log(option)
  }

</script>

<template>
  <!-- 这里最外层要放一个div, 不然可能被el-from识别为多个子标签而打乱排版 -->
  <div>
    <div class="div_select">
      <el-upload
          id="upup"
          ref="upload"
          v-model:file-list="photo_list"
          class="avatar-uploader"
          :show-file-list="false"
          :on-change="handleChange"
          :auto-upload="false"
          :limit="1"
          :on-exceed="handleExceed"
      >
        <img v-if="imageUrl&&imageUrl!='undefined'" :src="imageUrl" class="avatar" alt=""/>
        <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
      </el-upload>
      <el-avatar v-if="imageUrl&&imageUrl!='undefined'" :size="32" class="mr-3" :src="imageUrl" />
    </div>
    <div class="div_photo_list">
      <el-button v-if="props.upload" class="btn_upload" type="primary" @click="btn_upload" :loading="status_btn_upload" >上传</el-button>
      <el-image class="photo_default" v-for="i in photo_list_default" :src="i" @click="btn_replace(i)"/>
    </div>
  </div>


  <!--{{ user_info.user_photo }}-->
</template>

<style scoped>
.avatar-uploader .avatar {
  width: 178px;
  height: 178px;
  display: block;
}

</style>

<style>

.div_select {
  display: flex;
  gap: 30px;
}

.btn_upload {
  margin-top: 28px;
  margin-right: 20px;
}

.div_photo_list {
  margin-top: 20px;
  margin-bottom: 20px;
  /*margin-left: 50px;*/
  display: flex;
  gap: 10px;
  flex-wrap: wrap
}

.photo_default {
  width: 60px;
  height: 60px;
  display: block;
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
}

.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}
.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
}
</style>

