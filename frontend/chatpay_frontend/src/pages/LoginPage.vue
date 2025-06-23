<!-- src/pages/LoginPage.vue -->
<template>
  <div class="login-page">
    <div class="logo-container">
      <img src="~assets/logo/chatpay-logo.png" alt="ChatPay Logo" class="chatpay-logo" />
    </div>

    <div class="login-card q-pa-lg">
      <div class="login-header column items-center justify-center q-mb-xl">
        <div class="text-h5 text-center q-mt-sm">Welcome back!</div>
        <div class="text-subtitle2 text-center">Login to your account</div>
      </div>

      <q-form @submit.prevent="onSubmit" ref="formRef" class="q-gutter-md">
        <q-input
          filled
          v-model="username"
          type="text"
          label="Username"
          rounded
          dense
          class="input-pill"
          lazy-rules
          :rules="[(val) => !!val || 'Username is required']"
        >
          <template v-slot:prepend>
            <q-icon name="account_circle" />
          </template>
        </q-input>

        <q-input
          filled
          v-model="password"
          :type="showPassword ? 'text' : 'password'"
          label="Password"
          rounded
          dense
          class="input-pill"
          :rules="[(val) => !!val || 'Password is required']"
        >
          <template v-slot:prepend>
            <q-icon name="lock" />
          </template>
          <template v-slot:after>
            <q-icon
              :name="showPassword ? 'visibility_off' : 'visibility'"
              class="cursor-pointer"
              @click.stop="toggleShowPassword"
            />
          </template>
        </q-input>

        <div v-if="error" class="text-negative text-caption q-mt-xs">
          {{ error }}
        </div>

        <div class="sign-in row justify-center q-mt-lg">
          <q-btn
            label="Sign in"
            color="secondary"
            rounded
            unelevated
            class="sign-in-btn"
            :loading="loading"
            :disable="loading"
            type="submit"
          />
        </div>
      </q-form>

      <div class="text-center q-mt-lg q-mb-sm">
        <span class="text-body2">or sign in with</span>
      </div>
      <div class="row justify-center q-gutter-sm">
        <q-btn
          flat
          round
          dense
          icon="mdi-google"
          class="social-btn"
          @click="onSocialClick('google')"
        />
        <q-btn
          flat
          round
          dense
          icon="mdi-facebook"
          class="social-btn"
          @click="onSocialClick('facebook')"
        />
      </div>

      <div class="text-center q-mt-lg">
        <span class="text-body2">
          Don't have an account?
          <a @click="goToRegister" class="signup-link">Sign up here</a>
        </span>
      </div>
    </div>

    <div class="powered-container q-mt-lg">
      <span class="text-body2">Powered by</span>
      <img src="~assets/logo/paytaca-logo.png" alt="Paytaca Logo" class="paytaca-logo" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { Notify } from 'quasar'

const router = useRouter()

// 1) Reactive form fields
const username = ref('')
const password = ref('')
const showPassword = ref(false)

// 2) Loading + error state
const loading = ref(false)
const error = ref('')

// 3) Reference to the <q-form> (for Quasar's built-in validation)
const formRef = ref(null)

function toggleShowPassword() {
  showPassword.value = !showPassword.value
}

async function onSubmit() {
  try {
    // 4a) Run Quasar's client-side rules
    const isValid = await formRef.value.validate()
    if (!isValid) {
      return
    }

    // 4b) Clear any previous error and start loading
    error.value = ''
    loading.value = true

    try {
      // 4c) POST to Django's login endpoint.
      const resp = await axios.post('http://127.0.0.1:8000/api/login/', {
        username: username.value,
        password: password.value,
      })

      // 4d) On success: store the tokens
      const { access, refresh } = resp.data
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)

      // 4e) Redirect to /home with proper error handling
      try {
        await router.push('/home')

        // 4f) Show a toast after successful navigation
        Notify.create({
          type: 'positive',
          message: `Welcome back, ${username.value}!`,
        })
      } catch (navigationError) {
        console.error('Navigation error:', navigationError)
        // Still show success message even if navigation has issues
        Notify.create({
          type: 'positive',
          message: `Login successful! ${username.value}`,
        })
      }
    } catch (loginError) {
      // 5) Login failed: stop loading and display message
      if (loginError.response) {
        if (loginError.response.status === 401) {
          error.value = 'Invalid username or password.'
        } else if (loginError.response.data && loginError.response.data.detail) {
          error.value = loginError.response.data.detail
        } else {
          error.value = 'Login failed. Please try again.'
        }
      } else {
        error.value = 'Unable to connect. Check your network.'
      }
    }
  } catch (unexpectedError) {
    console.error('Unexpected error in onSubmit:', unexpectedError)
    error.value = 'An unexpected error occurred. Please try again.'
  } finally {
    // Always stop loading
    loading.value = false
  }
}

// 6) Navigation helpers
function goToRegister() {
  router.push('/register')
}
function onSocialClick(provider) {
  console.log(`Sign in with ${provider} clicked`)
}
</script>

<style scoped>
.login-page {
  background: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
}
.logo-container {
  position: relative;
  z-index: 1;
}
.chatpay-logo {
  width: 250px;
  height: 250px;
  object-fit: contain;
  padding: 10px;
  margin-bottom: 20%;
  mix-blend-mode: multiply;
}
.login-card {
  background-color: white;
  border-radius: 12px;
  max-width: 360px;
  width: 100%;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.5);
  padding: 2rem 1rem;
}
.login-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 3rem;
}
.input-pill {
  background-color: #e3f2fd;
}
.sign-in-btn {
  width: 100%;
  font-weight: 500;
}
.social-btn {
  background-color: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
  color: #555;
}
.social-btn:hover {
  background-color: #f0f0f0;
}
.signup-link {
  color: #1976d2;
  cursor: pointer;
  font-weight: 500;
}
.signup-link:hover {
  text-decoration: underline;
}
.powered-container {
  display: flex;
  align-items: center;
  gap: 0.2em;
  margin-top: 1rem;
}
.paytaca-logo {
  height: 3em;
}
</style>
