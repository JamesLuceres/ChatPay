// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// (We won’t mount any Quasar layout for now—just mount Vue + router)
createApp(App).use(router).mount('#q-app')
