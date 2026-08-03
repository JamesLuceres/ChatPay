// src/main.js
import { createApp } from 'vue'
import { Quasar, Dark } from 'quasar'
import App from './App.vue'
import router from './router'

// Import Quasar css
import '@quasar/extras/material-icons/material-icons.css'
import 'quasar/src/css/index.sass'

// Import dark mode service
import darkModeService from './services/dark-mode-service.js'

const app = createApp(App)

app.use(Quasar, {
  plugins: {
    Dark
  }
})

app.use(router)

// Initialize dark mode service
darkModeService

app.mount('#q-app')
