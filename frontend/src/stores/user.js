import {defineStore} from "pinia";
import {ref} from "vue";

export const useUserStore = defineStore('user', () => {
    const id = ref(1)
    const username = ref('q')
    const photo = ref('http://127.0.0.1:8000/media/user/photos/default.png')
    const profile = ref('111')
    const accessToken = ref('111')

    function isLogin() {
        return !!accessToken.value  // 必须带value!!!!!!!!!不带value永远都不空
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
    }
})
