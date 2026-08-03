// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/login', component: () => import('pages/LoginPage.vue') },
  { path: '/register', component: () => import('pages/RegisterPage.vue') },
  {
    path: '/home',
    component: () => import('pages/HomePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/rooms/:id',
    component: () => import('pages/RoomPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    component: () => import('pages/ProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    component: () => import('pages/SettingsPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/deposit',
    component: () => import('pages/DepositPage.vue'),
    meta: { requiresAuth: true },
  },
  { path: '/:catchAll(.*)*', component: () => import('pages/PageNotFound.vue') },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    // Notice we check for 'access' (same key LoginPage.vue used)
    const token = localStorage.getItem('access')
    if (!token) {
      return next('/login')
    }
  }
  next()
})

export default router
