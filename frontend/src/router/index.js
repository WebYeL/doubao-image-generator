import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/ImageGenerator.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/ImageHistory.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
