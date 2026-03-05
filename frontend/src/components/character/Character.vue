<script setup>
import {ref, useTemplateRef} from "vue";
import {useUserStore} from "@/stores/user.js";
import UpdateIcon from "@/components/character/icons/UpdateIcon.vue";
import RemoveIcon from "@/components/character/icons/RemoveIcon.vue";
import api from "@/js/http/api.js";
import ChatField from "@/components/character/chat_field/ChatField.vue";
import {useRouter} from "vue-router";

const props = defineProps(['character', 'canEdit', 'canRemoveFriend', 'friendId', 'characterUpdateTime', 'friendUpdateTime'])
const emit = defineEmits(['remove'])
const isHover = ref(false)
const user = useUserStore()

const showDeleteModal = ref(false)
// 新增：标记当前要删除的类型（'character' 或 'friend'）和对应的ID
const deleteType = ref('')
const deleteId = ref('')

// 统一的确认删除逻辑（根据 deleteType 执行不同操作）
async function confirmDelete() {
  try {
    let res;
    // 根据删除类型调用不同接口
    if (deleteType.value === 'character') {
      res = await api.post('/api/create/character/remove/', {
        character_id: deleteId.value,
      })
    } else if (deleteType.value === 'friend') {
      res = await api.post('/api/friend/remove/', {
        friend_id: deleteId.value,
      })
    }

    if (res?.data?.result === 'success') {
      emit('remove', deleteId.value)
    } else {
      alert(res?.data?.result || '删除失败')
    }
  } catch (err) {
    alert('系统异常，删除失败')
    console.error(`删除${deleteType.value}失败：`, err)
  } finally {
    showDeleteModal.value = false
    // 清空标记，避免下次误触发
    deleteType.value = ''
    deleteId.value = ''
  }
}

// 打开弹窗的通用方法（传入类型和ID）
function openDeleteModal(type, id) {
  deleteType.value = type
  deleteId.value = id
  showDeleteModal.value = true
}

// 角色删除按钮点击事件
function handleRemoveCharacter() {
  openDeleteModal('character', props.character.id)
}

// 好友删除按钮点击事件
function handleRemoveFriend() {
  openDeleteModal('friend', props.friendId)
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
          <RouterLink @click.stop :to="{name: 'update-character', params: {character_id: character.id}}" class="btn btn-circle btn-ghost bg-transparent">
            <UpdateIcon />
          </RouterLink>
          <button @click.stop="handleRemoveCharacter" class="btn btn-circle btn-ghost bg-transparent">
            <RemoveIcon />
          </button>
        </div>

         <div v-if="canRemoveFriend" class="absolute right-0 top-50">
          <button @click.stop="handleRemoveFriend" class="btn btn-circle btn-ghost bg-transparent">
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
      <div v-if="characterUpdateTime" class="text-sm text-gray-500 ml-auto">
        更新于: {{characterUpdateTime}}
      </div>
      <div v-if="friendUpdateTime" class="text-sm text-gray-500 ml-auto">
        相识于: {{friendUpdateTime}}
      </div>
    </RouterLink>

    <!-- 复用的删除模态框（根据 deleteType 动态显示提示） -->
    <div v-if="showDeleteModal" class="modal modal-open">
      <div class="modal-box relative max-w-md">
        <h3 class="font-bold text-lg text-red-400">确认删除</h3>
        <p class="py-4">
          <!-- 动态提示文案：删除角色/好友的不同话术 -->
          <template v-if="deleteType === 'character'">
            确定要删除角色【{{ character.name }}】吗？删除后不可恢复！
          </template>
          <template v-else-if="deleteType === 'friend'">
            确定要移除好友【{{ character.name }}】吗？移除后将无法再和TA聊天！
          </template>
        </p>
        <div class="modal-action flex justify-end gap-2">
          <button @click="showDeleteModal = false" class="btn btn-outline">取消</button>
          <!-- 绑定统一的确认删除方法 -->
          <button @click="confirmDelete" class="btn btn-warning">确认</button>
        </div>
      </div>
      <div class="modal-backdrop" @click="showDeleteModal = false"></div>
    </div>

    <ChatField ref="chat-field-ref" :friend="friend" />
  </div>
</template>

<style scoped>

</style>