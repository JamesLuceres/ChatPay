<!-- src/pages/RegisterPage.vue -->
<template>
  <div class="register-page">
    <!-- Logo container -->
    <div class="logo-container">
      <img src="~assets/logo/chatpay-logo.png" alt="ChatPay Logo" class="chatpay-logo" />
    </div>

    <!-- White card -->
    <div class="register-card q-pa-lg">
      <!-- Header -->
      <div class="register-header column items-center justify-center q-mb-xl">
        <div class="text-h5 text-center q-mt-sm">Create an account</div>
        <div class="text-subtitle2 text-center">Sign up to get started</div>
      </div>

      <q-form @submit.prevent="onSubmit" ref="formRef" class="q-gutter-md">
        <!-- Username Field -->
        <q-input
          filled
          v-model="username"
          type="text"
          label="Username"
          rounded
          dense
          class="input-pill"
          lazy-rules
          :rules="[
            (val) => !!val || 'Username is required',
            (val) => val.length >= 3 || 'Minimum 3 characters',
          ]"
        >
          <template v-slot:prepend>
            <q-icon name="account_circle" />
          </template>
        </q-input>
        <!-- Backend username errors -->
        <div v-if="errors.username" class="text-negative text-caption q-mt-xs">
          {{ errors.username }}
        </div>

        <!-- Email Field -->
        <q-input
          filled
          v-model="email"
          type="email"
          label="Email"
          rounded
          dense
          class="input-pill"
          lazy-rules
          :rules="[
            (val) => !!val || 'Email is required',
            (val) => /.+@.+\..+/.test(val) || 'Enter a valid email',
          ]"
        >
          <template v-slot:prepend>
            <q-icon name="email" />
          </template>
        </q-input>
        <!-- Backend email errors -->
        <div v-if="errors.email" class="text-negative text-caption q-mt-xs">
          {{ errors.email }}
        </div>

        <!-- Password Field -->
        <q-input
          filled
          v-model="password"
          :type="showPassword ? 'text' : 'password'"
          label="Password"
          rounded
          dense
          class="input-pill"
          lazy-rules
          :rules="[
            (val) => !!val || 'Password is required',
            (val) => val.length >= 6 || 'Minimum 6 characters',
          ]"
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
        <!-- Backend password errors -->
        <div v-if="errors.password" class="text-negative text-caption q-mt-xs">
          {{ errors.password }}
        </div>

        <!-- Confirm Password Field -->
        <q-input
          filled
          v-model="confirmPassword"
          :type="showPassword ? 'text' : 'password'"
          label="Confirm Password"
          rounded
          dense
          class="input-pill"
          lazy-rules
          :rules="[
            (val) => !!val || 'Confirmation is required',
            (val) => val === password || 'Passwords do not match',
          ]"
        >
          <template v-slot:prepend>
            <q-icon name="lock_open" />
          </template>
          <template v-slot:after>
            <q-icon
              :name="showPassword ? 'visibility_off' : 'visibility'"
              class="cursor-pointer"
              @click.stop="toggleShowPassword"
            />
          </template>
        </q-input>
        <!-- Backend confirm_password errors -->
        <div v-if="errors.confirm_password" class="text-negative text-caption q-mt-xs">
          {{ errors.confirm_password }}
        </div>

        <!-- General (non-field) error from server -->
        <div v-if="errors.general" class="text-negative text-caption q-mt-xs">
          {{ errors.general }}
        </div>

        <!-- Register Button -->
        <div class="sign-in row justify-center">
          <q-btn
            label="Register"
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

      <!-- “or sign in with” -->
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

      <!-- “Already have an account?” -->
      <div class="text-center q-mt-lg">
        <span class="text-body2">
          Already have an account?
          <a @click="goToLogin" class="signup-link">Sign in</a>
        </span>
      </div>
    </div>

    <!-- Bottom “Powered by” + Paytaca logo -->
    <div class="powered-container">
      <span class="text-body2">Powered by:</span>
      <img src="~assets/logo/paytaca-logo.png" alt="Paytaca Logo" class="paytaca-logo" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

// IMPORT the Notify plugin directly:
import { Notify } from 'quasar'

const router = useRouter()

// Form fields
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

// Show/hide password toggle
const showPassword = ref(false)
function toggleShowPassword() {
  showPassword.value = !showPassword.value
}

// Loading + error state
const loading = ref(false)
const errors = ref({
  username: '',
  email: '',
  password: '',
  confirm_password: '',
  general: '',
})

// Reference to Quasar’s <q-form> for client‐side validation
const formRef = ref(null)

async function onSubmit() {
  // 1) Run built‐in Quasar validation
  const valid = await formRef.value.validate()
  if (!valid) {
    return
  }

  // 2) Clear any existing errors before sending:
  Object.assign(errors.value, {
    username: '',
    email: '',
    password: '',
    confirm_password: '',
    general: '',
  })
  loading.value = true

  try {
    const response = await axios.post('/api/register/', {
      username: username.value,
      email: email.value,
      password: password.value,
      confirm_password: confirmPassword.value,
    })

    console.log('✅ onSubmit(): 201 received, success!', response)

    // 3) Clear errors again just to be safe:
    Object.assign(errors.value, {
      username: '',
      email: '',
      password: '',
      confirm_password: '',
      general: '',
    })

    // 4) Show a Quasar toast using Notify.create(...)
    Notify.create({
      type: 'positive',
      message: 'Registration successful! Please log in.',
    })

    // 5) Redirect to /login
    await router.push('/login')
  } catch (err) {
    console.error('❌ Registration error:', err)
    loading.value = false

    if (err.response && err.response.data) {
      const data = err.response.data

      // Field‐level errors:
      errors.value.username = data.username ? data.username.join(' ') : ''
      errors.value.email = data.email ? data.email.join(' ') : ''
      errors.value.password = data.password ? data.password.join(' ') : ''
      errors.value.confirm_password = data.confirm_password ? data.confirm_password.join(' ') : ''

      // Non‐field (general) errors:
      if (data.detail) {
        errors.value.general = data.detail
      } else if (data.non_field_errors) {
        errors.value.general = data.non_field_errors.join(' ')
      } else if (!data.username && !data.email && !data.password && !data.confirm_password) {
        errors.value.general = 'Registration failed. Please try again.'
      }
    } else {
      // Network or unexpected error
      errors.value.general = 'Registration failed. Please try again.'
    }
  }
}

function goToLogin() {
  router.push('/login')
}

function onSocialClick(provider) {
  console.log(`Register with ${provider} clicked`)
}
</script>
<style scoped>
.register-page {
  background: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
}

/* Logo container above card */
.logo-container {
  position: relative;
  z-index: 1;
  margin-bottom: -40px; /* pull up over the card */
}

.chatpay-logo {
  width: 250px;
  height: 250px;
  object-fit: contain;
  padding: 10px;
  margin-bottom: 15%;
  mix-blend-mode: multiply;
}

/* White card */
.register-card {
  background-color: white;
  border-radius: 12px;
  max-width: 360px;
  width: 100%;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.5);
  padding-top: 40px; /* so header text sits below the logo */
}

/* Center header text */
.register-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}

/* Pill-style inputs */
.input-pill {
  background-color: #e3f2fd;
}

/* Button style */
.sign-in-btn {
  width: 100%;
  font-weight: 500;
}

/* Social button styling */
.social-btn {
  background-color: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
  color: #555;
}
.social-btn:hover {
  background-color: #f0f0f0;
}

/* paytaca logo */
.powered-container {
  display: flex;
  align-items: center;
  gap: 0.2em; /* small gap */
  margin-top: 1rem;
}
.paytaca-logo {
  width: auto;
  height: 3em;
  object-fit: contain;
  mix-blend-mode: multiply;
}

/* “Sign in” link styling */
.signup-link {
  color: #1976d2;
  cursor: pointer;
  font-weight: 500;
}
.signup-link:hover {
  text-decoration: underline;
}
</style>
