<script setup>
import KeyboardIcon from "@/components/character/icons/KeyboardIcon.vue";
import {ref} from "vue";

const emit = defineEmits(['close'])
const isSpeaking = ref(false)
</script>

<template>
<div class="absolute bottom-4 left-2 h-12 w-86 flex items-center bg-black/30 backdrop-blur-sm rounded-2xl">
    <div v-if="isSpeaking" class="flex items-center justify-center gap-1 h-6 flex-1">
      <div
        v-for="i in 32" :key="i"
        class="w-0.5 bg-blue-400 rounded-full animate-wave"
        :style="{ animationDelay: `${i * 0.1}s` }"
      ></div>
    </div>
    <div v-else class="text-white/50 text-base w-full text-center">
      语音输入
    </div>
    <div @click="emit('close')" class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
      <KeyboardIcon />
    </div>
  </div>

</template>

<style scoped>
.animate-wave {
  height: 4px;
  animation: wave-animation 0.6s ease-in-out infinite alternate;
}

@keyframes wave-animation {
  0% { height: 4px; opacity: 0.3; }
  100% { height: 20px; opacity: 1; }
}
</style>