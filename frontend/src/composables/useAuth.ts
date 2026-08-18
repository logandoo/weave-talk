import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/client'
// weave-talk 无 assistant/chat/notes store（语音域裁剪），不再引用任何 store。

const TOKEN_KEY = 'chatllm_token'
const USER_KEY = 'chatllm_user'

interface User {
  id: string
  username: string
  created_at: string
  agent_permissions?: Record<string, boolean>
}

const DEFAULT_PERMISSIONS: Record<string, boolean> = {
  terminal_execution: true,
  note_create: true,
  note_edit: true,
  note_delete: true,
  notebook_create: true,
  notebook_edit: true,
  notebook_delete: true,
}

function normalizeUser(data: any): User {
  return {
    id: data.id,
    username: data.username,
    created_at: data.created_at,
    agent_permissions: { ...DEFAULT_PERMISSIONS, ...(data.agent_permissions || {}) },
  }
}

const user = ref<User | null>(null)
const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))

if (typeof window !== 'undefined') {
  window.addEventListener('storage', (e) => {
    if (e.key === TOKEN_KEY) {
      if (e.newValue) {
        token.value = e.newValue
      } else {
        clearStoredAuth()
      }
    }
    if (e.key === USER_KEY) {
      if (e.newValue) {
        try {
          user.value = normalizeUser(JSON.parse(e.newValue))
        } catch {
          user.value = null
        }
      } else {
        user.value = null
      }
    }
  })
}

export function clearStoredAuth() {
  token.value = null
  user.value = null
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function useAuth() {
  const router = useRouter()
  const isAuthenticated = computed(() => !!token.value)

  function setAuth(newToken: string, newUser: any) {
    const normalized = normalizeUser(newUser)
    token.value = newToken
    user.value = normalized
    localStorage.setItem(TOKEN_KEY, newToken)
    localStorage.setItem(USER_KEY, JSON.stringify(normalized))
  }

  function clearAuth() {
    clearStoredAuth()
  }

  function initAuth() {
    const storedToken = localStorage.getItem(TOKEN_KEY)
    const storedUser = localStorage.getItem(USER_KEY)
    if (storedToken && storedUser) {
      token.value = storedToken
      try {
        user.value = normalizeUser(JSON.parse(storedUser))
      } catch {
        clearStoredAuth()
      }
    }
  }

  async function login(username: string, password: string) {
    const response = await api.post('/auth/login', { username, password })
    const { access_token, user: userData } = response.data
    setAuth(access_token, userData)
    return userData
  }

  async function logout() {
    try {
      await api.post('/auth/logout')
    } catch (e) {
      // ignore logout errors
    }
    clearAuth()
    // Clear any session/local storage drafts
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith('chatllm_') && key !== TOKEN_KEY && key !== USER_KEY) {
        localStorage.removeItem(key)
      }
    })
    Object.keys(sessionStorage).forEach(key => {
      if (key.startsWith('chatllm_')) {
        sessionStorage.removeItem(key)
      }
    })
    router.push('/login')
  }

  async function checkAuth() {
    if (!token.value) return false
    try {
      const response = await api.get('/auth/me')
      user.value = normalizeUser(response.data)
      return true
    } catch (e) {
      clearAuth()
      return false
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    setAuth,
    clearAuth,
    initAuth,
    login,
    logout,
    checkAuth,
  }
}
