import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

// weave-talk 只保留语音域：/login → 登录页，/voice → 语音对话，/ 重定向 /voice。
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/components/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/voice',
    name: 'Voice',
    component: () => import('@/components/VoiceChat.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    redirect: '/voice'
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/voice'
  }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes
})

router.beforeEach(async (to, _from, next) => {
  const auth = useAuth()
  auth.initAuth()

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)

  if (requiresAuth && !auth.isAuthenticated.value) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && auth.isAuthenticated.value) {
    next({ name: 'Voice' })
  } else {
    next()
  }
})

export default router
