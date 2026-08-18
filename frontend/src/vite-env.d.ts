/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 先 import 再 declare 才是 module augmentation；直接 declare module 会
// 遮蔽 vue-router 的全部导出（useRoute/useRouter 等均不可见 → TS2305）。
import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    layout?: string
  }
}
