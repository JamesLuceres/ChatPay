<!-- src/pages/HomePage.vue -->
<template>
  <div class="home-page column">
    <!-- ─────────────────────────── HEADER ─────────────────────────── -->
    <div
      class="home-header row items-center bg-grey-3 q-px-md q-py-xs"
      style="box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1)"
    >
      <!-- Deposit/Balance -->
      <q-btn
        round
        dense
        flat
        aria-label="Deposit BCH"
        icon="mdi-cash"
        class="text-primary"
        @click="goToDepositPage"
      />
      <span class="text-subtitle2 text-primary q-ml-sm">0.00001 BCH</span>

      <!-- Center Logo -->
      <div class="q-ml-auto q-mr-auto flex items-center">
        <q-avatar>
          <img src="~assets/logo/chatpay-logo.png" alt="ChatPay Logo" class="chatpay-logo" />
        </q-avatar>
      </div>

      <!-- “Create New Room” Button -->
      <q-btn
        round
        dense
        flat
        icon="mdi-message-plus"
        class="q-ml-sm text-primary"
        aria-label="Create New Room"
        @click="goToCreateRoom"
      />

      <!-- “More” menu -->
      <q-btn round dense flat icon="mdi-dots-vertical" class="q-ml-xs text-primary">
        <q-menu auto-close :offset="[0, 8]">
          <q-list style="min-width: 150px">
            <q-item clickable @click="joinRoom">
              <q-item-section>Join Room</q-item-section>
            </q-item>
            <q-item clickable @click="goToProfile">
              <q-item-section>Profile</q-item-section>
            </q-item>
            <q-item clickable @click="goToSettings">
              <q-item-section>Settings</q-item-section>
            </q-item>
            <q-item clickable @click="logout">
              <q-item-section>Logout</q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-btn>
    </div>

    <!-- ─────────────────────────── SEARCH BAR ─────────────────────────── -->
    <div class="home-search-bar row items-center bg-grey-2 q-px-md q-py-xs">
      <q-input
        v-model="search"
        dense
        rounded
        outlined
        placeholder="Search conversations"
        class="home-search-input"
        bg-color="white"
        input-class="text-body2"
      >
        <template #prepend>
          <q-icon name="mdi-magnify" />
        </template>
      </q-input>
    </div>

    <!-- ─────────────────────────── CHAT LIST ─────────────────────────── -->
    <q-scroll-area class="home-scroll">
      <q-list padding class="q-pt-none q-pb-none">
        <q-item
          v-for="room in filteredRooms"
          :key="room.id"
          clickable
          v-ripple
          @click="openRoom(room.id)"
          class="home-chat-item row items-start"
          :class="{ 'home-chat-item--active': room.id === activeId }"
        >
          <q-item-section avatar class="q-pr-sm">
            <q-avatar size="40px">
              <img :src="room.avatar || defaultAvatar" alt="Avatar" />
            </q-avatar>
          </q-item-section>

          <q-item-section class="column">
            <div class="row justify-between items-center q-mb-xs">
              <span class="text-body1">{{ room.name }}</span>
              <span class="text-caption text-grey-6">{{ room.lastTime }}</span>
            </div>
            <div class="row items-center">
              <span class="text-caption text-grey-7 ellipsis">
                {{ room.lastMessage || 'No messages yet.' }}
              </span>
            </div>
          </q-item-section>
        </q-item>

        <q-separator v-for="r in filteredRooms.slice(0, -1)" :key="r.id + '-sep'" />

        <q-item v-if="filteredRooms.length === 0" class="q-pa-md justify-center">
          <q-item-section>
            <div class="text-caption text-center text-grey-6">No conversations found.</div>
          </q-item-section>
        </q-item>
      </q-list>
    </q-scroll-area>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const search = ref('')
const activeId = ref(null)

// Placeholder avatar
const defaultAvatar = 'https://cdn.quasar.dev/img/boy-avatar.png'

// The live rooms list
const rooms = ref([])

// Fetch “my rooms” from backend
async function loadRooms() {
  try {
    const token = localStorage.getItem('chatpay_access_token')
    const { data } = await axios.get('/api/rooms/my/', {
      headers: { Authorization: `Bearer ${token}` },
    })

    // Map API shape → UI shape
    rooms.value = data.map((r) => ({
      id: r.id,
      name: r.name,
      avatar: defaultAvatar,
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
    // you might show a Notify here
  }
}

onMounted(loadRooms)

// Filter rooms by search term
const filteredRooms = computed(() => {
  const term = search.value.trim().toLowerCase()
  return term === ''
    ? rooms.value
    : rooms.value.filter(
        (r) => r.name.toLowerCase().includes(term) || r.lastMessage.toLowerCase().includes(term),
      )
})

// Navigation helpers
function goToDepositPage() {
  router.push('/deposit')
}
function goToCreateRoom() {
  router.push('/rooms/create')
}
function joinRoom() {
  /* ... */
}
function goToProfile() {
  router.push('/profile')
}
function goToSettings() {
  router.push('/settings')
}
function logout() {
  localStorage.removeItem('chatpay_access_token')
  router.push('/login')
}

// Open a room
function openRoom(roomId) {
  activeId.value = roomId
  router.push(`/rooms/${roomId}`)
}
</script>

<style scoped>
/*wrapper fill the entire viewport */
.home-page {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f5f8fa; /* same as bg-grey-4 */
}

/* Fixed‐height header (deposit/balance + logo + buttons) */
.home-header {
  flex: 0 0 auto;
  z-index: 1;
}

/* SEARCH ROW: below header */
.home-search-bar {
  flex: 0 0 auto;
  padding-top: 4px;
  padding-bottom: 4px;
}

/* Make search input grow to fill horizontal space */
.home-search-input {
  flex: 1;
}

/* The scroll‐area with chat‐list must fill the remaining vertical space */
.home-scroll {
  flex: 1 1 auto;
}

/* Default padding around each chat item */
.home-chat-item {
  padding: 8px 16px;
  margin: 4px 16px;
  border-radius: 8px;
  transition:
    background-color 0.2s,
    box-shadow 0.2s;
  cursor: pointer;
}

/* Light box‐shadow by default */
.home-chat-item {
  background-color: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

/* Hover state */
.home-chat-item:hover {
  background-color: #f0f4f8;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}

/* Active/Focused conversation */
.home-chat-item--active {
  background-color: #e1f5fe;
  border-left: 4px solid #29b6f6;
}

/* Truncate long captions */
.ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Avatar logo styling */
.chatpay-logo {
  width: auto;
  height: auto;
  object-fit: contain;
  mix-blend-mode: multiply;
}
</style>
