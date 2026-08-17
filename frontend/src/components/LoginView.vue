<template>
  <div class="login-page">
    <div class="login-bg">
      <!-- Large ship wheel: top-right -->
      <div class="compass compass--large">
        <svg class="compass-svg" viewBox="0 0 800 800" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <radialGradient id="glow-lg" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="var(--color-primary)" stop-opacity="0.30"/>
              <stop offset="50%" stop-color="var(--color-primary)" stop-opacity="0.12"/>
              <stop offset="100%" stop-color="var(--color-primary)" stop-opacity="0"/>
            </radialGradient>
          </defs>

          <circle cx="400" cy="400" r="370" fill="url(#glow-lg)"/>

          <!-- Outer rim -->
          <circle cx="400" cy="400" r="350" stroke="var(--color-primary)" stroke-width="5" opacity="0.45"/>
          <circle cx="400" cy="400" r="338" stroke="var(--color-primary)" stroke-width="2.5" opacity="0.30"/>

          <!-- 8 Spokes -->
          <g stroke="var(--color-primary)" opacity="0.40" stroke-linecap="round">
            <line x1="400" y1="55" x2="400" y2="245" stroke-width="6"/>
            <line x1="608" y1="192" x2="515" y2="285" stroke-width="6"/>
            <line x1="745" y1="400" x2="555" y2="400" stroke-width="6"/>
            <line x1="608" y1="608" x2="515" y2="515" stroke-width="6"/>
            <line x1="400" y1="745" x2="400" y2="555" stroke-width="6"/>
            <line x1="192" y1="608" x2="285" y2="515" stroke-width="6"/>
            <line x1="55" y1="400" x2="245" y2="400" stroke-width="6"/>
            <line x1="192" y1="192" x2="285" y2="285" stroke-width="6"/>
          </g>

          <!-- Handle knobs -->
          <g fill="var(--color-primary)" opacity="0.45">
            <circle cx="400" cy="42" r="14"/>
            <circle cx="608" cy="180" r="14"/>
            <circle cx="758" cy="400" r="14"/>
            <circle cx="608" cy="620" r="14"/>
            <circle cx="400" cy="758" r="14"/>
            <circle cx="180" cy="620" r="14"/>
            <circle cx="42" cy="400" r="14"/>
            <circle cx="180" cy="180" r="14"/>
          </g>

          <!-- Handle inner rings -->
          <g stroke="var(--color-primary)" opacity="0.30" fill="none" stroke-width="2.5">
            <circle cx="400" cy="42" r="9"/>
            <circle cx="608" cy="180" r="9"/>
            <circle cx="758" cy="400" r="9"/>
            <circle cx="608" cy="620" r="9"/>
            <circle cx="400" cy="758" r="9"/>
            <circle cx="180" cy="620" r="9"/>
            <circle cx="42" cy="400" r="9"/>
            <circle cx="180" cy="180" r="9"/>
          </g>

          <!-- Inner hub -->
          <circle cx="400" cy="400" r="110" stroke="var(--color-primary)" stroke-width="4" opacity="0.35"/>
          <circle cx="400" cy="400" r="95" stroke="var(--color-primary)" stroke-width="2" opacity="0.25"/>

          <!-- Hub center -->
          <circle cx="400" cy="400" r="48" stroke="var(--color-primary)" stroke-width="3.5" opacity="0.40" fill="var(--color-primary)" fill-opacity="0.08"/>
          <circle cx="400" cy="400" r="30" stroke="var(--color-primary)" stroke-width="2.5" opacity="0.30"/>

          <!-- Center axle -->
          <circle cx="400" cy="400" r="16" fill="var(--color-primary)" opacity="0.35"/>
          <circle cx="400" cy="400" r="8" fill="var(--color-primary)" opacity="0.55"/>

          <!-- Rivets -->
          <g fill="var(--color-primary)" opacity="0.35">
            <circle cx="400" cy="45" r="4.5"/>
            <circle cx="553" cy="93" r="4.5"/>
            <circle cx="653" cy="193" r="4.5"/>
            <circle cx="703" cy="346" r="4.5"/>
            <circle cx="703" cy="454" r="4.5"/>
            <circle cx="653" cy="607" r="4.5"/>
            <circle cx="553" cy="707" r="4.5"/>
            <circle cx="400" cy="755" r="4.5"/>
            <circle cx="247" cy="707" r="4.5"/>
            <circle cx="147" cy="607" r="4.5"/>
            <circle cx="97" cy="454" r="4.5"/>
            <circle cx="97" cy="346" r="4.5"/>
            <circle cx="147" cy="193" r="4.5"/>
            <circle cx="247" cy="93" r="4.5"/>
            <circle cx="650" cy="150" r="4"/>
            <circle cx="650" cy="650" r="4"/>
            <circle cx="150" cy="650" r="4"/>
            <circle cx="150" cy="150" r="4"/>
          </g>

          <!-- Curved brackets -->
          <g stroke="var(--color-primary)" opacity="0.22" fill="none" stroke-width="2.5">
            <path d="M 400 55 Q 245 150 245 245"/>
            <path d="M 608 192 Q 655 305 550 350"/>
            <path d="M 745 400 Q 650 555 550 555"/>
            <path d="M 608 608 Q 450 655 400 745"/>
            <path d="M 400 745 Q 245 655 245 555"/>
            <path d="M 192 608 Q 145 495 250 450"/>
            <path d="M 55 400 Q 150 245 250 245"/>
            <path d="M 192 192 Q 345 145 400 55"/>
          </g>

          <!-- Dashed circles -->
          <circle cx="400" cy="400" r="310" stroke="var(--color-primary)" stroke-width="1.5" opacity="0.15" stroke-dasharray="5 7" fill="none"/>
          <circle cx="400" cy="400" r="275" stroke="var(--color-primary)" stroke-width="1.2" opacity="0.12" stroke-dasharray="3 9" fill="none"/>

          <!-- Directions -->
          <g opacity="0.40" font-family="system-ui, -apple-system, sans-serif" font-weight="600">
            <text x="400" y="72" text-anchor="middle" font-size="18" fill="var(--color-primary)">N</text>
            <text x="400" y="742" text-anchor="middle" font-size="15" fill="var(--color-primary)">S</text>
            <text x="742" y="406" text-anchor="middle" font-size="15" fill="var(--color-primary)">E</text>
            <text x="58" y="406" text-anchor="middle" font-size="15" fill="var(--color-primary)">W</text>
          </g>

          <!-- Anchor -->
          <g opacity="0.18" stroke="var(--color-primary)" stroke-width="2.5" fill="none" stroke-linecap="round">
            <path d="M 400 390 L 400 410"/>
            <path d="M 393 395 Q 400 390 407 395"/>
            <path d="M 390 405 Q 400 415 410 405"/>
          </g>
        </svg>
      </div>

      <!-- Small ship wheel: bottom-left -->
      <div class="compass compass--small">
        <svg class="compass-svg" viewBox="0 0 800 800" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <radialGradient id="glow-sm" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="var(--color-primary)" stop-opacity="0.28"/>
              <stop offset="50%" stop-color="var(--color-primary)" stop-opacity="0.10"/>
              <stop offset="100%" stop-color="var(--color-primary)" stop-opacity="0"/>
            </radialGradient>
          </defs>

          <circle cx="400" cy="400" r="370" fill="url(#glow-sm)"/>

          <circle cx="400" cy="400" r="350" stroke="var(--color-primary)" stroke-width="4" opacity="0.40"/>
          <circle cx="400" cy="400" r="338" stroke="var(--color-primary)" stroke-width="2" opacity="0.28"/>

          <g stroke="var(--color-primary)" opacity="0.35" stroke-linecap="round">
            <line x1="400" y1="55" x2="400" y2="245" stroke-width="5"/>
            <line x1="608" y1="192" x2="515" y2="285" stroke-width="5"/>
            <line x1="745" y1="400" x2="555" y2="400" stroke-width="5"/>
            <line x1="608" y1="608" x2="515" y2="515" stroke-width="5"/>
            <line x1="400" y1="745" x2="400" y2="555" stroke-width="5"/>
            <line x1="192" y1="608" x2="285" y2="515" stroke-width="5"/>
            <line x1="55" y1="400" x2="245" y2="400" stroke-width="5"/>
            <line x1="192" y1="192" x2="285" y2="285" stroke-width="5"/>
          </g>

          <g fill="var(--color-primary)" opacity="0.40">
            <circle cx="400" cy="42" r="12"/>
            <circle cx="608" cy="180" r="12"/>
            <circle cx="758" cy="400" r="12"/>
            <circle cx="608" cy="620" r="12"/>
            <circle cx="400" cy="758" r="12"/>
            <circle cx="180" cy="620" r="12"/>
            <circle cx="42" cy="400" r="12"/>
            <circle cx="180" cy="180" r="12"/>
          </g>

          <g stroke="var(--color-primary)" opacity="0.25" fill="none" stroke-width="2">
            <circle cx="400" cy="42" r="8"/>
            <circle cx="608" cy="180" r="8"/>
            <circle cx="758" cy="400" r="8"/>
            <circle cx="608" cy="620" r="8"/>
            <circle cx="400" cy="758" r="8"/>
            <circle cx="180" cy="620" r="8"/>
            <circle cx="42" cy="400" r="8"/>
            <circle cx="180" cy="180" r="8"/>
          </g>

          <circle cx="400" cy="400" r="110" stroke="var(--color-primary)" stroke-width="3.5" opacity="0.30"/>
          <circle cx="400" cy="400" r="95" stroke="var(--color-primary)" stroke-width="1.8" opacity="0.22"/>

          <circle cx="400" cy="400" r="48" stroke="var(--color-primary)" stroke-width="3" opacity="0.35" fill="var(--color-primary)" fill-opacity="0.06"/>
          <circle cx="400" cy="400" r="30" stroke="var(--color-primary)" stroke-width="2" opacity="0.25"/>

          <circle cx="400" cy="400" r="16" fill="var(--color-primary)" opacity="0.30"/>
          <circle cx="400" cy="400" r="8" fill="var(--color-primary)" opacity="0.50"/>

          <g fill="var(--color-primary)" opacity="0.30">
            <circle cx="400" cy="45" r="4"/>
            <circle cx="553" cy="93" r="4"/>
            <circle cx="653" cy="193" r="4"/>
            <circle cx="703" cy="346" r="4"/>
            <circle cx="703" cy="454" r="4"/>
            <circle cx="653" cy="607" r="4"/>
            <circle cx="553" cy="707" r="4"/>
            <circle cx="400" cy="755" r="4"/>
            <circle cx="247" cy="707" r="4"/>
            <circle cx="147" cy="607" r="4"/>
            <circle cx="97" cy="454" r="4"/>
            <circle cx="97" cy="346" r="4"/>
            <circle cx="147" cy="193" r="4"/>
            <circle cx="247" cy="93" r="4"/>
            <circle cx="650" cy="150" r="3.5"/>
            <circle cx="650" cy="650" r="3.5"/>
            <circle cx="150" cy="650" r="3.5"/>
            <circle cx="150" cy="150" r="3.5"/>
          </g>

          <g stroke="var(--color-primary)" opacity="0.18" fill="none" stroke-width="2">
            <path d="M 400 55 Q 245 150 245 245"/>
            <path d="M 608 192 Q 655 305 550 350"/>
            <path d="M 745 400 Q 650 555 550 555"/>
            <path d="M 608 608 Q 450 655 400 745"/>
            <path d="M 400 745 Q 245 655 245 555"/>
            <path d="M 192 608 Q 145 495 250 450"/>
            <path d="M 55 400 Q 150 245 250 245"/>
            <path d="M 192 192 Q 345 145 400 55"/>
          </g>

          <circle cx="400" cy="400" r="310" stroke="var(--color-primary)" stroke-width="1.2" opacity="0.12" stroke-dasharray="5 7" fill="none"/>
          <circle cx="400" cy="400" r="275" stroke="var(--color-primary)" stroke-width="1" opacity="0.10" stroke-dasharray="3 9" fill="none"/>

          <g opacity="0.35" font-family="system-ui, -apple-system, sans-serif" font-weight="600">
            <text x="400" y="72" text-anchor="middle" font-size="16" fill="var(--color-primary)">N</text>
            <text x="400" y="742" text-anchor="middle" font-size="13" fill="var(--color-primary)">S</text>
            <text x="742" y="406" text-anchor="middle" font-size="13" fill="var(--color-primary)">E</text>
            <text x="58" y="406" text-anchor="middle" font-size="13" fill="var(--color-primary)">W</text>
          </g>

          <g opacity="0.15" stroke="var(--color-primary)" stroke-width="2" fill="none" stroke-linecap="round">
            <path d="M 400 390 L 400 410"/>
            <path d="M 393 395 Q 400 390 407 395"/>
            <path d="M 390 405 Q 400 415 410 405"/>
          </g>
        </svg>
      </div>
    </div>

    <div class="login-card" :class="{ shake: showError }">
      <div class="login-header">
        <div class="logo">
          <LogoIcon :size="72" class="logo-img" />
        </div>
        <h1 class="title">Weave Talk</h1>
      </div>

      <form @submit.prevent="isRegisterMode ? handleRegister() : handleLogin()" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="username"
            type="text"
            :placeholder="isRegisterMode ? '请设置用户名（2-50个字符）' : '请输入用户名'"
            autocomplete="username"
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <div class="password-wrapper">
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              :placeholder="isRegisterMode ? '请设置密码（至少6位）' : '请输入密码'"
              :autocomplete="isRegisterMode ? 'new-password' : 'current-password'"
              :disabled="loading"
            />
            <button type="button" class="eye-btn" @click="showPassword = !showPassword" tabindex="-1">
              <svg class="eye-icon" :class="{ hidden: showPassword }" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg class="eye-off-icon" :class="{ hidden: !showPassword }" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="isRegisterMode" class="form-group">
          <label for="confirmPassword">确认密码</label>
          <div class="password-wrapper">
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="请再次输入密码"
              autocomplete="new-password"
              :disabled="loading"
            />
            <button type="button" class="eye-btn" @click="showConfirmPassword = !showConfirmPassword" tabindex="-1">
              <svg class="eye-icon" :class="{ hidden: showConfirmPassword }" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg class="eye-off-icon" :class="{ hidden: !showConfirmPassword }" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <div v-if="expiredMessage" class="expired-message">
          {{ expiredMessage }}
        </div>

        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>

        <button type="submit" class="login-btn" :disabled="loading">
          <span v-if="!loading">{{ isRegisterMode ? '注 册' : '登 录' }}</span>
          <span v-else class="loading-spinner"></span>
        </button>
      </form>

      <div class="login-footer">
        <button class="switch-mode-btn" @click="toggleMode" :disabled="loading">
          {{ isRegisterMode ? '已有账号？返回登录' : '没有账号？注册新用户' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import api from '@/api/client'
import LogoIcon from './LogoIcon.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuth()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const errorMessage = ref('')
const expiredMessage = ref('')
const successMessage = ref('')
const showError = ref(false)
const isRegisterMode = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

onMounted(() => {
  if (route.query.expired === '1') {
    expiredMessage.value = '登录已过期，请重新登录'
  }
})

function toggleMode() {
  isRegisterMode.value = !isRegisterMode.value
  errorMessage.value = ''
  successMessage.value = ''
  confirmPassword.value = ''
  showPassword.value = false
  showConfirmPassword.value = false
}

async function handleLogin() {
  if (!username.value || !password.value) {
    errorMessage.value = '请输入用户名和密码'
    triggerShake()
    return
  }

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await auth.login(username.value, password.value)
    const redirect = route.query.redirect as string || '/'
    router.push(redirect)
  } catch (e: any) {
    errorMessage.value = e.response?.data?.detail || '登录失败，请检查用户名和密码'
    triggerShake()
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!username.value || !password.value || !confirmPassword.value) {
    errorMessage.value = '请填写所有字段'
    triggerShake()
    return
  }

  if (password.value !== confirmPassword.value) {
    errorMessage.value = '两次输入的密码不一致'
    triggerShake()
    return
  }

  if (password.value.length < 6) {
    errorMessage.value = '密码长度不能少于6个字符'
    triggerShake()
    return
  }

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await api.post('/auth/register', { username: username.value, password: password.value })
    successMessage.value = '注册成功，请登录'
    isRegisterMode.value = false
    confirmPassword.value = ''
    showPassword.value = false
    showConfirmPassword.value = false
  } catch (e: any) {
    errorMessage.value = e.response?.data?.detail || '注册失败，请稍后重试'
    triggerShake()
  } finally {
    loading.value = false
  }
}

function triggerShake() {
  showError.value = true
  setTimeout(() => {
    showError.value = false
  }, 500)
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-bg) 0%, var(--color-sidebar) 100%);
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.compass {
  position: absolute;
  pointer-events: none;
}

.compass--large {
  top: -8vmin;
  right: -8vmin;
  width: 85vmin;
  height: 85vmin;
  max-width: 700px;
  max-height: 700px;
  animation: wheel-rotate 240s linear infinite;
}

.compass--large .compass-svg {
  animation: breathe 5s ease-in-out infinite;
}

.compass--small {
  bottom: -6vmin;
  left: -6vmin;
  width: 55vmin;
  height: 55vmin;
  max-width: 450px;
  max-height: 450px;
  animation: wheel-rotate 160s linear infinite reverse;
}

.compass--small .compass-svg {
  animation: breathe 7s ease-in-out infinite 2s;
}

.compass-svg {
  width: 100%;
  height: 100%;
}

@keyframes wheel-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes breathe {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.035); opacity: 0.78; }
}

.login-card {
  width: 380px;
  background: var(--color-white);
  border-radius: 24px;
  padding: 40px 36px;
  box-shadow: var(--shadow-lg);
  position: relative;
  z-index: 1;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
}

.login-card.shake {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-8px); }
  40%, 80% { transform: translateX(8px); }
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  background: transparent;
  border-radius: 16px;
  margin-bottom: 16px;
}

.logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 16px;
}

.title {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 4px 0;
  text-wrap: balance;
}

.subtitle {
  font-size: 14px;
  color: var(--color-text-light);
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text);
}

.form-group input {
  padding: 14px 16px;
  border: 2px solid var(--color-border);
  border-radius: 12px;
  font-size: 14px;
  color: var(--color-text);
  background: var(--color-sidebar);
  transition: border-color 0.2s ease, background-color 0.2s ease, box-shadow 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-primary);
  background: var(--color-white);
  box-shadow: 0 0 0 4px rgba(122, 163, 90, 0.10);
}

.form-group input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: var(--color-error);
  font-size: 13px;
  text-align: center;
  padding: 10px;
  background: rgba(216, 92, 92, 0.08);
  border-radius: 8px;
}

.expired-message {
  color: var(--color-warning, #d97706);
  font-size: 13px;
  text-align: center;
  padding: 10px;
  background: rgba(217, 119, 6, 0.08);
  border-radius: 8px;
}

.login-btn {
  padding: 14px 24px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  font-size: 15px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(90, 130, 60, 0.25);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.96);
  box-shadow: 0 4px 12px rgba(90, 130, 60, 0.18);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-footer {
  margin-top: 24px;
  text-align: center;
}

.switch-mode-btn {
  background: none;
  border: none;
  color: var(--color-primary);
  font-size: 13px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.switch-mode-btn:hover:not(:disabled) {
  background: rgba(122, 163, 90, 0.08);
}

.switch-mode-btn:active:not(:disabled) {
  transform: scale(0.96);
}

.switch-mode-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-wrapper input::-ms-reveal,
.password-wrapper input::-ms-clear {
  display: none;
}

.password-wrapper input {
  width: 100%;
  padding-right: 44px;
}

.eye-btn {
  position: absolute;
  right: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: none;
  border: none;
  border-radius: 6px;
  color: var(--color-text-light);
  cursor: pointer;
  transition: color 0.2s ease, background-color 0.2s ease, transform 0.2s ease;
}

.eye-btn:hover {
  color: var(--color-text);
  background: rgba(122, 163, 90, 0.06);
}

.eye-btn:active {
  transform: scale(0.96);
}

.eye-btn .eye-icon,
.eye-btn .eye-off-icon {
  position: absolute;
  inset: 0;
  margin: auto;
  transition: opacity 0.2s cubic-bezier(0.2, 0, 0, 1), transform 0.2s cubic-bezier(0.2, 0, 0, 1), filter 0.2s cubic-bezier(0.2, 0, 0, 1);
}

.eye-btn .eye-icon.hidden,
.eye-btn .eye-off-icon.hidden {
  opacity: 0;
  transform: scale(0.25);
  filter: blur(4px);
  pointer-events: none;
}

.success-message {
  color: var(--color-success, #38a169);
  font-size: 13px;
  text-align: center;
  padding: 10px;
  background: rgba(90, 138, 58, 0.08);
  border-radius: 8px;
}

@media (max-width: 480px) {
  .login-page {
    padding: 20px;
  }

  .login-card {
    width: 100%;
    padding: 28px 24px;
    border-radius: 20px;
  }

  .logo {
    width: 56px;
    height: 56px;
  }

  .logo svg {
    width: 32px;
    height: 32px;
  }

  .title {
    font-size: 24px;
  }

  .compass--large {
    top: -6vmin;
    right: -6vmin;
    width: 75vmin;
    height: 75vmin;
  }

  .compass--small {
    bottom: -5vmin;
    left: -5vmin;
    width: 50vmin;
    height: 50vmin;
  }
}

@media (prefers-reduced-motion: reduce) {
  .compass--large,
  .compass--large .compass-svg,
  .compass--small,
  .compass--small .compass-svg {
    animation: none;
  }

  .login-card.shake {
    animation: none;
  }
}
</style>
