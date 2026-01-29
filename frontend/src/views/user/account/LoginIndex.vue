<script setup lang="ts">
import {ref} from "vue";
import {useUserStore} from "@/stores/user.js";
import {useRouter} from "vue-router";
import api from "@/js/http/api.js";

const username = ref('')
const password = ref('')
const errorMessage = ref('')

const user = useUserStore()
const router = useRouter()

async function handleLogin() {
  errorMessage.value = ''
  if (!username.value.trim()) {
    errorMessage.value = '用户名不能为空'
  } else if (!password.value.trim()) {
    errorMessage.value = '密码不能为空'
  } else {
    try {
      // 你鼠标中键点那个链接里的login, 跳转到login.py, 这个res的内容和response里的内容完全一致
      const res = await api.post('/api/user/account/login/', {
        username: username.value,
        password: password.value,
      })
      const data = res.data
      if (data.result === 'success') {
        user.setAccessToken(data.access)
        user.setUserInfo(data)
        await router.push({
          name: 'homepage-index' // 返回首页
        })
      } else {
        errorMessage.value = data.result
      }
    } catch (err) {
      console.log(err)
    }
  }
}

</script>

<template>
  <div class="flex justify-center mt-10">
    <form @submit.prevent="handleLogin"> <!-- .prevent表示阻止默认行为, 这样点登录就不刷新了  -->
      <fieldset class="fieldset bg-base-200 border-base-300 rounded-box w-xs border p-4">
        <legend class="fieldset-legend">Login</legend>

        <label class="label">用户名</label>
        <input v-model="username" type="text" class="input" placeholder="Username" />

        <label class="label">密码</label>
        <input v-model="password" type="password" class="input" placeholder="Password" />

        <p v-if="errorMessage" class="text-sm text-red-500 mt-1">{{ errorMessage }}</p>


        <button class="btn btn-neutral mt-4">登录</button>
        <div class="flex justify-end">
          <RouterLink :to="{name: 'user-account-register-index'}" class="btn btn-sm btn-ghost text-gray-500">注册</RouterLink>
        </div>
      </fieldset>
    </form>
  </div>
</template>

<style scoped>

</style>