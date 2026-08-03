<template>
  <div class="settings-page-wrapper">
    <!-- Header -->
    <div class="settings-header row items-center q-px-md">
      <q-btn flat round icon="arrow_back" @click="goBack" />
      <span class="text-h6 q-ml-sm">Settings</span>
    </div>

    <!-- Settings Content -->
    <q-scroll-area class="settings-content">
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
            <q-item-label>Dark Mode</q-item-label>
            <q-item-label caption>Switch between light and dark themes</q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-toggle v-model="darkMode" color="primary" @update:model-value="onDarkModeToggle" />
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

    <!-- Help Dialog -->
    <q-dialog v-model="showHelpDialog" maximized>
      <q-card class="help-dialog">
        <q-card-section class="help-header row items-center">
          <q-btn flat round icon="arrow_back" @click="showHelpDialog = false" />
          <span class="text-h6 q-ml-sm">Help & Support</span>
          <q-space />
          <q-btn icon="close" flat round dense @click="showHelpDialog = false" />
        </q-card-section>

        <q-scroll-area class="help-content">
          <!-- Getting Started Section -->
          <div class="help-section">
            <div class="help-section-title">
              <q-icon name="mdi-rocket-launch" size="20px" class="q-mr-sm" />
              Getting Started
            </div>

            <q-expansion-item
              icon="mdi-wallet"
              label="Setting Up Your Wallet"
              header-class="help-expansion-header"
              class="help-expansion-item"
            >
              <q-card class="help-expansion-content">
                <q-card-section>
                  <p class="help-text">
                    <strong>1. Deposit BCH:</strong> Click on your balance in the top-left corner to
                    access the deposit page. You'll need at least 0.00018 BCH to start using
                    ChatPay.
                  </p>
                  <p class="help-text">
                    <strong>2. Wallet Address:</strong> Your unique wallet address is automatically
                    generated based on your username. This address is used for all transactions
                    within ChatPay.
                  </p>
                  <p class="help-text">
                    <strong>3. Balance Check:</strong> Your current balance is displayed in the
                    header. Keep sufficient funds for room creation and message payments.
                  </p>
                </q-card-section>
              </q-card>
            </q-expansion-item>

            <q-expansion-item
              icon="mdi-message-plus"
              label="Creating and Joining Rooms"
              header-class="help-expansion-header"
              class="help-expansion-item"
            >
              <q-card class="help-expansion-content">
                <q-card-section>
                  <p class="help-text">
                    <strong>Creating a Room:</strong>
                  </p>
                  <ul class="help-list">
                    <li>Tap the floating action button (FAB) in the bottom-right corner</li>
                    <li>Select "Create Room"</li>
                    <li>Enter a unique room name</li>
                    <li>Confirm the payment of 0.000037 BCH (room creation fee)</li>
                    <li>Wait for payment confirmation</li>
                  </ul>

                  <p class="help-text q-mt-md">
                    <strong>Joining a Room:</strong>
                  </p>
                  <ul class="help-list">
                    <li>Tap the FAB and select "Join Room"</li>
                    <li>Enter the invite code or paste the full room URL</li>
                    <li>Ensure you have at least 0.00018 BCH in your wallet</li>
                    <li>You'll be automatically added to the room</li>
                  </ul>
                </q-card-section>
              </q-card>
            </q-expansion-item>
          </div>

          <!-- How It Works Section -->
          <div class="help-section">
            <div class="help-section-title">
              <q-icon name="mdi-lightbulb" size="20px" class="q-mr-sm" />
              How ChatPay Works
            </div>

            <q-expansion-item
              icon="mdi-currency-btc"
              label="Payment System"
              header-class="help-expansion-header"
              class="help-expansion-item"
            >
              <q-card class="help-expansion-content">
                <q-card-section>
                  <p class="help-text">
                    ChatPay uses Bitcoin Cash (BCH) to create spam-free, value-driven conversations:
                  </p>
                  <ul class="help-list">
                    <li><strong>Room Creation:</strong> 0.000037 BCH (prevents spam rooms)</li>
                    <li>
                      <strong>Message Payments:</strong> 0.000001 BCH per message (minimal cost)
                    </li>
                    <li><strong>Admin Benefits:</strong> Room creators receive message payments</li>
                    <li>
                      <strong>Smart Contracts:</strong> All payments are handled automatically
                    </li>
                  </ul>
                  <p class="help-text q-mt-md">
                    This system ensures that every message has value and discourages spam while
                    rewarding quality content creators.
                  </p>
                </q-card-section>
              </q-card>
            </q-expansion-item>

            <q-expansion-item
              icon="mdi-shield-check"
              label="Security & Privacy"
              header-class="help-expansion-header"
              class="help-expansion-item"
            >
              <q-card class="help-expansion-content">
                <q-card-section>
                  <p class="help-text">
                    <strong>Your Security:</strong>
                  </p>
                  <ul class="help-list">
                    <li>All transactions are secured by Bitcoin Cash blockchain</li>
                    <li>Your wallet is controlled by your username and user ID</li>
                    <li>No personal information is stored on-chain</li>
                    <li>Messages are encrypted and secure</li>
                  </ul>
                  <p class="help-text q-mt-md">
                    <strong>Privacy Features:</strong>
                  </p>
                  <ul class="help-list">
                    <li>Control who can see your last seen time</li>
                    <li>Manage profile photo visibility</li>
                    <li>All settings are stored locally on your device</li>
                  </ul>
                </q-card-section>
              </q-card>
            </q-expansion-item>
          </div>

          <!-- Troubleshooting Section -->
          <div class="help-section">
            <div class="help-section-title">
              <q-icon name="mdi-wrench" size="20px" class="q-mr-sm" />
              Troubleshooting
            </div>

            <q-expansion-item
              icon="mdi-alert-circle"
              label="Common Issues"
              header-class="help-expansion-header"
              class="help-expansion-item"
            >
              <q-card class="help-expansion-content">
                <q-card-section>
                  <p class="help-text">
                    <strong>"Insufficient Balance" Error:</strong>
                  </p>
                  <ul class="help-list">
                    <li>Ensure you have at least 0.00018 BCH for joining rooms</li>
                    <li>For room creation, you need 0.000037 BCH + 0.000001 BCH fee</li>
                    <li>Check your balance in the top-left corner of the home screen</li>
                    <li>Deposit more BCH if needed</li>
                  </ul>

                  <p class="help-text q-mt-md">
                    <strong>"Payment Not Received" Error:</strong>
                  </p>
                  <ul class="help-list">
                    <li>Wait up to 30 seconds for payment confirmation</li>
                    <li>Check your internet connection</li>
                    <li>Try refreshing the page and retry</li>
                    <li>Contact support if the issue persists</li>
                  </ul>

                  <p class="help-text q-mt-md">
                    <strong>"Invalid Invite Code" Error:</strong>
                  </p>
                  <ul class="help-list">
                    <li>Make sure you copied the entire code correctly</li>
                    <li>You can paste the full room URL - the app will extract the code</li>
                    <li>Check that the room still exists and is active</li>
                  </ul>
                </q-card-section>
              </q-card>
            </q-expansion-item>

            <q-expansion-item
              icon="mdi-refresh"
              label="Network Issues"
              header-class="help-expansion-header"
              class="help-expansion-item"
            >
              <q-card class="help-expansion-content">
                <q-card-section>
                  <p class="help-text">
                    <strong>If you experience network issues:</strong>
                  </p>
                  <ul class="help-list">
                    <li>Check your internet connection</li>
                    <li>Try refreshing the page</li>
                    <li>Wait a few minutes and try again</li>
                    <li>Ensure you're not behind a restrictive firewall</li>
                    <li>Contact support if issues persist</li>
                  </ul>
                </q-card-section>
              </q-card>
            </q-expansion-item>
          </div>

          <!-- Contact Section -->
          <div class="help-section">
            <div class="help-section-title">
              <q-icon name="mdi-email" size="20px" class="q-mr-sm" />
              Contact & Support
            </div>

            <q-card class="help-contact-card">
              <q-card-section>
                <div class="row items-center q-mb-md">
                  <q-icon name="mdi-email-outline" size="24px" color="primary" class="q-mr-sm" />
                  <span class="text-body1 text-weight-medium">Need More Help?</span>
                </div>
                <p class="help-text">
                  If you couldn't find the answer to your question here, please contact our support
                  team:
                </p>
                <div class="row q-gutter-sm q-mt-md">
                  <q-btn
                    color="primary"
                    icon="mdi-email"
                    label="Email Support"
                    @click="contactSupport"
                    class="full-width"
                  />
                  <q-btn
                    color="secondary"
                    icon="mdi-web"
                    label="Visit Website"
                    @click="visitWebsite"
                    class="full-width"
                  />
                </div>
              </q-card-section>
            </q-card>
          </div>
        </q-scroll-area>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import darkModeService from '../services/dark-mode-service.js'

const router = useRouter()

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
const darkMode = ref(darkModeService.isDarkMode)

const onDarkModeToggle = (val) => {
  darkMode.value = val
  darkModeService.setDarkMode(val)
}

// About & Help
const showAboutDialog = ref(false)
const showHelpDialog = ref(false)

const openHelp = () => {
  showHelpDialog.value = true
}

const contactSupport = () => {
  window.open('mailto:support@chatpay.example.com?subject=ChatPay Support Request', '_blank')
}

const visitWebsite = () => {
  window.open('https://your-app-website.example.com', '_blank')
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

  // Update dark mode ref to match service state
  darkMode.value = darkModeService.isDarkMode
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

// Help Dialog Styles
.help-dialog {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f8fa;
}

.help-header {
  flex: 0 0 auto;
  height: 56px;
  background-color: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 8px 16px;
}

.help-content {
  flex: 1 1 auto;
  padding: 8px 0;
}

.help-section {
  margin: 8px 16px;

  &:not(:first-child) {
    margin-top: 16px;
  }
}

.help-section-title {
  padding: 12px 16px;
  font-size: 1rem;
  font-weight: 600;
  color: #1976d2;
  background-color: white;
  border-radius: 8px 8px 0 0;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
}

.help-expansion-item {
  background-color: white;
  border-radius: 0 0 8px 8px;
  margin-bottom: 8px;

  &:not(:first-child) {
    border-radius: 8px;
    margin-top: 8px;
  }
}

.help-expansion-header {
  padding: 16px;
  font-weight: 500;

  &:hover {
    background-color: #f5f5f5;
  }
}

.help-expansion-content {
  background-color: #fafafa;
  border-top: 1px solid #e0e0e0;
}

.help-text {
  margin: 8px 0;
  line-height: 1.5;
  color: #424242;
}

.help-list {
  margin: 8px 0;
  padding-left: 20px;

  li {
    margin: 4px 0;
    line-height: 1.4;
    color: #424242;
  }
}

.help-contact-card {
  background-color: white;
  border-radius: 8px;
  margin-top: 8px;
}
</style>
