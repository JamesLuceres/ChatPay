<template>
  <div class="room-page-wrapper">
    <!-- Header -->
    <div class="room-header row items-center q-px-md q-py-sm">
      <q-btn dense flat round icon="arrow_back" @click="goBack" class="text-grey-8" />
      <div class="header-content column q-ml-sm">
        <span class="text-subtitle1 text-weight-medium">{{ roomName }}</span>
      </div>
      <q-space />

      <!-- Balance display -->
      <div class="balance-display row items-center q-mr-md" @click.stop="refreshBalance">
        <q-icon
          :name="isRefreshingBalance ? 'mdi-sync' : 'mdi-currency-btc'"
          size="16px"
          :color="isRefreshingBalance ? 'orange' : 'primary'"
          :class="{ 'rotate-360': isRefreshingBalance }"
        />
        <span class="text-caption text-primary q-ml-xs">{{ balance }} BCH</span>
      </div>

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
          <q-item v-if="meId === createdById" clickable v-close-popup @click="openRenameDialog">
            <q-item-section>Rename Room</q-item-section>
            <q-item-section avatar>
              <q-icon name="edit" />
            </q-item-section>
          </q-item>
          <q-item clickable v-close-popup @click="manageChatMembers">
            <q-item-section>Member List</q-item-section>
            <q-item-section avatar>
              <q-icon name="people" />
            </q-item-section>
          </q-item>
          <q-item
            v-if="meId === createdById"
            clickable
            v-close-popup
            @click="openRoomSettingsDialog"
          >
            <q-item-section>Room Settings</q-item-section>
            <q-item-section avatar>
              <q-icon name="settings" />
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
            No messages yet.
          </div>

          <template v-else>
            <div
              v-for="(msg, index) in messages"
              :key="msg.id"
              class="row q-mb-sm"
              :class="msg.senderId === meId ? 'justify-end' : 'justify-start'"
            >
              <div class="column" style="max-width: 80%; position: relative">
                <div
                  v-if="shouldShowSender(msg, index)"
                  class="sender-name text-left text-grey-7 q-pl-2"
                >
                  {{ msg.senderName }}
                </div>
                <div
                  class="row items-end no-wrap"
                  :class="msg.senderId === meId ? 'justify-end' : 'justify-start'"
                >
                  <div v-if="msg.senderId === meId && msg.pending" class="msg-side-spinner q-mr-xs">
                    <q-spinner size="16px" color="primary" />
                  </div>
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
        <!-- <q-btn dense flat round icon="insert_emoticon" class="text-grey-7" /> -->
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

    <!-- Chat Members Dialog -->
    <q-dialog v-model="chatMembersDialog">
      <q-card style="width: 400px; max-width: 90vw">
        <q-card-section class="row items-center">
          <div class="text-h6">Room Members</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section>
          <q-list>
            <q-item v-for="member in members" :key="member.id">
              <q-item-section>
                <div>
                  {{ member.username }}
                  <span v-if="member.id === adminId" class="q-ml-xs text-primary text-caption"
                    >(admin)</span
                  >
                  <span v-else class="q-ml-xs text-grey-6 text-caption">(member)</span>
                </div>
                <div class="text-caption text-grey-6">{{ member.email }}</div>
              </q-item-section>
              <q-item-section side v-if="meId == adminId && member.id !== adminId">
                <q-btn
                  dense
                  flat
                  icon="remove_circle"
                  color="negative"
                  @click="removeMember(member.id)"
                  title="Remove from room"
                />
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>
    </q-dialog>
    <!-- Room Settings Dialog -->
    <q-dialog v-model="roomSettingsDialog">
      <q-card style="width: 400px">
        <q-card-section class="row items-center">
          <div class="text-h6">Room Settings</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <div class="text-subtitle2 q-mb-sm">Max Number of Participants</div>
          <q-input
            v-model.number="maxParticipants"
            type="number"
            label="Maximum users"
            min="0"
            class="q-mt-md"
            @keyup.enter="saveRoomSettings"
          />
          <div class="text-caption text-grey-6 q-mt-xs">0 means unlimited users.</div>
          <div class="text-subtitle2 q-mb-sm">Minimum Balance Requirement</div>
          <q-input
            v-model.number="minBalanceRequired"
            type="number"
            label="Minimum BCH balance to join"
            suffix="BCH"
            step="0.00001"
            min="0"
            autofocus
            @keyup.enter="saveRoomSettings"
          />
          <div class="text-caption text-grey-6 q-mt-sm">
            Users must have at least this amount of BCH to join this room.
          </div>
          <q-input
            v-model.number="messageFee"
            type="number"
            label="Message fee per message"
            suffix="BCH"
            step="0.000001"
            min="0"
            class="q-mt-md"
            @keyup.enter="saveRoomSettings"
          />
          <div class="text-caption text-grey-6 q-mt-xs">
            Users must pay this amount of BCH to send each message in this room.
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="grey" v-close-popup />
          <q-btn
            flat
            label="Save"
            color="primary"
            :disable="minBalanceRequired < 0"
            @click="saveRoomSettings"
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
import UserWalletService from '../services/cashscript-service.js'
import RoomCreateArtifact from '../contracts/RoomCreate.json'
import { Contract, ElectrumNetworkProvider, Network } from 'cashscript'
import { decodeCashAddress } from '@bitauth/libauth'

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
const roomSettingsDialog = ref(false)
const minBalanceRequired = ref(0.00018)
const chatMembersDialog = ref(false)
const members = ref([])
const adminId = ref(null)
const newMsg = ref('')
const messages = ref([])
const meId = ref(null)
const meName = ref('')
const maxParticipants = ref(0)
let socket = ref(null)

// Balance functionality
const balance = ref('0.00000')
const isRefreshingBalance = ref(false)
let walletSvc = null

let inviteCode = ''
const roomUuid = ref('')
const roomContractAddress = ref('')

// Add a reactive variable for message fee
const messageFee = ref(0.000018)

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
  }

  socket.value.onmessage = async (e) => {
    try {
      const data = JSON.parse(e.data)
      // If this is a message from me and I have a pending message with the same content, update it
      if (data.message && data.sender_id === meId.value) {
        const pendingIdx = messages.value.findIndex((m) => m.content === data.message && m.pending)
        if (pendingIdx !== -1) {
          // Replace the pending message with the confirmed one from backend
          messages.value[pendingIdx] = {
            id: data.id || Date.now() + Math.random(),
            content: data.message,
            senderId: data.sender_id,
            senderName: data.sender_name || meName.value,
            timestamp: data.timestamp || new Date().toISOString(),
            pending: false,
          }
          await refreshBalance()
          scrollToBottom()
          return
        }
      }
      // Only push if it's not a duplicate of a pending message
      messages.value.push({
        id: data.id || Date.now() + Math.random(),
        content: data.message,
        senderId: data.sender_id,
        senderName: data.sender_name,
        timestamp: data.timestamp,
        pending: false,
      })
      scrollToBottom()
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
  roomUuid.value = data.id // UUID string
  roomContractAddress.value = data.contract_address
  minBalanceRequired.value = data.min_balance_required || 0.00018
  messageFee.value = data.message_fee || 0.000018
  maxParticipants.value = data.max_participants || 0
  console.log('Room data:', data)
  console.log('Room contract address from backend:', data.contract_address)
}

async function manageChatMembers() {
  settingsMenu.value = false
  chatMembersDialog.value = true
  await loadRoomMembers()
}

async function loadRoomMembers() {
  try {
    const token = localStorage.getItem('access')
    const { data } = await axios.get(`/api/rooms/${roomId}/members/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    members.value = data.members
    adminId.value = data.admin_id
  } catch (err) {
    console.error(err)
    Notify.create({
      message: 'Failed to load members',
      color: 'negative',
      position: 'bottom',
    })
  }
}

async function removeMember(memberId) {
  if (!window.confirm('Remove this member from the room?')) return
  try {
    const token = localStorage.getItem('access')
    await axios.post(
      `/api/rooms/${roomId}/remove_member/`,
      { member_id: memberId },
      { headers: { Authorization: `Bearer ${token}` } },
    )
    members.value = members.value.filter((m) => m.id !== memberId)
    Notify.create({
      message: 'Member removed',
      color: 'positive',
      position: 'bottom',
      timeout: 2000,
    })
  } catch (err) {
    console.error(err)
    Notify.create({
      message: 'Failed to remove member',
      color: 'negative',
      position: 'bottom',
    })
  }
}

function openRenameDialog() {
  newRoomName.value = roomName.value
  settingsMenu.value = false
  renameDialog.value = true
}

function openRoomSettingsDialog() {
  settingsMenu.value = false
  roomSettingsDialog.value = true
}

async function saveRoomSettings() {
  try {
    const token = localStorage.getItem('access')
    await axios.patch(
      `/api/rooms/${roomId}/settings/`,
      {
        min_balance_required: minBalanceRequired.value,
        message_fee: messageFee.value,
        max_participants: maxParticipants.value,
      },
      { headers: { Authorization: `Bearer ${token}` } },
    )
    roomSettingsDialog.value = false
    Notify.create({
      message: 'Room settings updated successfully',
      color: 'positive',
      position: 'bottom',
      timeout: 2000,
    })
  } catch (error) {
    console.error('Failed to update room settings:', error)
    Notify.create({
      message: 'Failed to update room settings',
      color: 'negative',
      position: 'bottom',
    })
  }
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

// Helper for locking bytecode
function addressToLockingBytecode(address) {
  const decoded = decodeCashAddress(address)
  if (!decoded || !decoded.payload) {
    throw new Error(`Invalid CashAddress: ${address}`)
  }
  const { payload, type } = decoded
  // handle numeric or string types
  if (type === 0 || type === 'p2pkh') {
    // P2PKH → OP_DUP OP_HASH160 <20> OP_EQUALVERIFY OP_CHECKSIG
    return new Uint8Array([0x76, 0xa9, 0x14, ...payload, 0x88, 0xac])
  }
  if (type === 1 || type === 'p2sh') {
    // P2SH → OP_HASH160 <20> OP_EQUAL
    return new Uint8Array([0xa9, 0x14, ...payload, 0x87])
  }
  throw new Error(`Unsupported address type: ${type}`)
}

async function withdrawAndDeleteRoom() {
  try {
    // 1. Get admin wallet info
    const token = localStorage.getItem('access')
    const { data: profile } = await axios.get('/api/profile/', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const username = profile.username
    const userId = profile.id
    const userWallet = new UserWalletService(username, userId)
    // Get the UserWallet contract address and extract the 32-byte hash256
    const userWalletContractAddress = userWallet.getAddress()
    const decoded = decodeCashAddress(userWalletContractAddress)
    const adminLockingHash256 = decoded.payload

    // 2. Prepare contract args
    const roomIdBytes = new TextEncoder().encode(roomUuid.value)
    // You need to use the same payee address as at creation
    const payeeAddress = 'bitcoincash:qp5le2vn7hjs73tlgskfdswzy60s908ly5wtll9lm9' // update if dynamic
    const payeeLockingBytecode = addressToLockingBytecode(payeeAddress)

    // 3. Load the contract
    const provider = new ElectrumNetworkProvider(Network.MAINNET)

    // Use the stored contract address if available, otherwise recreate
    let roomCreateContract
    if (roomContractAddress.value) {
      // Use the stored contract address
      roomCreateContract = new Contract(
        RoomCreateArtifact,
        [roomIdBytes, payeeLockingBytecode, adminLockingHash256],
        { provider, address: roomContractAddress.value },
      )
    } else {
      // Recreate the contract (fallback)
      roomCreateContract = new Contract(
        RoomCreateArtifact,
        [roomIdBytes, payeeLockingBytecode, adminLockingHash256],
        { provider },
      )
    }

    // 4. Get contract UTXOs and calculate total
    const utxos = await roomCreateContract.getUtxos()
    const totalSats = utxos.reduce((sum, u) => sum + BigInt(u.satoshis), 0n)

    if (totalSats === 0n) {
      Notify.create({ type: 'info', message: 'No funds to withdraw.' })
    } else if (totalSats <= 1000n) {
      Notify.create({
        type: 'info',
        message: `Contract has only ${totalSats} sats (${(Number(totalSats) / 1e8).toFixed(8)} BCH), which is less than the withdrawal fee.`,
      })
    } else {
      // 5. Withdraw all funds to admin
      Notify.create({
        type: 'info',
        message: `Processing withdrawal of ${(Number(totalSats - 1000n) / 1e8).toFixed(8)} BCH...`,
      })

      // Use the admin wallet address - CashScript will handle the conversion
      const adminWalletAddress = userWallet.getAddress()

      await roomCreateContract.functions
        .withdraw()
        .to(adminWalletAddress, totalSats - 1000n)
        .withHardcodedFee(1000n)
        .withoutChange()
        .send()
      Notify.create({
        type: 'positive',
        message: `Funds withdrawn to your wallet: ${(Number(totalSats - 1000n) / 1e8).toFixed(8)} BCH`,
      })
    }

    // 6. Delete the room via backend
    await axios.delete(`/api/rooms/${roomId}/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    Notify.create({ type: 'positive', message: 'Room deleted successfully' })
    router.push('/home')
  } catch (err) {
    console.error('Withdraw/Delete failed:', err)
    Notify.create({ type: 'negative', message: 'Failed to withdraw or delete room.' })
  }
}

function confirmDelete() {
  if (!window.confirm('Are you sure you want to delete this room? This cannot be undone.')) return
  withdrawAndDeleteRoom()
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
  loadContractAndBalance()
  connectWebSocket()
})

// Add a helper to generate a temporary ID for pending messages
function generateTempId() {
  return 'temp-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9)
}

// Update sendMessage to add a pending message
async function sendMessage() {
  const text = newMsg.value.trim()
  if (!text || !socket.value || socket.value.readyState !== WebSocket.OPEN) return

  // 1. Add the message to the UI immediately with pending: true and a tempId
  const tempId = generateTempId()
  messages.value.push({
    id: tempId,
    content: text,
    senderId: meId.value,
    senderName: meName.value,
    timestamp: new Date().toISOString(),
    pending: true,
  })
  scrollToBottom()

  // 2. Send the message via WebSocket, including the message fee if needed
  // If your backend expects the fee in the payload, include it:
  // socket.value.send(JSON.stringify({ message: text, fee: messageFee.value }))
  // If not, just send the message as before:
  socket.value.send(JSON.stringify({ message: text }))

  newMsg.value = ''
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

// Balance functionality
async function loadContractAndBalance() {
  try {
    isRefreshingBalance.value = true
    const token = localStorage.getItem('access')
    if (!token) throw new Error('Missing access token')
    // Fetch user profile from backend
    const { data: profile } = await axios.get('/api/profile/', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const username = profile.username
    const userId = profile.id
    console.log('UserWalletService args:', username, userId)

    // 1) new service instance
    walletSvc = new UserWalletService(username, userId)

    // 2) read address & balance
    balance.value = await walletSvc.getBalance()
  } catch (loadError) {
    console.error(loadError)
    Notify.create({
      type: 'negative',
      message: 'Failed to load wallet balance',
    })
    balance.value = '0.00000'
  } finally {
    isRefreshingBalance.value = false
  }
}

async function refreshBalance() {
  if (!isRefreshingBalance.value) {
    await loadContractAndBalance()
  }
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

.balance-display {
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 16px;
  background-color: rgba(0, 150, 136, 0.1);
  transition: background-color 0.2s;

  &:hover {
    background-color: rgba(0, 150, 136, 0.2);
  }
}

.rotate-360 {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.msg-side-spinner {
  display: flex;
  align-items: center;
  height: 100%;
}
</style>
