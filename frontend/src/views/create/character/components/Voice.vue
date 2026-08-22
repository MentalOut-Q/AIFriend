<script setup>
import {ref, watch} from "vue";
import api from "@/js/http/api.js";

const props = defineProps(['voices', 'curVoiceId'])
const localVoices = ref([])
const myVoice = ref(props.curVoiceId)
const showCustomVoice = ref(false)
const voiceName = ref('')
const voiceFile = ref(null)
const agreed = ref(false)
const isRecording = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')
const recordedAudioUrl = ref('')

let mediaRecorder = null
let mediaStream = null
let audioChunks = []

watch(() => props.curVoiceId, newVal => {
  myVoice.value = newVal
})

watch(() => props.voices, newVal => {
  localVoices.value = [...(newVal || [])]
}, {immediate: true})

function handleFileChange(event) {
  voiceFile.value = event.target.files?.[0] || null
  if (recordedAudioUrl.value) {
    URL.revokeObjectURL(recordedAudioUrl.value)
    recordedAudioUrl.value = ''
  }
}

async function startRecording() {
  errorMessage.value = ''
  if (!navigator.mediaDevices?.getUserMedia) {
    errorMessage.value = '当前浏览器不支持录音'
    return
  }

  try {
    audioChunks = []
    mediaStream = await navigator.mediaDevices.getUserMedia({audio: true})
    mediaRecorder = new MediaRecorder(mediaStream)
    mediaRecorder.ondataavailable = event => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }
    mediaRecorder.onstop = () => {
      const blob = new Blob(audioChunks, {type: mediaRecorder.mimeType || 'audio/webm'})
      voiceFile.value = new File([blob], 'voice-sample.webm', {type: blob.type})
      if (recordedAudioUrl.value) {
        URL.revokeObjectURL(recordedAudioUrl.value)
      }
      recordedAudioUrl.value = URL.createObjectURL(blob)
      mediaStream?.getTracks().forEach(track => track.stop())
      mediaStream = null
    }
    mediaRecorder.start()
    isRecording.value = true
  } catch (err) {
    errorMessage.value = '无法打开麦克风，请检查浏览器权限或使用HTTPS'
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
  isRecording.value = false
}

function closeCustomVoice() {
  if (isRecording.value) {
    stopRecording()
  }
  showCustomVoice.value = false
}

async function submitCustomVoice() {
  errorMessage.value = ''
  if (!voiceName.value.trim()) {
    errorMessage.value = '请填写音色名称'
    return
  }
  if (!voiceFile.value) {
    errorMessage.value = '请录音或上传声音文件'
    return
  }
  if (!agreed.value) {
    errorMessage.value = '请确认该声音已获得授权'
    return
  }

  const formData = new FormData()
  formData.append('name', voiceName.value.trim())
  formData.append('audio', voiceFile.value)
  formData.append('confirm_voice_rights', 'true')

  try {
    isSubmitting.value = true
    const res = await api.post('/api/create/character/voice/custom/create/', formData)
    const data = res.data
    if (data.result === 'success') {
      localVoices.value.push(data.voice)
      myVoice.value = data.voice.id
      voiceName.value = ''
      voiceFile.value = null
      agreed.value = false
      closeCustomVoice()
    } else {
      errorMessage.value = data.result
    }
  } catch (err) {
    errorMessage.value = '音色复刻失败，请稍后重试'
  } finally {
    isSubmitting.value = false
  }
}

defineExpose({
  myVoice,
})
</script>

<template>
  <fieldset class="fieldset">
    <label class="label text-base">音色</label>
    <div class="flex gap-2">
      <select v-model="myVoice" class="select flex-1">
        <option
            v-for="voice in localVoices"
            :key="voice.id"
            :id="voice.id"
            :value="voice.id"
        >{{ voice.name }}</option>
      </select>
      <button type="button" class="btn btn-neutral" @click="showCustomVoice = true">复刻</button>
    </div>
  </fieldset>

  <div v-if="showCustomVoice" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div class="bg-base-100 rounded-lg w-100 max-w-[92vw] p-5 shadow-xl">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold">复刻音色</h3>
        <button type="button" class="btn btn-sm btn-circle btn-ghost" @click="closeCustomVoice">✕</button>
      </div>

      <label class="fieldset mb-2">
        <span class="label text-base">音色名称</span>
        <input v-model="voiceName" class="input w-full" type="text" placeholder="例如：我的声音">
      </label>

      <div class="flex gap-2 my-3">
        <button
            v-if="!isRecording"
            type="button"
            class="btn btn-outline flex-1"
            @click="startRecording"
        >开始录音</button>
        <button
            v-else
            type="button"
            class="btn btn-error flex-1"
            @click="stopRecording"
        >停止录音</button>
      </div>

      <audio v-if="recordedAudioUrl" :src="recordedAudioUrl" controls class="w-full mb-3"></audio>

      <label class="fieldset mb-3">
        <span class="label text-base">或上传声音文件</span>
        <input class="file-input w-full" type="file" accept="audio/*" @change="handleFileChange">
      </label>

      <label class="label justify-start gap-2 mb-3">
        <input v-model="agreed" type="checkbox" class="checkbox checkbox-sm">
        <span>我确认该声音为本人或已获得授权</span>
      </label>

      <p v-if="errorMessage" class="text-sm text-red-500 mb-3">{{ errorMessage }}</p>

      <div class="flex justify-end gap-2">
        <button type="button" class="btn" @click="closeCustomVoice">取消</button>
        <button
            type="button"
            class="btn btn-neutral"
            :disabled="isSubmitting"
            @click="submitCustomVoice"
        >{{ isSubmitting ? '复刻中...' : '创建音色' }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>
