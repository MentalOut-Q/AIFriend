### 1. 项目结构

![幕截图 2026-01-24 00063](D:\86180\Pictures\Screenshots\屏幕截图 2026-01-24 000633.png)

#### 1.1 目录介绍

#####1.1.1 backend

创建 Django 项目时，命令类似：

``django-admin startproject backend``

| 外层 `backend/`                  | 内层 `backend/`             |
| -------------------------------- | --------------------------- |
| 整个后端项目的根目录             | Django 项目的配置包         |
| 放 `manage.py`、数据库、业务 app | 放 `settings.py` 等全局配置 |

*****

##### 1.1.2 static

放「网站自带的、固定的文件」，不是用户上传的。

典型内容：

- 前端打包后的 JS、CSS（Vue `build` 后的文件）
- 图标、默认图片
- 管理后台用的静态资源

frontend (js, css, 图片)  ──build──→  backend/static/
                                         					↑
                              				打包后放进 static，由 Django 一起提供

开发时前端在 `5173` 单独跑；上线后往往会进 `static`，和 Django 的 `8000` 合在一起。

****

##### 1.1.3 media

放「用户上传、会不断变多」的文件。

在这个项目里典型是：

- 用户头像
- 角色照片
- 角色背景图


****

##### 1.1.4 web

web/

├── html      ← 模板（Django 里一般叫 templates）

├── views     ← 处理请求的逻辑

└── url       ← URL 和 views 的对应关系

### `views` — 干活的

- 接收请求（登录、查角色、聊天等）
- 查数据库、调 AI
- 返回 JSON 或 HTML

 `HomepageIndexView`、`LoginView` 都在这类目录里。

### `url` — 指路牌

- 决定「哪个网址由哪个 view 处理」
- 例如：`/api/homepage/index/` → 首页数据接口

### `html` — 页面壳子

- 主要是 `index.html` 这类模板
- 生产模式下：用户访问任意前端路径，Django often 返回这一页，再由 Vue 在浏览器里渲染具体页面




U2 登录模块

# 第 1 部分：实现路由

## 1.1 创建页面文件（项目结构）

每个 `.vue` 文件 = 一个「页面级」组件，放在 `frontend/src/views/` 下：

views/

├── homepage/HomepageIndex.vue      → 首页 /

├── friend/FriendIndex.vue          → 好友 /friend/

├── create/CreateIndex.vue          → 创作 /create/

├── error/NotFoundIndex.vue         → 404

└── user/

​    ├── account/

​    │   ├── LoginIndex.vue          → 登录

​    │   └── RegisterIndex.vue       → 注册

​    ├── profile/ProfileIndex.vue    → 编辑资料（教程写 profile/，项目实际是 user/profile/）

​    └── space/SpaceIndex.vue        → 个人空间 /user/space/:user_id/

规律：文件夹按功能分，`XxxIndex.vue` 表示某个模块的入口页。

------

## 1.2 添加路由 `router/index.js`

路由 = URL 和页面的对应表。

```javascript
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',                          // URL 路径
      component: HomepageIndex,           // 显示哪个组件
      name: 'homepage-index',             // 路由名（代码里跳转用）
      meta: { needLogin: false },         // 自定义元信息（后面守卫用）
    },
    // ... 其他路由
  ],
})

```

### 几种 `path` 写法

| 写法     | 例子                      | 含义                                   |
| -------- | ------------------------- | -------------------------------------- |
| 普通路径 | `'/'`、`'/friend/'`       | 固定 URL                               |
| 动态参数 | `'/user/space/:user_id/'` | `:user_id` 是变量，如 `/user/space/3/` |
| 兜底 404 | `'/:pathMatch(.*)*'`      | 匹配任意未定义路径                     |

### 动态参数 `:user_id`

```js
{
  path: '/user/space/:user_id/',
  name: 'user-space-index',
}

```



在 `SpaceIndex.vue` 里读取：

```js
const route = useRoute()
route.params.user_id   // URL 是 /user/space/3/ 时，值为 '3'
```

```js
const route = useRoute()

route.params.user_id   // URL 是 /user/space/3/ 时，值为 '3'

```

请求 API 时上：

```js
params: {
  user_id: route.params.user_id,
}
```



### 404 路由为什么要放最后

```js
{
  path: '/:pathMatch(.)',
  component: NotFoundIndex,
}

```

路由从上到下匹配，这条放最后，只有前面都不匹配时才进 404。

### `meta.needLogin`

自定义字段，标记「这个页面要不要登录」：

```js
meta: { needLogin: true }   // 创作、好友、资料
meta: { needLogin: false }  // 首页、登录、注册
```



------

## 1.3 把路由挂到页面上

### `App.vue`：放 `<RouterView />`

<template>

  <NavBar>

​    <RouterView/>

  </NavBar>

</template>

作用：URL 变了，Vue Router 在这里替换对应页面组件。

URL = /           → 渲染 HomepageIndex

URL = /friend/    → 渲染 FriendIndex

URL = /xxx/yyy    → 渲染 NotFoundIndex

### 导航栏：`<RouterLink>`

```js
<RouterLink :to="{name: 'homepage-index'}" active-class="menu-focus">
  首页
</RouterLink>

```

| 属性                        | 作用                                       |
| --------------------------- | ------------------------------------------ |
| `:to="{name: '...'}"`       | 跳转到指定路由（用 name，不用手写 path）   |
| `active-class="menu-focus"` | 当前 URL 匹配时，自动加这个 CSS 类（高亮） |

### `NavBar` 里的 slot

<!-- NavBar.vue -->

<slot></slot>

<!-- App.vue -->

<NavBar>

  <RouterView/>

</NavBar>

`<slot>` = 占位符，App 传进去的内容会显示在 NavBar 里。效果是：导航栏固定，中间内容随路由变。

------

# 第 2 部分：登录、注册前端页面

## 共同模式

Login 和 Register 结构一样：

ref 变量存输入 → 表单 v-model 绑定 → @submit.prevent 提交 → api.post → 成功则存用户信息并跳转

### LoginIndex.vue 核心

```js
async function handleLogin() {
  const res = await api.post('/api/user/account/login/', {
    username: username.value,
    password: password.value,
  })

  if (data.result === 'success') {
    user.setAccessToken(data.access)   // access 放内存
    user.setUserInfo(data)             // 用户信息放 Pinia
    await router.push({ name: 'homepage-index' })
  }
}

```





### RegisterIndex.vue 多一步

```js
else if (password.value.trim() !== passwordConfirmed.value.trim()) {
  errorMessage.value = '两次输入的密码不一致'
}

```

注册成功后逻辑和登录相同：存 token + 用户信息 → 跳首页。

### 模板要点

```js
<form @submit.prevent="handleLogin">
  <input v-model="username" />
  <input v-model="password" type="password" />
  <p v-if="errorMessage">{{ errorMessage }}</p>
  <button>登录</button>
  <RouterLink :to="{name: 'user-account-register-index'}">注册</RouterLink>
</form>
```

- `@submit.prevent`：回车/点按钮提交，不刷新整页
- `v-if="errorMessage"`：有错误才显示红字

------

# 第 3 部分：登录、注册后端

## 3.1 创建 UserProfile 数据库

### 为什么要 UserProfile？

Django 自带 `User` 只有用户名、密码等基础字段。
头像、简介等扩展信息放在 `UserProfile`，和 `User` 一对一关联。

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(default='user/photos/default.png', upload_to=photo_upload_to)
    profile = models.TextField(default='谢谢你的关注', max_length=500)

```



| 字段                                | 含义                                  |
| ----------------------------------- | ------------------------------------- |
| `OneToOneField(User)`               | 一个 User 对应一个 UserProfile        |
| `ImageField`                        | 存图片路径，需要 `pip install Pillow` |
| `default='user/photos/default.png'` | 默认头像                              |

### 迁移命令（每次改 model 都要做）

```python
cd backend
python manage.py makemigrations   # 生成迁移文件
python manage.py migrate            # 同步到 db.sqlite3
```





### admin.py 注册

```python
cd backend
python manage.py makemigrations   # 生成迁移文件
python manage.py migrate            # 同步到 db.sqlite3
```

才能在 Django 管理后台 `/admin/` 看到并编辑 `UserProfile`。

------

## 3.2 实现 views（JWT 双 token）

### 认证方案概览

access_token   → 放前端内存（Pinia），每次请求带 Authorization 头，有效期短（2 小时）

refresh_token  → 放 HttpOnly Cookie，用来换新的 access_token，有效期长（7 天）

### login.py

```python
user = authenticate(username=username, password=password)  # Django 验证密码
refresh = RefreshToken.for_user(user)                       # 生成 JWT

response = Response({
    'result': 'success',
    'access': str(refresh.access_token),   # 返回给前端
    'user_id': user.id,
    'username': user.username,
    'photo': user_profile.photo.url,
    'profile': user_profile.profile,
})

response.set_cookie(                       # refresh 放 Cookie
    key='refresh_token',
    value=str(refresh),
    httponly=True,    # JS 读不到，防 XSS
    samesite='Lax',
    secure=True,
    max_age=86400 * 7,
)

```





### register.py

```python
user = User.objects.create_user(username=username, password=password)
user_profile = UserProfile.objects.create(user=user)  # 同时创建资料
# 后面和 login 一样：发 token + set_cookie
```



### logout.py

```python
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # 必须已登录
    def post(self, request):
        response = Response({'result': 'success'})
        response.delete_cookie('refresh_token')  # 删 Cookie
        return response
```



### refresh_token.py

```python
refresh_token = request.COOKIES.get('refresh_token')  # 从 Cookie 读
refresh = RefreshToken(refresh_token)
return Response({'access': str(refresh.access_token)})  # 只返回新 access
```

失败时返回 401，前端 axios 拦截器靠这个判断要不要刷新。

------

## 3.3 更新 urls.py

```js
path('api/user/account/login/', LoginView.as_view()),
path('api/user/account/register/', RegisterView.as_view()),
path('api/user/account/logout/', LogoutView.as_view()),
path('api/user/account/refresh_token/', RefreshTokenView.as_view()),
path('api/user/account/get_user_info/', GetUserInfoView.as_view()),
```



为什么加 `api/`：和后端 SPA 路由区分，避免冲突。

------

# 第 4 部分：对接前后端

## 4.1 全局状态 `stores/user.js`（Pinia）

```js
export const useUserStore = defineStore('user', () => {

    const accessToken = ref('')
    const hasPulledUserInfo = ref(false)

    // id, username, photo, profile ...
    function isLogin() {
        return !!accessToken.value   // 有 token = 已登录
    }
    function setUserInfo(data) { ... }
    function logout() { ... }      // 清空所有字段
    return { accessToken, isLogin, ... }  // 必须 return，外面才能用
})
```



为什么用 Pinia：登录态要在 NavBar、Login、App 等多处共享，比组件间传 props 简单。

删除 counter.js：示例 store，项目不需要。

------

## 4.2 登录后导航栏

NavBar 根据登录状态显示不同内容：

```js
<RouterLink v-if="user.hasPulledUserInfo && !user.isLogin()" :to="...">登录</RouterLink>
<UserMenu v-else />
```



| 状态           | 显示                        |
| -------------- | --------------------------- |
| 未拉取用户信息 | 暂不显示登录（避免闪一下）  |
| 未登录         | 「登录」按钮                |
| 已登录         | 头像 + 下拉菜单（UserMenu） |

### `closeMenu()` 原理

```js
function closeMenu() {
  const element = document.activeElement
  if (element && element instanceof HTMLElement) element.blur()
}
```



下拉菜单靠「焦点」保持打开；菜单项点击后 `blur()` 去掉焦点，菜单自动关闭。

------

## 4.3 封装 axios `api.js`

### 三层能力

\1. 请求拦截器  →  自动加 Authorization: Bearer <access_token>

\2. 响应拦截器  →  401 时用 refresh_token 换新 access，再重发原请求

\3. withCredentials: true  →  请求带上 Cookie（refresh_token）

### 401 刷新流程

请求 A 返回 401

​    ↓

isRefreshing = true，发 refresh 请求

​    ↓

成功 → user.setAccessToken(新token) → 重发请求 A

失败 → user.logout() → 用户需重新登录

### 为什么要 `refreshSubscribers`？

多个请求同时 401 时，只刷新一次，其他请求排队等新 token，避免重复刷 refresh。

------

## 4.4 对接前后端（三个文件）

| 文件              | 调用的 API                         | 成功后                              |
| ----------------- | ---------------------------------- | ----------------------------------- |
| LoginIndex.vue    | POST `/api/user/account/login/`    | setAccessToken + setUserInfo → 首页 |
| RegisterIndex.vue | POST `/api/user/account/register/` | 同上                                |
| UserMenu.vue      | POST `/api/user/account/logout/`   | user.logout() → 首页                |

前后端 `result` 字段约定一致：`'success'` 表示成功，否则是错误文案。

------

## 4.5 路由守卫

```js
router.beforeEach((to, from) => {
  const user = useUserStore()
  if (to.meta.needLogin && user.hasPulledUserInfo && !user.isLogin()) {
    return { name: 'user-account-login-index' }
  }
  return true
})
```



每次路由跳转前执行：

要去 needLogin 页面 + 已拉过用户信息 + 未登录

​    → 重定向到登录页

否则

​    → 放行 (return true)

为什么要 `hasPulledUserInfo`：刚打开网站时还没请求 `get_user_info`，此时不应立刻踢去登录（Cookie 里可能还有有效 refresh）。

------

## 4.6 首次打开：从云端恢复登录态

### 问题

`access_token` 在内存里，刷新页面就没了。
但 `refresh_token` 在 Cookie 里还在，需要恢复登录。

### 后端 get_user_info.py

```python
class GetUserInfoView(APIView):
    permission_classes = [IsAuthenticated]  # 需要有效 access_token
    def get(self, request):
        user = request.user   # JWT 解析后自动注入
        ...

```



### App.vue onMounted

```js
onMounted(async () => {

  try {
    const res = await api.get('/api/user/account/get_user_info/')
    if (data.result === 'success') {
      user.setUserInfo(data)
    }

  } catch (err) {
    // 401 → api.js 自动尝试 refresh；refresh 也失败 → logout
  } finally {
    user.setHasPulledUserInfo(true)
    if (route.meta.needLogin && !user.isLogin()) {
      await router.replace({ name: 'user-account-login-index' })
    }
  }
})

```



### 时序

打开网站

​    ↓

App onMounted → GET get_user_info（此时可能没 access）

​    ↓

401 → api.js 用 Cookie refresh → 拿到新 access → 重试 get_user_info

​    ↓

成功 → setUserInfo

​    ↓

hasPulledUserInfo = true

​    ↓

若当前页需登录且仍未登录 → router.replace 去登录页

### `push` vs `replace`

| 方法             | 历史记录                             |
| ---------------- | ------------------------------------ |
| `router.push`    | 可后退                               |
| `router.replace` | 替换当前记录，防止用户后退到需登录页 |

------

## 4.7 前端打包到后端 + 兜底路由

### Vite 打包

// vite.config.js

build: {

  outDir: '../backend/static/frontend',

}

`npm run build` 后，Vue 产物进 Django 的 `static/frontend/`。

### Django 兜底路由

path('', index),   # 根路径返回 index.html

re_path(r'^(?!media/|static/|assets/).*$', index),

问题：生产环境只跑 Django，用户直接访问 `/friend/` 或刷新页面，Django 没有这条 API 路由。

解决：除 `media/`、`static/`、`assets/` 外，全部返回 `index.html`，再由 Vue Router 在浏览器里渲染正确页面。

用户访问 /friend/

​    ↓

Django re_path 匹配 → 返回 index.html

​    ↓

浏览器加载 Vue → Router 看到 /friend/ → 渲染 FriendIndex

------

# 全链路：用户登录一次，发生了什么

![幕截图 2026-07-01 22151](D:\86180\Pictures\Screenshots\屏幕截图 2026-07-01 221519.png)

------

# 知识点速查

| 概念                | 一句话                       |
| ------------------- | ---------------------------- |
| Vue Router          | 前端 URL ↔ 页面组件          |
| `RouterView`        | 页面渲染出口                 |
| `RouterLink`        | 不刷新页面的链接             |
| `meta.needLogin`    | 标记要不要登录               |
| `beforeEach`        | 路由跳转前拦截               |
| Pinia               | 全局状态（登录信息）         |
| JWT access          | 短期令牌，放内存，请求头携带 |
| JWT refresh         | 长期令牌，放 HttpOnly Cookie |
| axios 拦截器        | 自动带 token、401 自动刷新   |
| `hasPulledUserInfo` | 避免刷新页面前误判未登录     |
| Django 兜底路由     | 生产环境 SPA 刷新不 404      |

# JWT 验证流程（基于你的 AIFriend 项目）

你的项目用的是 双 Token 方案：

| Token         | 有效期 | 存在哪                 | 用途                             |
| ------------- | ------ | ---------------------- | -------------------------------- |
| access_token  | 2 小时 | 前端 Pinia 内存        | 每次 API 请求证明「我是谁」      |
| refresh_token | 7 天   | 浏览器 HttpOnly Cookie | access 过期后，用来换新的 access |

配置在 `settings.py`：

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```



------

## 一、JWT 是什么

JWT 是一串加过密的字符串，里面大致包含：

{ 用户是谁, 什么时候过期, 签名 }

后端用密钥验证签名，确认 token 没被篡改、没过期，就知道是哪个用户在请求。

和传统 Session 的区别：

- Session：登录后服务器存一份会话，浏览器只带 session id
- JWT：服务器不存 access token，每次请求带上 token，服务器验签即可

------

## 二、两个 Token 为什么要分开？

access_token  →  短命、频繁使用、放内存

refresh_token →  长命、很少使用、放 HttpOnly Cookie

好处：

1. access 被盗，2 小时就失效
2. refresh 放 HttpOnly Cookie，JavaScript 读不到，降低 XSS 风险
3. 用户 7 天内不用重新输密码

------

## 三、流程 1：登录（签发 Token）

![幕截图 2026-07-02 20030](D:\86180\Pictures\Screenshots\屏幕截图 2026-07-02 200307.png)

### 后端做了什么

login.py

```python
    refresh = RefreshToken.for_user(user)  # 生成jwt
    response = Response({
        'result': 'success',
        'access': str(refresh.access_token),
        'user_id': user.id,
        ...
    })

    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        httponly=True,
        ...
    )
```

- access → 放在 JSON 里返回给前端
- refresh → 写进 Cookie，浏览器自动保存

### 前端做了什么

user.setAccessToken(data.access)   // 存 Pinia 内存

user.setUserInfo(data)             // 存用户名、头像等

------

## 四、流程 2：正常 API 请求（带 access 验证）

![幕截图 2026-07-02 20005](D:\86180\Pictures\Screenshots\屏幕截图 2026-07-02 200058.png)

### 前端：请求拦截器自动加 token

api.js

```js
api.interceptors.request.use(config => {
    const user = useUserStore()
    if (user.accessToken) {
        config.headers.Authorization = Bearer ${user.accessToken}
    }
    return config
})
```



每个 `api.get()` / `api.post()` 都会自动带上：

Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

### 后端：谁在做验证？

`settings.py` 配置了：

```
'DEFAULT_AUTHENTICATION_CLASSES': (
    'rest_framework_simplejwt.authentication.JWTAuthentication',
),
```

DRF 会在每个请求进来时：

1. 读 `Authorization` 头里的 Bearer token
2. 验签、看是否过期
3. 成功 → `request.user` = 对应用户
4. 失败 → 返回 401 Unauthorized

需要登录的接口会加：

``permission_classes = [IsAuthenticated]``

例如 `GetUserInfoView`：

get_user_info.py

```python
class GetUserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user   # JWT 验证通过后，这里自动有值
```



------

## 五、流程 3：access 过期 → 自动刷新（核心）

access 2 小时过期后，带旧 token 请求会收到 401。
`api.js` 的响应拦截器会接管：

![幕截图 2026-07-02 19565](D:\86180\Pictures\Screenshots\屏幕截图 2026-07-02 195657.png)

### 关键代码逻辑

api.js

```js
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true   // 防止无限重试
            // 1. 用 Cookie 里的 refresh 换新 access
            axios.post(${BASE_URL}/api/user/account/refresh_token/, ...)
            // 2. 成功 → 更新 Pinia，重发原请求
            user.setAccessToken(res.data.access)
            resolve(api(originalRequest))
            // 3. 失败 → 清空登录态
            user.logout()
        }
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true   // 防止无限重试
            // 1. 用 Cookie 里的 refresh 换新 access
            axios.post(${BASE_URL}/api/user/account/refresh_token/, ...)
            // 2. 成功 → 更新 Pinia，重发原请求
            user.setAccessToken(res.data.access)
            resolve(api(originalRequest))
            // 3. 失败 → 清空登录态
            user.logout()
        }
```



### 后端 refresh 接口

refresh_token.py

```python
	refresh_token = request.COOKIES.get('refresh_token')
	...
	refresh = RefreshToken(refresh_token)
	...
	'access': str(refresh.access_token),
```



- refresh 从 Cookie 读（不是从 JSON body）
- 所以 axios 必须设 `withCredentials: true`，请求才会带 Cookie

### 为什么要 `isRefreshing` + `refreshSubscribers`？

如果同时有 3 个请求都 401：

❌ 错误做法：发 3 次 refresh 请求

✅ 正确做法：只 refresh 1 次，其他 2 个排队等新 access

------

## 六、流程 4：刷新页面（F5）后恢复登录

问题：access 在 Pinia 内存里，刷新页面就没了。
但 refresh 在 Cookie 里还在。

![幕截图 2026-07-02 19540](D:\86180\Pictures\Screenshots\屏幕截图 2026-07-02 195401.png)

`App.vue` 在 `onMounted` 里调 `get_user_info`，配合 `api.js` 的 401 刷新，实现「打开网站自动恢复登录」。

------

## 七、流程 5：退出登录

![幕截图 2026-07-02 19513](D:\86180\Pictures\Screenshots\屏幕截图 2026-07-02 195132.png)

```python
# logout.py
response.delete_cookie('refresh_token')  # 删 Cookie
```



// user.js

```js
function logout() {
    accessToken.value = ''
    // 清空 id, username, photo...
}
```



两边都清：Cookie 里的 refresh + 内存里的 access。

------

## 八、一张总流程图

![幕截图 2026-07-02 19502](D:\86180\Pictures\Screenshots\屏幕截图 2026-07-02 195021.png)

------

## 九、各文件在 JWT 流程里的角色

| 文件               | 角色                            |
| ------------------ | ------------------------------- |
| `settings.py`      | 配置 JWT 认证类、token 有效期   |
| `login.py`         | 签发 access + refresh           |
| `register.py`      | 同 login，注册后直接签发        |
| `refresh_token.py` | 用 refresh 换新 access          |
| `logout.py`        | 删 refresh Cookie               |
| `get_user_info.py` | 需有效 access，返回用户信息     |
| `stores/user.js`   | 存 access、判断 `isLogin()`     |
| `api.js`           | 自动带 token、401 自动刷新      |
| `App.vue`          | 启动时用 get_user_info 恢复登录 |

------

## 十、几个容易混淆的点

### 1. 401 是谁返回的？

| 场景                | 谁返回 401                                      |
| ------------------- | ----------------------------------------------- |
| access 过期/无效    | DRF 的 `JWTAuthentication` 或 `IsAuthenticated` |
| refresh 不存在/过期 | `RefreshTokenView` 主动 `status=401`            |

前端 `api.js` 主要靠 401 判断要不要走刷新逻辑。

### 2. `withCredentials: true` 为什么必须？

跨域时（5173 → 8000），默认不带 Cookie。
设了 `withCredentials: true`，refresh 请求才会把 Cookie 发给后端。

### 3. access 和 refresh 内容一样吗？

不一样。都是 JWT，但：

- access：短效，用来访问 API
- refresh：长效，只能用来换 access，不能直接调业务接口

### 4. `ROTATE_REFRESH_TOKENS: True` 是什么？

每次 refresh 时，旧的 refresh 作废，发新的 refresh（并写入 Cookie）。
stolen refresh 被用过一次后，原来的就失效，更安全。

------

## 十一、一句话总结

> 登录：密码对了 → 发 access（内存）+ refresh（Cookie）。
> 平时：每个请求带 access，后端验签。
> access 过期：api.js 用 Cookie 里的 refresh 换新 access，重发请求。
> refresh 也过期：logout，重新登录。
> 刷新页面：access 没了，但 Cookie 还在 → get_user_info 触发 401 → 自动 refresh → 恢复登录。





U3 编辑资料, 编辑角色模块



U4流式布局

### 1. 前端：哨兵 + IntersectionObserver

以 `HomepageIndex.vue` 为例：

```js
async function loadMore() {
  if (isLoading.value || !hasCharacters.value) return
  isLoading.value = true
  // ...
  const res = await api.get('/api/homepage/index/', {
    params: {
      items_count: characters.value.length,  // 已加载数量 = 偏移量
      search_query: route.query.q || '',
    }
  })
  // ...
  if (newCharacters.length === 0) {
    hasCharacters.value = false   // 没更多了
  } else {
    characters.value.push(...newCharacters)  // 追加到列表
    await nextTick()
    if (checkSentinelVisible()) {
      await loadMore()  // 哨兵仍可见 → 继续加载（首屏不够一屏时）
    }
  }
}
```



挂载时监听页面底部的「哨兵」元素：

```js
onMounted(async () => {
  await loadMore()
  observer = new IntersectionObserver(
    entries => { // 遍历每个监听元素, 实际上这里只有sentinelRef.value
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          loadMore()
        }
      })
    },
    {root: null, rootMargin: '2px', threshold: 0}
  )
    
  // 3. 监听页面底部的哨兵DOM元素 sentinelRef.value
  observer.observe(sentinelRef.value)
})
```

```js
<script setup>
const sentinelRef = useTemplateRef('sentinel-ref')
let observer = null

function checkSentinelVisible() {  // 判断哨兵是否能被看到
  if (!sentinelRef.value) return false

  const rect = sentinelRef.value.getBoundingClientRect()
  return rect.top < window.innerHeight && rect.bottom > 0
}

onMounted(async () => {
  await loadMore()  // 加载新元素

  observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          loadMore()
        }
      })
    },
    {root: null, rootMargin: '2px', threshold: 0}
  )

  //监听哨兵元素， 每次哨兵被看到时，都会触发一次
  observer.observe(sentinelRef.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()  // 解绑监听器
})
</script>

<template>
...
<!-- 设置哨兵 -->
<div ref="sentinel-ref" class="h-2"></div>
...
</template>
```



模板里列表下方放哨兵：

```js
<div ref="sentinel-ref" class="h-2 mt-8"></div>
<div v-if="isLoading" class="text-gray-500 mt-4">加载中...</div>
<div v-else-if="!hasCharacters" class="text-gray-500 mt-4">没有更多角色了</div>
```



​    

![幕截图 2026-07-07 22235](D:\86180\Pictures\Screenshots\屏幕截图 2026-07-07 222355.png)



### 