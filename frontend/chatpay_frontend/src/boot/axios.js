// src/boot/axios.js
import { boot } from 'quasar/wrappers'
import axios from 'axios'

export default boot(({ app }) => {
  // Set the base URL for all requests to your Django backend.
  // If your backend and frontend are on different ports during dev,
  // adjust as needed (e.g., process.env.API_URL).
  axios.defaults.baseURL = 'http://127.0.0.1:8000/'

  // Interceptor: attach access token to every request (if present)
  axios.interceptors.request.use(config => {
    const token = localStorage.getItem('chatpay_access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  // Make axios available in all components as this.$axios
  app.config.globalProperties.$axios = axios
})

