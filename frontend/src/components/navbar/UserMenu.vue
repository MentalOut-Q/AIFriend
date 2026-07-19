<script setup>
import {useUserStore} from "@/stores/user.js";
import UserProfileIcon from "@/components/navbar/icons/UserProfileIcon.vue";
import UserLogoutIcon from "@/components/navbar/icons/UserLogoutIcon.vue";
import api from "@/js/http/api.js";
import {useRouter} from "vue-router";
import UserSpaceIcon from "@/components/navbar/icons/UserSpaceIcon.vue";
import UserCharacter from "@/components/navbar/icons/UserCharacter.vue";
import FavoriteIcon from "@/views/post/icons/FavoriteIcon.vue";

const user = useUserStore()
const router = useRouter()

function closeMenu() {
  const element = document.activeElement
  if (element && element instanceof HTMLElement) element.blur()
}

async function handleLogout() {
  try {
    const res = await api.post('/api/user/account/logout/')
    if (res.data.result === 'success') {
      user.logout()
      await router.push({
        name: 'homepage-index' // 返回首页
      })
    }
  } catch (err) {

  }
}

</script>

<template>
  <div class="dropdown dropdown-end">
    <div tabindex="0" role="button" class="avatar btn btn-circle w-8 h-8 mr-6">
      <div class="w-8 rounded-full">
        <img :src="user.photo" alt="">
      </div>
    </div>
    <ul tabindex="-1" class="dropdown-content menu bg-base-100 rounded-box z-1 w-48 p-2 shadow-lg">
      <li>
        <RouterLink @click="closeMenu" :to="{name: 'user-space-index', params: {user_id: user.id}}">
          <div class="avatar">
            <div class="w-10 rounded-full">
              <img :src="user.photo" alt="">
            </div>
          </div>
          <span class="text-base font-bold line-clamp-1 break-all">{{ user.username }}</span>
        </RouterLink>
      </li>
      <li>
        <RouterLink @click="closeMenu" :to="{name: 'user-space-index', params: {user_id: user.id}}" class="text-sm font-bold py-3">
          <UserCharacter />
          我的角色
        </RouterLink>
      </li>
      <li>
        <RouterLink @click="closeMenu" :to="{name: 'post-index', query: {user_id: user.id}}" class="text-sm font-bold py-3">
          <UserSpaceIcon />
          我的动态
        </RouterLink>
      </li>
      <li>
        <RouterLink @click="closeMenu" :to="{name: 'post-index', query: {favorites: 1}}" class="text-sm font-bold py-3">
          <FavoriteIcon class="w-5 h-5" />
          我的收藏
        </RouterLink>
      </li>
      <li>
        <RouterLink @click="closeMenu" :to="{name: 'user-profile-index'}" class="text-sm font-bold py-3">
          <UserProfileIcon />
          编辑资料
        </RouterLink>
      </li>
      <li></li>
      <li>
        <a @click="handleLogout" class="text-sm font-bold py-3">
          <UserLogoutIcon />
          退出登录
        </a>
      </li>
    </ul>
  </div>
</template>

<style scoped>

</style>
