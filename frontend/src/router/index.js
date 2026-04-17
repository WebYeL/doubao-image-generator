import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/ImageGenerator.vue')
  },
  {
    path: '/video',
    name: 'VideoGenerator',
    component: () => import('@/views/VideoGenerator.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/ImageHistory.vue')
  },
  {
    path: '/video-history',
    name: 'VideoHistory',
    component: () => import('@/views/VideoHistory.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
