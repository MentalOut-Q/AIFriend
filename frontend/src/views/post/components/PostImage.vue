<script setup>
import {ref, useTemplateRef} from "vue";
import CameraIcon from "@/views/user/profile/components/icon/CameraIcon.vue";

const myPhoto = ref('')   // 预览用
const myFile = ref(null)  // 上传用

const fileInputRef = useTemplateRef('file-input-ref')

function onFileChange(e) {
  const file = e.target.files[0]
  e.target.value = ''
  if (!file) return

  if (myPhoto.value.startsWith('blob:')) {
    URL.revokeObjectURL(myPhoto.value)
  }

  myFile.value = file
  myPhoto.value = URL.createObjectURL(file)
}

function clearImage() {
  if (myPhoto.value.startsWith('blob:')) {
    URL.revokeObjectURL(myPhoto.value)
  }
  myPhoto.value = ''
  myFile.value = null
}

defineExpose({
  myPhoto,
  myFile,
})
</script>

<template>
  <div class="flex flex-col items-center w-full">
    <div v-if="myPhoto" class="relative w-full">
      <img :src="myPhoto" class="rounded-xl w-full max-h-60 object-contain bg-base-300/30" alt="">
      <button @click="clearImage" type="button" class="btn btn-circle btn-sm btn-ghost absolute right-2 top-2">✕</button>
    </div>
    <div
      v-else
      @click="fileInputRef.click()"
      class="w-full h-40 rounded-xl border-2 border-dashed border-base-content/20 flex flex-col items-center justify-center cursor-pointer hover:bg-base-200/30"
    >
      <CameraIcon />
      <span class="text-sm text-gray-500 mt-2">点击添加图片（可选）</span>
    </div>
    <input ref="file-input-ref" type="file" accept="image/*" class="hidden" @change="onFileChange">
  </div>
</template>