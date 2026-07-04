<script setup>
import NavBar from "@/components/navbar/NavBar.vue";
import {onMounted} from "vue";
import {useUserStore} from "@/stores/user.js";
import api from "@/js/http/api.js";
import {useRoute, useRouter} from "vue-router";
import bgImage from '@/assets/bg.jpg'

const user = useUserStore()
const route = useRoute()
const router = useRouter()

onMounted(async () => {
  try {
    const res = await api.get('/api/user/account/get_user_info/')
    const data = res.data
    if (data.result === 'success') {
      user.setUserInfo(data)
    }
  } catch (err) {
  } finally {
    user.setHasPulledUserInfo(true)

    if (route.meta.needLogin && !user.isLogin()) {
      await router.replace({
        name: 'user-account-login-index',
      })
    }
  }
})

</script>

<template>
  <div class="min-h-screen bg-cover bg-center bg-fixed bg-no-repeat"
    :style="{ backgroundImage: `url(${bgImage})` }"
  >
    <NavBar>
        <RouterView/> <!--根据url在router的index.js里面找, 把对应的Index渲染出来-->
    </NavBar>
  </div>
</template>

<style scoped>

</style>
