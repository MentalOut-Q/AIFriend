<script setup>
import {nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef} from "vue";
import {useRouter} from "vue-router";
import {useUserStore} from "@/stores/user.js";
import api from "@/js/http/api.js";

const posts = ref([])
const isLoading = ref(false)
const hasPosts = ref(true)
const sentinelRef = useTemplateRef('sentinel-ref')
const commentModalRef = useTemplateRef('comment-modal-ref')

const commentPostId = ref(null)
const commentContent = ref('')
const commentImageFile = ref(null)
const commentImagePreview = ref('')

const user = useUserStore()
const router = useRouter()

function checkSentinelVisible() {
  if (!sentinelRef.value) return false
  const rect = sentinelRef.value.getBoundingClientRect()
  return rect.top < window.innerHeight && rect.bottom > 0
}

async function loadMore() {
  if (isLoading.value || !hasPosts.value) return
  isLoading.value = true

  let newPosts = []
  try {
    const res = await api.get('/api/post/get_list/', {
      params: {
        items_count: posts.value.length,
      }
    })
    const data = res.data
    if (data.result === 'success') {
      newPosts = data.posts
    }
  } catch (err) {
  } finally {
    isLoading.value = false
    if (newPosts.length === 0) {
      hasPosts.value = false
    } else {
      posts.value.push(...newPosts)
      await nextTick()
      if (checkSentinelVisible()) {
        await loadMore()
      }
    }
  }
}

async function requireLogin() {
  if (user.isLogin()) return true
  await router.push({name: 'user-account-login-index'})
  return false
}

async function toggleLike(post) {
  if (!(await requireLogin())) return
  try {
    const res = await api.post('/api/post/like/toggle/', {post_id: post.id})
    if (res.data.result === 'success') {
      post.is_liked = res.data.is_liked
      post.like_count = res.data.like_count
    }
  } catch (err) {}
}

async function toggleFavorite(post) {
  if (!(await requireLogin())) return
  try {
    const res = await api.post('/api/post/favorite/toggle/', {post_id: post.id})
    if (res.data.result === 'success') {
      post.is_favorited = res.data.is_favorited
      post.favorite_count = res.data.favorite_count
    }
  } catch (err) {}
}

function clearCommentImage() {
  if (commentImagePreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(commentImagePreview.value)
  }
  commentImagePreview.value = ''
  commentImageFile.value = null
}

async function openCommentModal(post) {
  if (!(await requireLogin())) return
  commentPostId.value = post.id
  commentContent.value = ''
  clearCommentImage()
  commentModalRef.value.showModal()
}

function onCommentImageChange(e) {
  const file = e.target.files[0]
  e.target.value = ''
  if (!file) return

  if (commentImagePreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(commentImagePreview.value)
  }

  commentImageFile.value = file
  commentImagePreview.value = URL.createObjectURL(file)
}

async function submitComment() {
  const content = commentContent.value.trim()
  if (!content && !commentImageFile.value) {
    alert('评论内容和图片不能同时为空')
    return
  }

  const formData = new FormData()
  formData.append('post_id', commentPostId.value)
  formData.append('content', content)
  if (commentImageFile.value) {
    formData.append('image', commentImageFile.value)
  }

  try {
    const res = await api.post('/api/post/comment/create/', formData)
    if (res.data.result === 'success') {
      const post = posts.value.find(p => p.id === commentPostId.value)
      if (post) post.comment_count += 1
      commentModalRef.value.close()
    } else {
      alert(res.data.result)
    }
  } catch (err) {
    alert('评论失败，请稍后重试')
  }
}

async function handleRemove(post) {
  if (!(await requireLogin())) return
  if (post.author.user_id !== user.id) return
  if (!confirm('确定删除这条动态吗？')) return
  try {
    const res = await api.post('/api/post/remove/', {post_id: post.id})
    if (res.data.result === 'success') {
      posts.value = posts.value.filter(p => p.id !== post.id)
    } else {
      alert(res.data.result)
    }
  } catch (err) {}
}

let observer = null
onMounted(async () => {
  await loadMore()
  observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) loadMore()
      })
    },
    {root: null, rootMargin: '2px', threshold: 0}
  )
  observer.observe(sentinelRef.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()
  clearCommentImage()
})
</script>

<template>
  <div class="flex flex-col items-center mb-12 px-4">
    <div class="w-full max-w-2xl flex flex-col gap-6 mt-12">
      <div
        v-for="post in posts"
        :key="post.id"
        class="card bg-base-200/80 backdrop-blur-sm shadow-sm"
      >
        <div class="card-body">
          <!-- 作者 -->
          <div class="flex items-center gap-3">
            <RouterLink
              :to="{name: 'user-space-index', params: {user_id: post.author.user_id}}"
              class="avatar"
            >
              <div class="w-10 rounded-full">
                <img :src="post.author.photo" alt="">
              </div>
            </RouterLink>
            <div class="flex flex-col min-w-0">
              <RouterLink
                :to="{name: 'user-space-index', params: {user_id: post.author.user_id}}"
                class="font-bold line-clamp-1 break-all hover:underline"
              >
                {{ post.author.username }}
              </RouterLink>
              <span class="text-xs text-gray-500">{{ post.create_time }}</span>
            </div>
            <button
              v-if="user.isLogin() && post.author.user_id === user.id"
              @click="handleRemove(post)"
              type="button"
              class="btn btn-ghost btn-sm ml-auto"
            >
              删除
            </button>
          </div>

          <!-- 正文 -->
          <p v-if="post.content" class="whitespace-pre-wrap break-all mt-2">{{ post.content }}</p>

          <!-- 图片 -->
          <img
            v-if="post.image"
            :src="post.image"
            class="mt-3 rounded-xl w-full max-h-96 object-contain bg-base-300/30"
            alt=""
          >

          <!-- 互动 -->
          <div class="flex flex-wrap gap-2 mt-3">
            <button
              @click="toggleLike(post)"
              type="button"
              class="btn btn-ghost btn-sm"
              :class="{'text-error': post.is_liked}"
            >
              {{ post.is_liked ? '已赞' : '点赞' }} {{ post.like_count }}
            </button>
            <button
              @click="toggleFavorite(post)"
              type="button"
              class="btn btn-ghost btn-sm"
              :class="{'text-warning': post.is_favorited}"
            >
              {{ post.is_favorited ? '已藏' : '收藏' }} {{ post.favorite_count }}
            </button>
            <button @click="openCommentModal(post)" type="button" class="btn btn-ghost btn-sm">
              评论 {{ post.comment_count }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div ref="sentinel-ref" class="h-2 mt-8"></div>
    <div v-if="isLoading" class="text-gray-500 mt-4">加载中...</div>
    <div v-else-if="!hasPosts && posts.length === 0" class="text-gray-500 mt-4">还没有动态，去发一条吧</div>
    <div v-else-if="!hasPosts" class="text-gray-500 mt-4">没有更多了</div>
  </div>

  <!-- 评论弹窗：文字 + 可选图片，无裁剪 -->
  <dialog ref="comment-modal-ref" class="modal">
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">发表评论</h3>

      <textarea
        v-model="commentContent"
        rows="4"
        class="textarea w-full"
        placeholder="写下你的评论..."
      />

      <div class="mt-4">
        <img
          v-if="commentImagePreview"
          :src="commentImagePreview"
          class="rounded-lg w-full max-h-48 object-contain bg-base-300/30"
          alt=""
        >
        <div class="flex gap-2 mt-2">
          <label class="btn btn-sm btn-outline cursor-pointer">
            选图片（可选）
            <input type="file" accept="image/*" class="hidden" @change="onCommentImageChange">
          </label>
          <button
            v-if="commentImagePreview"
            @click="clearCommentImage"
            type="button"
            class="btn btn-sm btn-ghost"
          >
            移除图片
          </button>
        </div>
      </div>

      <div class="modal-action">
        <form method="dialog">
          <button type="button" class="btn">取消</button>
        </form>
        <button @click="submitComment" type="button" class="btn btn-neutral">发送</button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button>close</button>
    </form>
  </dialog>
</template>