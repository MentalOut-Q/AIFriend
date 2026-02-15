<script setup>
import {ref, useTemplateRef} from "vue";
import {useUserStore} from "@/stores/user.js";
import UpdateIcon from "@/components/character/icons/UpdateIcon.vue";
import RemoveIcon from "@/components/character/icons/RemoveIcon.vue";
import api from "@/js/http/api.js";
import ChatField from "@/components/character/chat_field/ChatField.vue";
import {useRouter} from "vue-router";

const props = defineProps(['character', 'canEdit'])
const emit = defineEmits(['remove'])
const isHover = ref(false)
const user = useUserStore()

const showDeleteModal = ref(false)

// 确认删除逻辑
async function confirmRemove() {
  try {
    const res = await api.post('/api/create/character/remove/', {
      character_id: props.character.id,
    })
    if (res.data.result === 'success') {
      emit('remove', props.character.id)
    } else {
      alert(res.data.result || '删除失败')
    }
  } catch (err) {
    alert('系统异常，删除失败')
    console.error('删除角色失败：', err)
  } finally {
    // 无论成功失败，关闭弹窗
    showDeleteModal.value = false
  }
}

// 点击删除按钮仅打开弹窗
function handleRemoveCharacter() {
  showDeleteModal.value = true
}

const chatFieldRef = useTemplateRef('chat-field-ref')
const friend = ref(null)
const router = useRouter()

async function openChatField() {
  if (!user.isLogin()) {
    await router.push({
      name: 'user-account-login-index'
    })
  } else {
    try {
      const res = await api.post('/api/friend/get_or_create/', {
        character_id: props.character.id,
      })
      const data = res.data
      if (data.result === 'success') {
        friend.value = data.friend
        chatFieldRef.value.showModal()
      }
    } catch (err) {
      console.log(err)
    }
  }
}

</script>

<template>
  <div>
    <div class="avatar cursor-pointer" @mouseover="isHover=true" @mouseout="isHover=false" @click="openChatField">
      <div class="w-60 h-100 rounded-2xl relative">
        <img :src="character.background_image" class="transition-transform duration-300" :class="{'scale-120': isHover}" alt="">
        <div class="absolute left-0 top-50 w-60 h-50 bg-linear-to-t from-black/40 to-transparent"></div>

        <div v-if="canEdit && character.author.user_id === user.id" class="absolute right-0 top-50">
          <RouterLink :to="{name: 'update-character', params: {character_id: character.id}}" class="btn btn-circle btn-ghost bg-transparent">
            <UpdateIcon />
          </RouterLink>
          <button @click="handleRemoveCharacter" class="btn btn-circle btn-ghost bg-transparent">
            <RemoveIcon />
          </button>
        </div>

        <div class="absolute left-4 top-54 avatar">
          <div class="w-16 rounded-full ring-3 ring-white">
            <img :src="character.photo" alt="">
          </div>
        </div>
        <div class="absolute left-24 right-4 top-58 text-white font-bold line-clamp-1 break-all">
          {{ character.name }}
        </div>
        <div class="absolute left-4 right-4 top-72 text-white line-clamp-4 break-all">
          {{ character.profile }}
        </div>
      </div>
    </div>
    <RouterLink :to="{name: 'user-space-index', params: {user_id: character.author.user_id}}" class="flex items-center mt-4 gap-2 w-60">
      <div class="avatar">
        <div class="w-7 rounded-full">
          <img :src="character.author.photo" alt="">
        </div>
      </div>
      <div class="text-sm line-clamp-1 break-all">{{ character.author.username }}</div>
      <div class="text-sm text-gray-500 ml-auto">
        {{character.create_time}}
      </div>
    </RouterLink>

    <!-- 核心：daisyUI 确认删除弹窗（modal 组件） -->
    <div v-if="showDeleteModal" class="modal modal-open">
      <div class="modal-box relative max-w-md">
        <h3 class="font-bold text-lg text-red-400">确认删除</h3>
        <p class="py-4">确定不要{{ character.name }}了吗？</p>
        <div class="modal-action flex justify-end gap-2">
          <button @click="showDeleteModal = false" class="btn btn-outline">取消</button>
          <button @click="confirmRemove" class="btn btn-warning">确认</button>
        </div>
      </div>
      <!-- 蒙层（点击可关闭弹窗） -->
      <div class="modal-backdrop" @click="showDeleteModal = false"></div>
    </div>

    <ChatField ref="chat-field-ref" :friend="friend" />
  </div>
</template>

<style scoped>

</style>