<script setup>
import {useUserStore} from "@/stores/user.js";

defineProps({
  userProfile: Object,
  mode: {
    type: String, // 'character' | 'post'
    default: '',
  },
})

const user = useUserStore()
</script>

<template>
  <div v-if="userProfile" class="flex flex-col items-center mt-12 gap-4">
    <!-- 头像 + 文字信息（恢复原来布局，不固定高度） -->
    <div class="flex items-center gap-8">
      <div class="avatar">
        <div class="w-44 rounded-full">
          <img :src="userProfile.photo" alt="">
        </div>
      </div>
      <div class="flex flex-col justify-center w-64">
        <div class="text-2xl font-bold line-clamp-1 break-all">{{ userProfile.username }}</div>
        <div class="text-sm text-gray-500 mt-2">AIFriends号：{{ userProfile.user_id }}</div>
        <div class="text-sm h-20 mt-4 line-clamp-4 break-all">{{ userProfile.profile }}</div>
      </div>
    </div>

    <!-- 跳转按钮：独立一行，在信息区下方 -->
    <div v-if="mode">
      <RouterLink
        v-if="mode === 'character'"
        :to="{ name: 'post-index', query: { user_id: userProfile.user_id } }"
        class="btn btn-outline btn-sm"
      >
        {{ userProfile.user_id === user.id ? '我的动态' : '查看 TA 的动态' }}
      </RouterLink>

      <RouterLink
        v-else-if="mode === 'post'"
        :to="{ name: 'user-space-index', params: { user_id: userProfile.user_id } }"
        class="btn btn-outline btn-sm"
      >
        {{ userProfile.user_id === user.id ? '我的角色' : '查看 TA 的角色' }}
      </RouterLink>
    </div>
  </div>
</template>