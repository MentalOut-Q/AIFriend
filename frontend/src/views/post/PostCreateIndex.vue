<script setup>
import {ref, useTemplateRef} from "vue";
import {useRouter} from "vue-router";
import {useUserStore} from "@/stores/user.js";
import api from "@/js/http/api.js";
import PostImage from "@/views/post/components/PostImage.vue";

const content = ref('')
const errorMessage = ref('')
const imageRef = useTemplateRef('image-ref')

const user = useUserStore()
const router = useRouter()

async function handlePublish() {
  const text = content.value.trim()
  const imageFile = imageRef.value?.myFile

  errorMessage.value = ''
  if (!text && !imageFile) {
    errorMessage.value = '写点内容或选张图吧'
    return
  }

  const formData = new FormData()
  formData.append('content', text)
  if (imageFile) {
    formData.append('image', imageFile)
  }

  try {
    const res = await api.post('/api/post/create/', formData)
    const data = res.data
    if (data.result === 'success') {
      await router.push({
        name: 'user-space-index',
        params: {user_id: user.id},
        query: {tab: 'posts'},
      })
    } else {
      errorMessage.value = data.result
    }
  } catch (err) {
    errorMessage.value = '发布失败，请稍后重试'
  }
}
</script>

<template>
  <div class="flex justify-center">
    <div class="card w-120 bg-base-200/80 backdrop-blur-sm shadow-sm mt-16">
      <div class="card-body">
        <h3 class="text-lg font-bold my-2">发布动态</h3>

        <fieldset class="fieldset">
          <label class="label text-base">内容</label>
          <textarea
            v-model="content"
            rows="6"
            class="textarea w-full"
            placeholder="分享你的想法..."
          />
        </fieldset>

        <PostImage ref="image-ref" class="mt-4" />

        <p v-if="errorMessage" class="text-sm text-red-500 mt-2">{{ errorMessage }}</p>

        <div class="flex justify-center mt-4">
          <button @click="handlePublish" type="button" class="btn btn-neutral w-60">发布</button>
        </div>
      </div>
    </div>
  </div>
</template>