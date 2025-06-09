// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', component: () => import('pages/LoginPage.vue') },
  { path: '/register', component: () => import('pages/RegisterPage.vue') },
  {
    path: '/home',
    component: () => import('pages/HomePage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/rooms/create',
    component: () => import('pages/CreateRoom.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/rooms/:id',
    component: () => import('pages/RoomPage.vue'),
    meta: { requiresAuth: true }
  },
  { path: '/:catchAll(.*)*', component: () => import('pages/PageNotFound.vue') }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    // Notice we check for 'chatpay_access_token' (same key LoginPage.vue used)
    const token = localStorage.getItem('chatpay_access_token')
    if (!token) {
      return next('/login')
    }
  }
  next()
})

export default router
