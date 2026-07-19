<script setup>
import {nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef, watch} from "vue";
import {useRoute, useRouter} from "vue-router";
import {useUserStore} from "@/stores/user.js";
import api from "@/js/http/api.js";

import UserInfoField from "@/views/user/space/components/UserInfoField.vue";
import ChooseIcon from "@/views/post/icons/ChooseIcon.vue";

import LikeIcon from "@/views/post/icons/LikeIcon.vue";
import FavoriteIcon from "@/views/post/icons/FavoriteIcon.vue";
import CommentIcon from "@/views/post/icons/CommentIcon.vue";

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

const expandedPostId = ref(null)
const currentComments = ref([])
const commentsLoading = ref(false)

async function loadComments(postId) {
  commentsLoading.value = true
  try {
    const res = await api.get('/api/post/get_single/', {
      params: {post_id: postId},
    })
    if (res.data.result === 'success') {
      currentComments.value = res.data.post.comments
    }
  } catch (err) {
  } finally {
    commentsLoading.value = false
  }
}

async function toggleComments(post) {
  // 再次点击同一条 → 收起
  if (expandedPostId.value === post.id) {
    expandedPostId.value = null
    currentComments.value = []
    return
  }

  expandedPostId.value = post.id
  await loadComments(post.id)
}

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
    const params = {
      items_count: posts.value.length,
    }
    // 我的收藏
    if (route.query.favorites) {
      params.favorites = 1
    } else if (route.query.user_id) {
      // 只查看该用户的所有动态
      params.user_id = route.query.user_id
    }
    const res = await api.get('/api/post/get_list/', {params})
    const data = res.data
    if (data.result === 'success') {
      newPosts = data.posts
      if (data.user_profile) {
        userProfile.value = data.user_profile
      }
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
  } catch (err) {
  }
}

async function toggleFavorite(post) {
  if (!(await requireLogin())) return
  try {
    const res = await api.post('/api/post/favorite/toggle/', {post_id: post.id})
    if (res.data.result === 'success') {
      post.is_favorited = res.data.is_favorited
      post.favorite_count = res.data.favorite_count
      // 在「我的收藏」页取消收藏后从列表移除
      if (route.query.favorites && !post.is_favorited) {
        posts.value = posts.value.filter(p => p.id !== post.id)
      }
    }
  } catch (err) {
  }
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

      if (expandedPostId.value === commentPostId.value) {
        await loadComments(commentPostId.value)
      }
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
  } catch (err) {
  }
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
  clearEditImage()
})

const route = useRoute()
const userProfile = ref(null)

function reset() {
  posts.value = []
  userProfile.value = null
  isLoading.value = false
  hasPosts.value = true
  loadMore()
}

watch(() => [route.query.user_id, route.query.favorites], () => {
  reset()
})

function closeMenu() {
  const element = document.activeElement
  if (element && element instanceof HTMLElement) element.blur()
}


const editModalRef = useTemplateRef('edit-modal-ref')
const editPostId = ref(null)
const editContent = ref('')
const editImagePreview = ref('')
const editImageFile = ref(null)
const editRemoveImage = ref(false)

const imagePreviewModalRef = useTemplateRef('image-preview-modal-ref')
const previewImageUrl = ref('')
const previewScale = ref(1)

function openImagePreview(url) {
  if (!url) return
  previewImageUrl.value = url
  previewScale.value = 1
  imagePreviewModalRef.value.showModal()
}

function onPreviewWheel(e) {
  e.preventDefault()
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  const next = previewScale.value + delta
  previewScale.value = Math.min(5, Math.max(0.5, Number(next.toFixed(2))))
}

function clearEditImage() {
  if (editImagePreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(editImagePreview.value)
  }
  editImagePreview.value = ''
  editImageFile.value = null
}

function openEditModal(post) {
  closeMenu()
  editPostId.value = post.id
  editContent.value = post.content
  editImagePreview.value = post.image || ''
  editImageFile.value = null
  editRemoveImage.value = false
  editModalRef.value.showModal()
}

function onEditImageChange(e) {
  const file = e.target.files[0]
  e.target.value = ''
  if (!file) return

  if (editImagePreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(editImagePreview.value)
  }

  editImageFile.value = file
  editImagePreview.value = URL.createObjectURL(file)
  editRemoveImage.value = false
}

function removeEditImage() {
  clearEditImage()
  editRemoveImage.value = true
}

async function submitEdit() {
  const content = editContent.value.trim()
  const post = posts.value.find(p => p.id === editPostId.value)
  const willHaveImage = !!editImageFile.value || (!!post?.image && !editRemoveImage.value)

  if (!content && !willHaveImage) {
    alert('内容和图片不能同时为空')
    return
  }

  const formData = new FormData()
  formData.append('post_id', editPostId.value)
  formData.append('content', content)
  if (editImageFile.value) {
    formData.append('image', editImageFile.value)
  } else if (editRemoveImage.value) {
    formData.append('remove_image', 'true')
  }

  try {
    const res = await api.post('/api/post/update/', formData)
    if (res.data.result === 'success' && post) {
      post.content = res.data.content
      post.image = res.data.image
      editModalRef.value.close()
    } else {
      alert(res.data.result)
    }
  } catch (err) {
    alert('修改失败，请稍后重试')
  }
}
</script>

<template>
  <div class="flex flex-col items-center mb-12 px-4">
    <!-- 有 user_id 时显示作者信息 + 标题 -->
    <UserInfoField v-if="userProfile && !route.query.favorites" :userProfile="userProfile" mode="post"/>
    <h2 v-if="route.query.favorites" class="text-xl font-bold mt-4 w-full max-w-2xl">
      我的收藏
    </h2>
    <h2 v-else-if="route.query.user_id" class="text-xl font-bold mt-4 w-full max-w-2xl">
      {{ Number(route.query.user_id) === user.id ? '我的动态' : 'TA 的动态' }}
    </h2>
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
                :to="{name: 'post-index', query: {user_id: post.author.user_id}}"
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

            <div
                v-if="user.isLogin() && post.author.user_id === user.id"
                class="dropdown dropdown-end ml-auto"
            >
              <ChooseIcon/>
              <!-- 展开菜单 -->
              <ul
                  tabindex="0"
                  class="dropdown-content menu bg-base-100 rounded-box z-20 w-36 p-2 shadow-lg"
              >
                <li>
                  <a @click="closeMenu(); openEditModal(post)">更改</a>
                </li>
                <li>
                  <a @click="closeMenu(); handleRemove(post)" class="text-error">删除</a>
                </li>
              </ul>
            </div>
          </div>

          <!-- 正文 -->
          <p v-if="post.content" class="whitespace-pre-wrap break-all mt-2">{{ post.content }}</p>

          <!-- 图片 -->
          <img
              v-if="post.image"
              :src="post.image"
              @click="openImagePreview(post.image)"
              class="mt-3 rounded-xl w-full max-h-96 object-contain bg-base-300/30 cursor-pointer"
              alt=""
          >

          <!-- 互动 -->
          <div class="flex items-center gap-1 mt-3">
            <button
                @click="toggleLike(post)"
                type="button"
                class="btn btn-ghost btn-sm gap-1"
                :class="{'text-error': post.is_liked}"
            >
              <LikeIcon/>
              <span class="text-sm">{{ post.like_count }}</span>
            </button>

            <button
                @click="toggleFavorite(post)"
                type="button"
                class="btn btn-ghost btn-sm gap-1"
                :class="{'text-warning': post.is_favorited}"
            >
              <FavoriteIcon/>
              <span class="text-sm">{{ post.favorite_count }}</span>
            </button>

            <button
                @click="toggleComments(post)"
                type="button"
                class="btn btn-ghost btn-sm gap-1"
                :class="{'text-primary': expandedPostId === post.id}"
            >
              <CommentIcon/>
              <span class="text-sm">{{ post.comment_count }}</span>
            </button>
          </div>

          <!-- 评论列表 -->
          <div
              v-if="expandedPostId === post.id"
              class="w-full mt-4 pt-4 border-t border-base-content/10"
          >
            <div v-if="commentsLoading" class="text-sm text-gray-500">
              评论加载中...
            </div>

            <div v-else-if="currentComments.length === 0" class="text-sm text-gray-500">
              暂无评论
            </div>

            <div
                v-for="comment in currentComments"
                :key="comment.id"
                class="flex items-start gap-3 mb-4 w-full"
            >
              <!-- 左侧：小圆头像 -->
              <RouterLink
                  :to="{ name: 'user-space-index', params: { user_id: comment.author.user_id } }"
                  class="shrink-0 self-start"
              >
                <div class="avatar">
                  <div class="w-8 h-8 rounded-full overflow-hidden">
                    <img
                        :src="comment.author.photo"
                        alt=""
                        class="w-full h-full object-cover"
                    >
                  </div>
                </div>
              </RouterLink>

              <!-- 右侧：用户名+时间在上，正文和图片在时间下面 -->
              <div class="flex flex-col items-start min-w-0 flex-1">
                <div class="flex items-center gap-2 w-full">
                  <span class="font-bold text-sm line-clamp-1 break-all">
                    {{ comment.author.username }}
                  </span>
                  <span class="text-xs text-gray-500 shrink-0">
                    {{ comment.create_time }}
                  </span>
                </div>

                <p
                    v-if="comment.content"
                    class="text-sm whitespace-pre-wrap break-all mt-1 text-left w-full"
                >
                  {{ comment.content }}
                </p>

                <img
                    v-if="comment.image"
                    :src="comment.image"
                    @click="openImagePreview(comment.image)"
                    class="mt-2 rounded-lg max-h-48 max-w-full w-auto block cursor-pointer"
                    alt=""
                >
              </div>
            </div>

            <button
                @click="openCommentModal(post)"
                type="button"
                class="btn btn-sm btn-outline"
            >
              写评论
            </button>
          </div>
        </div>
      </div>
    </div>

    <div ref="sentinel-ref" class="h-2 mt-8"></div>
    <div v-if="isLoading" class="text-gray-500 mt-4">加载中...</div>
    <div v-else-if="!hasPosts && posts.length === 0" class="text-gray-500 mt-4">
      {{ route.query.favorites ? '还没有收藏的动态' : '还没有动态，去发一条吧' }}
    </div>
    <div v-else-if="!hasPosts" class="text-gray-500 mt-4">没有更多了</div>
  </div>

  <!-- 评论弹窗：文字 + 可选图片 -->
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

  <dialog ref="edit-modal-ref" class="modal">
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">编辑动态</h3>

      <textarea
          v-model="editContent"
          rows="4"
          class="textarea w-full"
          placeholder="修改内容..."
      />

      <div class="mt-4">
        <img
            v-if="editImagePreview"
            :src="editImagePreview"
            class="rounded-lg w-full max-h-48 object-contain bg-base-300/30"
            alt=""
        >
        <div class="flex gap-2 mt-2">
          <label class="btn btn-sm btn-outline cursor-pointer">
            换图片
            <input type="file" accept="image/*" class="hidden" @change="onEditImageChange">
          </label>
          <button
              v-if="editImagePreview"
              @click="removeEditImage"
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
        <button @click="submitEdit" type="button" class="btn btn-neutral">保存</button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button>close</button>
    </form>
  </dialog>

  <dialog ref="image-preview-modal-ref" class="modal">
    <div
        class="modal-box max-w-5xl w-full h-[90vh] p-2 bg-transparent shadow-none overflow-hidden flex items-center justify-center"
        @wheel="onPreviewWheel"
    >
      <button
          @click="imagePreviewModalRef.close()"
          type="button"
          class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2 z-10 bg-base-100"
      >
        ✕
      </button>
      <img
          :src="previewImageUrl"
          :style="{ transform: `scale(${previewScale})` }"
          class="max-w-full max-h-[85vh] object-contain rounded-lg transition-transform duration-100 origin-center select-none"
          draggable="false"
          alt=""
      >
    </div>
    <form method="dialog" class="modal-backdrop">
      <button>close</button>
    </form>
  </dialog>
</template>