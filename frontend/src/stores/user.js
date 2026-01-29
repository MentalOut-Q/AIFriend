import {defineStore} from "pinia";
import {ref} from "vue";

export const useUserStore = defineStore('user', () => {
    const id = ref(0)
    const username = ref('')
    const photo = ref('')
    const profile = ref('')
    const accessToken = ref('')
    const hasPulledUserInfo = ref(false)

    function isLogin() {
        return !!accessToken.value  // 必须带value!!!!!!!!!不带value永远都不空
    }

    function setHasPulledUserInfo(newStatus) {
        hasPulledUserInfo.value = newStatus
    }

    function setAccessToken(token) {
        accessToken.value = token
    }

    // data的内容和backend/web/views/user/account/login.py中的一一对应
    function setUserInfo(data) {
        id.value = data.user_id
        username.value = data.username
        photo.value = data.photo
        profile.value = data.profile
    }

    function logout() {
        id.value = 0
        username.value = ''
        photo.value = ''
        profile.value = ''
        accessToken.value = ''
    }

    return {
        id,
        username,
        photo,
        profile,
        accessToken,  // 千万不要忘了！！！！
        isLogin,
        setAccessToken,
        setUserInfo,
        logout,
        hasPulledUserInfo,
        setHasPulledUserInfo,
    }
})
