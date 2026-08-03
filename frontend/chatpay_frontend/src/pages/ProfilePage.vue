<template>
  <div class="profile-page-wrapper">
    <!-- Header -->
    <div class="profile-header row items-center q-px-md">
      <q-btn flat round icon="arrow_back" @click="goBack" />
      <span class="text-h6 q-ml-sm">Profile</span>
    </div>

    <!-- Profile Content -->
    <q-scroll-area class="profile-content">
      <!-- Avatar Section -->
      <div class="profile-avatar-section column items-center q-pa-md">
        <div class="relative-position">
          <q-avatar size="120px" class="profile-avatar">
            <img :src="profile.avatar_url || defaultAvatar" alt="Avatar" />
          </q-avatar>
          <q-btn
            round
            dense
            icon="mdi-camera-plus"
            color="primary"
            class="avatar-edit-btn"
            @click="triggerFileInput"
          />
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            class="hidden"
            @change="onAvatarSelected"
          />
        </div>
      </div>

      <!-- Profile Form -->
      <q-form @submit.prevent="saveProfile" class="q-px-md q-gutter-md">
        <div class="q-mt-md">
          <div class="text-caption text-grey-7">Username</div>
          <div
            class="text-body2 bg-grey-2 q-pa-sm q-mt-xs"
            style="border-radius: 4px; word-break: break-all"
          >
            {{ profile.username }}
          </div>
        </div>

        <div class="q-mt-md">
          <div class="text-caption text-grey-7">Email</div>
          <div
            class="text-body2 bg-grey-2 q-pa-sm q-mt-xs"
            style="border-radius: 4px; word-break: break-all"
          >
            {{ profile.email }}
          </div>
        </div>

        <div class="q-mt-md">
          <div class="text-caption text-grey-7">Password</div>
          <div
            class="text-body2 bg-grey-2 q-pa-sm q-mt-xs"
            style="border-radius: 4px; width: 120px"
          >
            ********
          </div>
        </div>

        <div class="row q-mt-lg q-mb-lg">
          <q-btn
            label="Save Changes"
            type="submit"
            color="primary"
            :loading="saving"
            :disable="saving"
            class="full-width"
          />
        </div>
      </q-form>

      <!-- Action Buttons -->
      <div class="action-buttons q-px-md">
        <q-btn
          outline
          label="Change Password"
          color="primary"
          @click="openPasswordDialog"
          class="full-width q-mb-md"
        />

        <q-btn
          flat
          label="Delete Account"
          color="negative"
          @click="confirmDeleteAccount"
          class="full-width"
        />
      </div>
    </q-scroll-area>

    <!-- Change Password Dialog -->
    <q-dialog v-model="passwordDialog">
      <q-card style="width: 320px">
        <q-card-section class="row items-center">
          <div class="text-h6">Change Password</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <q-form @submit.prevent="submitPasswordChange" class="q-gutter-md">
            <q-input
              v-model="passwordForm.current_password"
              label="Current Password"
              type="password"
              outlined
              :rules="[(v) => !!v || 'Required']"
            />
            <q-input
              v-model="passwordForm.new_password"
              label="New Password"
              type="password"
              outlined
              :rules="[(v) => !!v || 'Required']"
            />
            <q-input
              v-model="passwordForm.confirm_password"
              label="Confirm New Password"
              type="password"
              outlined
              :rules="[
                (v) => !!v || 'Required',
                (v) => v === passwordForm.new_password || 'Passwords do not match',
              ]"
            />

            <div class="row justify-end q-mt-md">
              <q-btn flat label="Cancel" v-close-popup />
              <q-btn
                label="Change"
                type="submit"
                color="primary"
                :loading="changingPassword"
                :disable="changingPassword"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Confirm Delete Dialog -->
    <q-dialog v-model="deleteDialog">
      <q-card style="width: 320px">
        <q-card-section class="row items-center">
          <div class="text-h6 text-negative">Delete Account?</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          This action <strong>cannot</strong> be undone. All your data will be permanently deleted.
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            flat
            label="Delete"
            color="negative"
            @click="deleteAccount"
            :loading="deleting"
            :disable="deleting"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Notify } from 'quasar'

const router = useRouter()
const defaultAvatar = '/default-avatar.png'

// Profile state
const profile = ref({
  id: null,
  username: '',
  email: '',
  avatar_url: '',
})
const saving = ref(false)

// Password dialog
const passwordDialog = ref(false)
const changingPassword = ref(false)
const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: '',
})

// Delete dialog
const deleteDialog = ref(false)
const deleting = ref(false)

// File input ref
const fileInput = ref(null)

// Load profile
async function loadProfile() {
  try {
    const token = localStorage.getItem('access')
    const { data } = await axios.get('/api/profile/', {
      headers: { Authorization: `Bearer ${token}` },
    })
    profile.value = { ...data }
  } catch {
    Notify.create({ type: 'negative', message: 'Could not load profile.' })
  }
}

// Save edits
async function saveProfile() {
  saving.value = true
  try {
    const token = localStorage.getItem('access')
    await axios.patch('/api/profile/', {}, { headers: { Authorization: `Bearer ${token}` } })
    Notify.create({ type: 'positive', message: 'Profile updated.' })
  } catch {
    Notify.create({ type: 'negative', message: 'Failed to update profile.' })
  } finally {
    saving.value = false
  }
}

// Change avatar
function triggerFileInput() {
  fileInput.value.click()
}
async function onAvatarSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  const form = new FormData()
  form.append('avatar', file)

  try {
    const token = localStorage.getItem('access')
    const { data } = await axios.post('/api/profile/avatar/', form, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
    })
    profile.value.avatar_url = data.avatar_url
    Notify.create({ type: 'positive', message: 'Avatar updated.' })
  } catch {
    Notify.create({ type: 'negative', message: 'Avatar upload failed.' })
  }
}

// Password change
function openPasswordDialog() {
  passwordForm.value = {
    current_password: '',
    new_password: '',
    confirm_password: '',
  }
  passwordDialog.value = true
}
async function submitPasswordChange() {
  changingPassword.value = true
  try {
    const token = localStorage.getItem('access')
    await axios.post(
      '/api/profile/password/',
      { ...passwordForm.value },
      { headers: { Authorization: `Bearer ${token}` } },
    )
    Notify.create({ type: 'positive', message: 'Password changed.' })
    passwordDialog.value = false
  } catch {
    Notify.create({ type: 'negative', message: 'Password change failed.' })
  } finally {
    changingPassword.value = false
  }
}

// Delete account
function confirmDeleteAccount() {
  deleteDialog.value = true
}
async function deleteAccount() {
  deleting.value = true
  try {
    const token = localStorage.getItem('access')
    await axios.delete('/api/profile/', {
      headers: { Authorization: `Bearer ${token}` },
    })
    Notify.create({ type: 'positive', message: 'Account deleted.' })
    localStorage.removeItem('access')
    router.replace('/login')
  } catch {
    Notify.create({ type: 'negative', message: 'Could not delete account.' })
  } finally {
    deleting.value = false
    deleteDialog.value = false
  }
}

// Navigation
function goBack() {
  router.back()
}

onMounted(loadProfile)
</script>

<style scoped lang="scss">
.profile-page-wrapper {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f8fa;
}

.profile-header {
  flex: 0 0 auto;
  height: 56px;
  background-color: white;
  border-bottom: 1px solid #e0e0e0;
}

.profile-content {
  flex: 1 1 auto;
}

.profile-avatar-section {
  background-color: white;
  margin-bottom: 8px;
  padding-top: 24px;
  padding-bottom: 24px;
}

.profile-avatar {
  border: 3px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.avatar-edit-btn {
  position: absolute;
  bottom: 8px;
  right: 8px;
  transform: translate(50%, 50%);
}

.action-buttons {
  margin-top: 16px;
  margin-bottom: 24px;
}

.q-dialog .q-card {
  border-radius: 12px;
}

.hidden {
  display: none;
}
</style>
