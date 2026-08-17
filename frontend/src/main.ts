import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/main.css'

const app = createApp(App)
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue error:', err, info, vm)
}
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
})
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error)
})
app.use(createPinia())
app.use(router)
app.mount('#app')
