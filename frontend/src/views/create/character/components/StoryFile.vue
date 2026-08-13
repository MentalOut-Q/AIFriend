<script setup>
import {ref} from 'vue'

const props = defineProps({
  fileName: { type: String, default: '' }, // 更新页可显示「已有故事」
})

const storyFile = ref(null)
const displayName = ref(props.fileName || '')

function onFileChange(e) {
  const file = e.target.files[0]
  e.target.value = ''
  if (!file) return
  if (!file.name.endsWith('.txt')) {
    alert('请上传 .txt 文本文件')
    return
  }
  storyFile.value = file
  displayName.value = file.name
}

function clearFile() {
  storyFile.value = null
  displayName.value = props.fileName || ''
}

defineExpose({ storyFile })
</script>

<template>
  <fieldset class="fieldset mt-4">
    <label class="label text-base">角色故事文档（可选）</label>
    <div class="flex items-center gap-2">
      <label class="btn btn-outline btn-sm cursor-pointer">
        上传故事 .txt
        <input type="file" accept=".txt,text/plain" class="hidden" @change="onFileChange">
      </label>
      <span v-if="displayName" class="text-sm text-gray-500 line-clamp-1">{{ displayName }}</span>
      <button
        v-if="storyFile"
        type="button"
        class="btn btn-ghost btn-xs"
        @click="clearFile"
      >
        清除
      </button>
    </div>
    <p class="text-xs text-gray-500 mt-1">用于聊天时检索角色身世/剧情</p>
  </fieldset>
</template>