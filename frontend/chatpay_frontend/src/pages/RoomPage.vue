<template>
  <div class="room-page-wrapper">
    <!-- Header -->
    <div class="room-header row items-center q-px-md q-py-sm">
      <q-btn dense flat round icon="arrow_back" @click="goBack" class="text-grey-8" />
      <div class="header-content column q-ml-sm">
        <span class="text-subtitle1 text-weight-medium">{{ roomName }}</span>
      </div>
      <q-space />

      <!-- Settings menu -->
      <q-btn
        dense
        flat
        round
        icon="more_vert"
        @click.stop="settingsMenu = true"
        class="text-grey-8"
      />
      <q-menu v-model="settingsMenu" anchor="bottom right" self="top right">
        <q-list style="min-width: 180px" class="text-grey-9">
          <q-item clickable v-close-popup @click="copyInviteLink">
            <q-item-section>Copy Invite Link</q-item-section>
            <q-item-section avatar>
              <q-icon name="link" />
            </q-item-section>
          </q-item>
          <q-item clickable v-close-popup @click="openRenameDialog">
            <q-item-section>Rename Room</q-item-section>
            <q-item-section avatar>
              <q-icon name="edit" />
            </q-item-section>
          </q-item>
          <q-separator />
          <q-item
            v-if="meId === createdById"
            clickable
            v-close-popup
            @click="confirmDelete"
            class="text-negative"
          >
            <q-item-section>Delete Room</q-item-section>
            <q-item-section avatar>
              <q-icon name="delete" color="negative" />
            </q-item-section>
          </q-item>
          <q-item v-else clickable v-close-popup @click="confirmLeave">
            <q-item-section>Leave Room</q-item-section>
            <q-item-section avatar>
              <q-icon name="logout" />
            </q-item-section>
          </q-item>
        </q-list>
      </q-menu>
    </div>

    <!-- Messages area -->
    <div class="room-messages">
      <q-scroll-area ref="scrollArea" class="fit">
        <div class="q-px-md q-py-sm column">
          <div v-if="!meId" class="text-caption text-grey-6 text-center q-py-lg">
            Loading messages...
          </div>
          <div
            v-else-if="messages.length === 0"
            class="text-caption text-grey-6 text-center q-py-lg"
          >
            No messages yet. Say hello!
          </div>

          <template v-else>
            <div
              v-for="(msg, index) in messages"
              :key="msg.id"
              class="row q-mb-sm"
              :class="msg.senderId === meId ? 'justify-end' : 'justify-start'"
            >
              <div class="column" style="max-width: 80%">
                <div
                  v-if="shouldShowSender(msg, index)"
                  class="sender-name text-left text-grey-7 q-pl-2"
                >
                  {{ msg.senderName }}
                </div>
                <div
                  class="row items-end"
                  :class="msg.senderId === meId ? 'justify-end' : 'justify-start'"
                >
                  <div class="msg-bubble" :class="msg.senderId === meId ? 'me' : 'other'">
                    <div class="text-body2">{{ msg.content }}</div>
                    <div class="message-time">
                      {{ formatTime(msg.timestamp) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </q-scroll-area>
    </div>

    <!-- Input bar -->
    <div class="room-input row items-center q-px-md q-py-sm">
      <div class="row items-center full-width" style="background: white; border-radius: 20px">
        <q-input
          v-model="newMsg"
          placeholder="Type a message"
          rounded
          dense
          class="full-width"
          input-class="text-body2"
          outlined
          bg-color="white"
          @keyup.enter="sendMessage"
        />
        <q-btn dense flat round icon="insert_emoticon" class="text-grey-7" />
        <q-btn
          dense
          flat
          round
          icon="send"
          color="primary"
          @click="sendMessage"
          class="q-ml-sm"
          :disable="!newMsg.trim()"
        />
      </div>
    </div>

    <!-- Rename Room Dialog -->
    <q-dialog v-model="renameDialog">
      <q-card style="width: 320px">
        <q-card-section class="row items-center">
          <div class="text-h6">Rename Room</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="newRoomName"
            label="New room name"
            autofocus
            @keyup.enter="renameRoom"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="grey" v-close-popup />
          <q-btn
            flat
            label="Save"
            color="primary"
            :disable="!newRoomName.trim()"
            @click="renameRoom"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Notify } from 'quasar'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const roomId = route.params.id

//ref and state
const scrollArea = ref(null)
const roomName = ref('')
const createdById = ref(null)
const settingsMenu = ref(false)
const renameDialog = ref(false)
const newRoomName = ref('')
const newMsg = ref('')
const messages = ref([])
const meId = ref(null)
const meName = ref('')
let socket = ref(null)

let inviteCode = ''
// helper to show sender only on first of a block
function shouldShowSender(msg, index) {
  if (msg.senderId === meId.value) return false
  if (index === 0) return true
  const prevMsg = messages.value[index - 1]
  return prevMsg.senderId !== msg.senderId
}
// scroll to bottom
async function scrollToBottom() {
  await nextTick()
  if (scrollArea.value) {
    const target = scrollArea.value.getScrollTarget()
    target.scrollTo({ top: target.scrollHeight, behavior: 'smooth' })
  }
}
// open websocket
function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const token = localStorage.getItem('access')
  // RoomPage.vue → connectWebSocket()
  const wsUrl = `${protocol}://${location.host}/ws/rooms/${roomId}/?token=${token}`

  console.log('Connecting to WebSocket at:', wsUrl)
  socket.value = new WebSocket(wsUrl)

  socket.value.onopen = () => {
    console.log('WebSocket connected')
    const token = localStorage.getItem('access')
    if (token) {
      socket.value.send(
        JSON.stringify({
          type: 'auth',
          token: token,
        }),
      )
    }
  }

  socket.value.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data)
      console.log('📨 Received WebSocket message:', data)

      // Handle auth response
      if (data.type === 'auth_success') {
        console.log('✅ WebSocket authentication successful')
        return
      }

      if (data.type === 'auth_error') {
        console.error('❌ WebSocket authentication failed:', data.message)
        return
      }

      // Handle regular chat messages
      if (data.message) {
        console.log('💬 Adding message to chat:', {
          content: data.message,
          senderId: data.sender_id,
          senderName: data.sender_name,
        })

        messages.value.push({
          id: Date.now() + Math.random(), // Ensure unique ID
          content: data.message,
          senderId: data.sender_id,
          senderName: data.sender_name || `User ${data.sender_id}`,
          timestamp: data.timestamp || new Date().toISOString(),
        })
        scrollToBottom()
      }
    } catch (err) {
      console.error('❌ Error parsing WebSocket message:', err)
    }
  }
  socket.value.onerror = (error) => {
    console.error('WebSocket error:', error)
    Notify.create({
      message: `Connection error: ${error.message || 'Unknown error'}`,
      color: 'negative',
      position: 'bottom',
    })
  }
  socket.value.onclose = (e) => {
    console.log('WebSocket closed:', e.code, e.reason)
    if (e.code !== 1000) {
      // Only reconnect if not normal closure
      setTimeout(connectWebSocket, 3000)
    }
  }
}
onBeforeUnmount(() => {
  if (socket.value) {
    socket.value.close(1000, 'Component unmounted')
  }
})

async function copyInviteLink() {
  try {
    const token = localStorage.getItem('access')
    const { data } = await axios.post(
      `/api/rooms/invite/`,
      { room: roomName.value },
      { headers: { Authorization: `Bearer ${token}` } },
    )
    inviteCode = data.code
    const url = `${window.location.origin}/rooms/join/${inviteCode}`
    await navigator.clipboard.writeText(url)
    Notify.create({
      message: 'Invite link copied to clipboard!',
      color: 'positive',
      position: 'bottom',
      timeout: 2000,
    })
  } catch (err) {
    console.error(err)
    Notify.create({
      message: 'Failed to generate invite',
      color: 'negative',
      position: 'bottom',
    })
  }
}

async function loadRoom() {
  const token = localStorage.getItem('access')
  if (!token) return
  const { data } = await axios.get(`/api/rooms/${roomId}/`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  roomName.value = data.name
  createdById.value = data.created_by.id
}

function openRenameDialog() {
  newRoomName.value = roomName.value
  settingsMenu.value = false
  renameDialog.value = true
}

async function renameRoom() {
  const name = newRoomName.value.trim()
  if (!name) return
  const token = localStorage.getItem('access')
  await axios.patch(
    `/api/rooms/${roomId}/`,
    { name },
    { headers: { Authorization: `Bearer ${token}` } },
  )
  roomName.value = name
  renameDialog.value = false
  Notify.create({
    message: 'Room renamed successfully',
    color: 'positive',
    position: 'bottom',
    timeout: 2000,
  })
}

function confirmDelete() {
  if (!window.confirm('Are you sure you want to delete this room? This cannot be undone.')) return
  deleteRoom()
}

async function deleteRoom() {
  const token = localStorage.getItem('access')
  await axios.delete(`/api/rooms/${roomId}/`, { headers: { Authorization: `Bearer ${token}` } })
  router.push('/home')
  Notify.create({
    message: 'Room deleted successfully',
    color: 'positive',
    position: 'bottom',
    timeout: 2000,
  })
}

function confirmLeave() {
  if (!window.confirm('Are you sure you want to leave this room?')) return
  leaveRoom()
}

async function leaveRoom() {
  const token = localStorage.getItem('access')
  await axios.post(
    `/api/rooms/${roomId}/leave/`,
    {},
    { headers: { Authorization: `Bearer ${token}` } },
  )
  router.push('/home')
  Notify.create({
    message: 'You have left the room',
    color: 'positive',
    position: 'bottom',
    timeout: 2000,
  })
}

async function loadMessages() {
  const token = localStorage.getItem('access')
  if (!token) return router.replace('/login')

  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    meId.value = payload.id ?? payload.user_id ?? payload.r_id ?? null
    meName.value = payload.username ?? payload.user ?? payload.name ?? ''
  } catch {
    meId.value = null
    meName.value = ''
  }

  const normalize = (str) => (str || '').trim().toLowerCase()
  const res = await axios.get(`/api/rooms/${roomId}/messages/`, {
    headers: { Authorization: `Bearer ${token}` },
  })

  messages.value = res.data.map((msg) => {
    let senderId = null,
      senderName = ''
    if (msg.sender && typeof msg.sender === 'object') {
      senderId = msg.sender.id
      senderName = msg.sender.username
    } else if (typeof msg.sender === 'number') {
      senderId = msg.sender
    } else {
      senderName = msg.sender
      senderId = msg.sender_id ?? msg.user_id ?? null
    }
    if (senderId === null && normalize(senderName) === normalize(meName.value)) {
      senderId = meId.value
    }
    return { ...msg, senderId, senderName }
  })

  await nextTick()
  if (scrollArea.value) {
    const target = scrollArea.value.getScrollTarget()
    target.scrollTo({ top: target.scrollHeight, behavior: 'smooth' })
  }
}

onMounted(() => {
  loadMessages()
  loadRoom()
  connectWebSocket()
})

async function sendMessage() {
  const text = newMsg.value.trim()
  if (!text || !socket.value || socket.value.readyState !== WebSocket.OPEN) {
    console.log('Cannot send message:', {
      hasText: !!text,
      hasSocket: !!socket.value,
      socketState: socket.value?.readyState,
    })
    return
  }

  console.log('🚀 Sending message via WebSocket:', text)

  // Send message via WebSocket instead of HTTP API
  socket.value.send(
    JSON.stringify({
      message: text,
    }),
  )

  newMsg.value = ''
  console.log('✅ Message sent, input cleared')
}

function goBack() {
  router.push('/home')
}

function formatTime(iso) {
  const d = new Date(iso)
  return d.toLocaleTimeString([], {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })
}
</script>

<style scoped>
.room-page-wrapper {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f8fa;
}

.room-header {
  flex: 0 0 auto;
  background-color: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  height: 60px;
}

.room-messages {
  flex: 1 1 auto;
  background: #f5f8fa;
  overflow: hidden;
}

.room-input {
  flex: 0 0 auto;
  background-color: #f0f2f5;
  border-top: 1px solid #e0e0e0;
}

.room-input .q-field {
  flex: 1;
}

.room-input .q-field__control {
  height: 40px;
  min-height: unset;
}

.room-input .q-field--dense .q-field__control,
.room-input .q-field--dense .q-field__marginal {
  height: 40px;
}

.msg-bubble {
  position: relative;
  display: inline-block;
  max-width: 100%;
  padding: 8px 12px;
  margin-bottom: 2px;
  line-height: 1.4;
  word-break: break-word;
  white-space: pre-line;
  font-size: 0.9375rem;
  border-radius: 12px;
}

.msg-bubble.me {
  background-color: #0088cc;
  color: white;
  border-bottom-right-radius: 4px;
}

.msg-bubble.other {
  background-color: white;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
}

.message-time {
  font-size: 0.6875rem;
  margin-top: 4px;
  line-height: 1;
  color: rgba(255, 255, 255, 0.7);
  display: inline-flex;
  align-items: center;
  margin-left: 6px;
  float: right;
}

.msg-bubble.other .message-time {
  color: rgba(0, 0, 0, 0.4);
}

.sender-name {
  font-size: 0.8125rem;
  font-weight: 500;
  margin-bottom: 2px;
  color: #5e5e5e;
}

.q-menu {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  overflow: hidden;
}
</style>
