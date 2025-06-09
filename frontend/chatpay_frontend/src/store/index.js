// src/store/index.js
import { defineStore } from 'pinia'
import { api } from 'boot/axios' // our shared Axios instance

export const useUserStore = defineStore('user', {
  state: () => ({
    token: null,
    profile: null
  }),
  actions: {
    async login(username, password) {
      const { data } = await api.post('auth/login/', { username, password })
      this.token = data.token
      api.defaults.headers.common['Authorization'] = `Bearer ${data.token}`
      const res = await api.get('users/me/')
      this.profile = res.data
    },
    async register({ username, email, password }) {
      // Calls your backend’s registration endpoint
      await api.post('auth/register/', { username, email, password })
      // You can choose to automatically log them in, or return here
    }
  }
})
