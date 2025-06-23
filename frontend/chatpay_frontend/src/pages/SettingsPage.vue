<template>
  <div class="settings-page-wrapper">
    <!-- Header -->
    <div class="settings-header row items-center q-px-md">
      <q-btn flat round icon="arrow_back" @click="goBack" />
      <span class="text-h6 q-ml-sm">Settings</span>
    </div>

    <!-- Settings Content -->
    <q-scroll-area class="settings-content">
      <!-- Privacy Section -->
      <div class="settings-section">
        <div class="section-title">Privacy</div>
        <q-item class="settings-item">
          <q-item-section avatar>
            <q-icon name="mdi-account-eye" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Last Seen</q-item-label>
            <q-item-label caption>Who can see your last seen time</q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-select
              v-model="lastSeenPrivacy"
              :options="privacyOptions"
              borderless
              dense
              options-dense
              style="min-width: 120px"
            />
          </q-item-section>
        </q-item>

        <q-item class="settings-item">
          <q-item-section avatar>
            <q-icon name="mdi-account-group" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Profile Photo</q-item-label>
            <q-item-label caption>Who can see your profile photo</q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-select
              v-model="profilePhotoPrivacy"
              :options="privacyOptions"
              borderless
              dense
              options-dense
              style="min-width: 120px"
            />
          </q-item-section>
        </q-item>
      </div>

      <!-- Notifications Section -->
      <div class="settings-section">
        <div class="section-title">Notifications</div>
        <q-item class="settings-item">
          <q-item-section avatar>
            <q-icon name="mdi-bell" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Enable Notifications</q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-toggle
              v-model="notificationsEnabled"
              color="primary"
              @update:model-value="onNotificationsToggle"
            />
          </q-item-section>
        </q-item>

        <q-item class="settings-item" v-if="notificationsEnabled">
          <q-item-section avatar>
            <q-icon name="mdi-bell-ring" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Notification Sound</q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-select
              v-model="notificationSound"
              :options="soundOptions"
              borderless
              dense
              options-dense
              style="min-width: 120px"
            />
          </q-item-section>
        </q-item>
      </div>

      <!-- Appearance Section -->
      <div class="settings-section">
        <div class="section-title">Appearance</div>
        <q-item class="settings-item">
          <q-item-section avatar>
            <q-icon name="mdi-theme-light-dark" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Theme</q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-select
              v-model="theme"
              :options="themeOptions"
              borderless
              dense
              options-dense
              style="min-width: 120px"
            />
          </q-item-section>
        </q-item>

        <q-item class="settings-item">
          <q-item-section avatar>
            <q-icon name="mdi-text" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Font Size</q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-slider
              v-model="fontSize"
              :min="12"
              :max="20"
              label
              label-always
              style="width: 120px"
            />
          </q-item-section>
        </q-item>
      </div>

      <!-- About Section -->
      <div class="settings-section">
        <q-item clickable class="settings-item" @click="showAboutDialog = true">
          <q-item-section avatar>
            <q-icon name="mdi-information-outline" />
          </q-item-section>
          <q-item-section>
            <q-item-label>About ChatPay</q-item-label>
            <q-item-label caption>Version 1.0.0</q-item-label>
          </q-item-section>
          <q-item-section avatar>
            <q-icon name="chevron_right" />
          </q-item-section>
        </q-item>

        <q-item clickable class="settings-item" @click="openHelp">
          <q-item-section avatar>
            <q-icon name="mdi-help-circle" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Help</q-item-label>
          </q-item-section>
          <q-item-section avatar>
            <q-icon name="chevron_right" />
          </q-item-section>
        </q-item>
      </div>
    </q-scroll-area>

    <!-- About Dialog -->
    <q-dialog v-model="showAboutDialog">
      <q-card style="width: 320px">
        <q-card-section class="row items-center">
          <div class="text-h6">About</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="column items-center q-pt-none">
          <q-avatar size="80px">
            <img src="~assets/logo/chatpay-logo.png" alt="ChatPay Logo" />
          </q-avatar>
          <div class="text-center q-mt-md">
            <p class="text-body1 text-weight-medium">ChatPay v1.0.0</p>
            <p class="text-caption">
              Secure, spam-free conversations<br />
              one BCH at a time.
            </p>
            <p class="text-caption q-mt-sm">
              <a href="https://your-app-website.example.com" target="_blank" class="text-primary">
                Learn more
              </a>
            </p>
          </div>
        </q-card-section>

        <q-card-actions align="center">
          <q-btn flat label="Close" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Privacy Settings
const privacyOptions = [
  { label: 'Everyone', value: 'everyone' },
  { label: 'My Contacts', value: 'contacts' },
  { label: 'Nobody', value: 'nobody' },
]
const lastSeenPrivacy = ref('everyone')
const profilePhotoPrivacy = ref('everyone')

// Notification Settings
const notificationsEnabled = ref(true)
const soundOptions = [
  { label: 'Default', value: 'default' },
  { label: 'Chime', value: 'chime' },
  { label: 'Note', value: 'note' },
  { label: 'Silent', value: 'silent' },
]
const notificationSound = ref('default')

const onNotificationsToggle = (val) => {
  notificationsEnabled.value = val
  localStorage.setItem('chatpay_notifications_enabled', val ? '1' : '0')
}

// Appearance Settings
const themeOptions = [
  { label: 'System', value: 'system' },
  { label: 'Light', value: 'light' },
  { label: 'Dark', value: 'dark' },
]
const theme = ref('system')
const fontSize = ref(14)

// About & Help
const showAboutDialog = ref(false)
const openHelp = () => {
  window.open('https://your-app-website.example.com/help', '_blank')
}

// Navigation
const goBack = () => {
  router.back()
}

// Load saved settings
onMounted(() => {
  const stored = localStorage.getItem('chatpay_notifications_enabled')
  if (stored !== null) {
    notificationsEnabled.value = stored === '1'
  }

  // Load other settings from localStorage or API
})
</script>

<style scoped lang="scss">
.settings-page-wrapper {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f8fa;
}

.settings-header {
  flex: 0 0 auto;
  height: 56px;
  background-color: white;
  border-bottom: 1px solid #e0e0e0;
}

.settings-content {
  flex: 1 1 auto;
  padding: 8px 0;
}

.settings-section {
  background-color: white;
  margin: 8px 16px;
  border-radius: 8px;
  overflow: hidden;

  &:not(:first-child) {
    margin-top: 16px;
  }
}

.section-title {
  padding: 12px 16px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #5e5e5e;
  text-transform: uppercase;
  border-bottom: 1px solid #f0f0f0;
}

.settings-item {
  padding: 12px 16px;
  min-height: 56px;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f0f0f0;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background-color: #f5f5f5;
  }
}

.q-dialog .q-card {
  border-radius: 12px;
}
</style>
