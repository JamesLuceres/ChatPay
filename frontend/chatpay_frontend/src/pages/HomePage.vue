<!-- src/pages/HomePage.vue -->
<template>
  <div class="home-page column">
    <!-- Header with Telegram styling -->
    <div class="home-header row items-center q-px-md">
      <!-- Balance -->
      <div class="balance-display row items-center" @click="goToDepositPage">
        <q-icon name="mdi-cash" size="20px" color="primary" />
        <span class="text-caption text-primary q-ml-xs">{{ balance }} BCH</span>
      </div>

      <q-space />

      <!-- Logo -->
      <q-avatar size="45px">
        <img src="~assets/logo/chatpay-logo.png" alt="ChatPay" class="chatpay-logo" />
      </q-avatar>

      <q-space />

      <!-- Right side buttons -->
      <div class="row items-center">
        <q-btn
          flat
          round
          dense
          icon="mdi-message-plus"
          color="primary"
          @click="openCreateDialog"
          class="q-mr-xs"
        />
        <q-btn flat round dense icon="mdi-dots-vertical" color="primary">
          <q-menu auto-close :offset="[0, 8]">
            <q-list style="min-width: 180px" class="text-grey-9">
              <q-item clickable @click="openJoinDialog">
                <q-item-section avatar>
                  <q-icon name="mdi-login" />
                </q-item-section>
                <q-item-section>Join Room</q-item-section>
              </q-item>
              <q-item clickable @click="goToProfile">
                <q-item-section avatar>
                  <q-icon name="mdi-account" />
                </q-item-section>
                <q-item-section>Profile</q-item-section>
              </q-item>
              <q-item clickable @click="goToSettings">
                <q-item-section avatar>
                  <q-icon name="mdi-cog" />
                </q-item-section>
                <q-item-section>Settings</q-item-section>
              </q-item>
              <q-separator />
              <q-item clickable @click="logout">
                <q-item-section avatar>
                  <q-icon name="mdi-logout" color="negative" />
                </q-item-section>
                <q-item-section class="text-negative">Logout</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </div>
    </div>

    <!-- Search with Telegram styling -->
    <div class="home-search q-px-md q-py-sm">
      <q-input
        v-model="search"
        dense
        rounded
        outlined
        placeholder="Search conversations"
        bg-color="white"
        input-class="text-body2"
        class="telegram-search"
      >
        <template #prepend>
          <q-icon name="mdi-magnify" />
        </template>
      </q-input>
    </div>
    <!-- tabs for different chat lists -->
    <div>
      <q-tabs v-model="activeTab" class="text-primary" align="justify" dense>
        <q-tab name="all" label="All Chats" />
        <q-tab name="admin" label="Admin Chats" />
        <q-tab name="member" label="Member Chats" />
      </q-tabs>
      <q-separator />
    </div>

    <!-- Chat List with Telegram styling -->
    <q-scroll-area class="home-scroll">
      <q-list padding class="chat-list">
        <q-item
          v-for="room in filteredRooms"
          :key="room.id"
          clickable
          v-ripple
          @click="openRoom(room.id)"
          class="chat-item"
          :class="{ 'chat-item--active': room.id === activeId }"
        >
          <q-item-section>
            <div class="row justify-between items-center">
              <span class="text-body2 text-weight-medium">{{ room.name }}</span>
              <span class="text-caption text-grey-6">{{ room.lastTime }}</span>
            </div>
            <div class="row items-center q-mt-xs">
              <span class="text-caption text-grey-7 ellipsis">
                {{ room.lastMessage || 'No messages yet' }}
              </span>
            </div>
          </q-item-section>
        </q-item>

        <q-item v-if="filteredRooms.length === 0" class="empty-state">
          <q-item-section class="text-center">
            <q-icon size="40px" color="grey-5" class="q-mb-sm" />
            <div class="text-caption text-grey-6">No conversations found</div>
          </q-item-section>
        </q-item>
      </q-list>
    </q-scroll-area>

    <!-- Dialogs with Telegram styling -->
    <q-dialog v-model="createDialog">
      <q-card style="width: 320px">
        <q-card-section class="row items-center">
          <div class="text-h6">Create New Room</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="newRoomName"
            label="Room name"
            placeholder="Enter a unique room name"
            autofocus
            @keyup.enter="confirmCreate"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="grey" v-close-popup />
          <q-btn
            flat
            label="Create"
            color="primary"
            :disable="!newRoomName.trim()"
            @click="confirmCreate"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="joinDialog">
      <q-card style="width: 320px">
        <q-card-section class="row items-center">
          <div class="text-h6">Join Room</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="joinCode"
            label="Invite code"
            placeholder="Paste the code or URL"
            autofocus
            @keyup.enter="confirmJoin"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="grey" v-close-popup />
          <q-btn
            flat
            label="Join"
            color="primary"
            :disable="!joinCode.trim()"
            @click="confirmJoin"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <div class="contract-address text-caption text-grey-7 q-ml-xs">
      Address: {{ contractAddress }}
    </div>
    <div class="user-pubkey text-caption text-grey-7 q-ml-xs">PubKey: {{ userPubKey }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Notify } from 'quasar'
import { cashScriptService } from '../services/cashscript-service.js'

const router = useRouter()
const search = ref('')
const activeId = ref(null)

// Create dialog state
const createDialog = ref(false)
const newRoomName = ref('')
// The live rooms list
const rooms = ref([])
// Join dialog state
const joinDialog = ref(false)
const joinCode = ref('')

// decode my user id
const meId = ref(null)
function loadMe() {
  const token = localStorage.getItem('access')
  if (token) {
    const payload = JSON.parse(atob(token.split('.')[1]))
    meId.value = payload.id ?? payload.user_id ?? payload.r_id
  }
}

// tabs for chat
const activeTab = ref('all')
const adminChats = computed(() => rooms.value.filter((room) => room.isAdmin))
const memberChats = computed(() => rooms.value.filter((room) => !room.isAdmin))

// Fetch rooms from backend
async function loadRooms() {
  try {
    const token = localStorage.getItem('access')
    const { data } = await axios.get('/api/rooms/my/', {
      headers: { Authorization: `Bearer ${token}` },
    })

    rooms.value = data.map((r) => ({
      id: r.id,
      name: r.name,
      isAdmin: r.created_by.id === meId.value,
      lastMessage: r.last_message ? r.last_message.content : '',
      lastTime: r.last_message
        ? new Date(r.last_message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })
        : '',
    }))
  } catch (err) {
    console.error('Failed to load rooms', err)
    Notify.create({ type: 'negative', message: 'Could not load rooms.' })
  }
}

onMounted(loadRooms)

// Filter rooms by search term
const filteredRooms = computed(() => {
  const term = search.value.trim().toLowerCase()
  let filtered = rooms.value
  if (activeTab.value === 'admin') {
    filtered = adminChats.value
  } else if (activeTab.value === 'member') {
    filtered = memberChats.value
  }
  return term === ''
    ? filtered
    : filtered.filter(
        (r) => r.name.toLowerCase().includes(term) || r.lastMessage.toLowerCase().includes(term),
      )
})

// Navigation functions
function goToDepositPage() {
  router.push('/deposit')
}

function goToProfile() {
  router.push('/profile')
}

function goToSettings() {
  router.push('/settings')
}

function logout() {
  localStorage.removeItem('access')
  router.push('/login')
}

// Room functions
function openRoom(roomId) {
  activeId.value = roomId
  router.push(`/rooms/${roomId}`)
}

function openCreateDialog() {
  newRoomName.value = ''
  createDialog.value = true
}

async function confirmCreate() {
  // Fixed typo from confintCreate
  const name = newRoomName.value.trim()
  if (!name) return

  try {
    const token = localStorage.getItem('access')
    const { data } = await axios.post(
      '/api/rooms/',
      { name },
      { headers: { Authorization: `Bearer ${token}` } },
    )

    createDialog.value = false
    Notify.create({ type: 'positive', message: `Room "${data.name}" created` })
    router.push(`/rooms/${data.id}`)
  } catch {
    Notify.create({ type: 'negative', message: 'Failed to create room.' })
  }
}

function openJoinDialog() {
  joinCode.value = ''
  joinDialog.value = true
}

async function confirmJoin() {
  // Fixed typo from confintJoin
  const codeRaw = joinCode.value.trim()
  if (!codeRaw) return

  // Extract just the UUID if they pasted the full URL
  const matches = codeRaw.match(/[0-9A-Fa-f-]{36}/)
  const code = matches ? matches[0] : codeRaw

  try {
    const token = localStorage.getItem('access')
    const { data } = await axios.post(
      `/api/rooms/join/${code}/`,
      {},
      { headers: { Authorization: `Bearer ${token}` } },
    )

    joinDialog.value = false
    Notify.create({ type: 'positive', message: `Joined "${data.name}"` })
    router.push(`/rooms/${data.id}`)
  } catch (err) {
    console.error('Join failed', err)
    Notify.create({ type: 'negative', message: 'Invalid invite code.' })
  }
}

// New balance functionality
const balance = ref('0.00000')
const contractAddress = ref('')
const userPubKey = ref('')

async function loadContractAndBalance() {
  try {
    await cashScriptService.createUserWalletContract()
    contractAddress.value = cashScriptService.getContractAddress()
    balance.value = await cashScriptService.fetchBalance()
    userPubKey.value = cashScriptService.userPubKey
  } catch (err) {
    console.error('Failed to load contract or balance', err)
    balance.value = '0.00000'
    contractAddress.value = ''
    userPubKey.value = ''
  }
}

onMounted(() => {
  loadMe()
  loadContractAndBalance()
})
</script>

<style scoped lang="scss">
.home-page {
  height: 100vh;
  background-color: #e6ebee;
}

.home-header {
  flex: 0 0 auto;
  height: 56px;
  background-color: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 8px 16px;
}

.balance-display {
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 18px;
  background-color: rgba(0, 150, 136, 0.1);
  transition: background-color 0.2s;

  &:hover {
    background-color: rgba(0, 150, 136, 0.2);
  }
}

.home-search {
  flex: 0 0 auto;
  background-color: #f5f6fa;
  padding: 8px 16px;
}

.telegram-search .q-field__control {
  height: 36px;
  min-height: unset;
  border-radius: 18px;
}

.home-scroll {
  flex: 1 1 auto;
}

.chat-list {
  padding: 0;
}

.chat-item {
  padding: 12px 16px;
  margin: 0;
  background-color: white;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f0f0f0;

  &:hover {
    background-color: #f5f5f5;
  }

  &--active {
    background-color: #e3f2fd;
    border-left: 3px solid #2196f3;
  }
}

.empty-state {
  padding: 40px 16px;
  text-align: center;
}

.chatpay-logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.q-menu {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.q-dialog .q-card {
  border-radius: 12px;
}
</style>
