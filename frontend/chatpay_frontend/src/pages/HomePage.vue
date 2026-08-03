<!-- src/pages/HomePage.vue -->
<template>
  <div class="home-page column">
    <!-- Header with Telegram styling -->
    <div class="home-header row items-center q-px-md">
      <!-- Left side - Balance -->
      <div class="header-left">
        <div class="balance-display row items-center" @click="goToDepositPage">
          <q-icon name="mdi-currency-btc" size="20px" color="green" />
          <span class="text-caption text-primary q-ml-xs">{{ balance }} BCH</span>
        </div>
      </div>

      <!-- Center - Logo (absolutely positioned) -->
      <div class="header-center">
        <q-avatar size="45px">
          <img src="~assets/logo/chatpay-logo.png" alt="ChatPay" class="chatpay-logo" />
        </q-avatar>
      </div>

      <!-- Right side - Buttons -->
      <div class="header-right row items-center">
        <q-btn flat round dense icon="mdi-dots-vertical" color="primary">
          <q-menu auto-close :offset="[0, 8]">
            <q-list style="min-width: 180px" class="text-grey-9">
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

    <!-- Floating Create/Join Room Speed Dial -->
    <q-fab
      icon="mdi-message-plus"
      icon-size="120px"
      active-icon="mdi-close"
      direction="left"
      color="primary"
      class="fab-create-room"
    >
      <q-fab-action
        color="primary"
        icon="mdi-message-plus"
        @click="openCreateDialog"
        label="Create Room"
        label-position="right"
      />
      <q-fab-action
        color="secondary"
        icon="mdi-login"
        @click="openJoinDialog"
        label="Join Room"
        label-position="right"
      />
    </q-fab>

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
            <div class="row items-center q-mt-xs" v-if="room.minBalanceRequired > 0">
              <q-icon name="mdi-currency-btc" size="12px" color="green" class="q-mr-xs" />
              <span class="text-caption text-grey-6"> Min: {{ room.minBalanceRequired }} BCH </span>
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
          <q-input
            v-model.number="newRoomMinBalance"
            type="number"
            label="Minimum BCH balance to join"
            placeholder="0.00018"
            suffix="BCH"
            step="0.00001"
            min="0"
            class="q-mt-md"
            @keyup.enter="confirmCreate"
          />
          <div class="text-caption text-grey-6 q-mt-xs">
            Users must have at least this amount of BCH to join this room.
          </div>
          <div class="text-negative q-mt-md">
            <q-icon name="mdi-currency-btc" color="green" size="18px" class="q-mr-xs" />
            Creating a room will automatically deduct <b>0.000037 BCH</b> from your wallet.
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="grey" v-close-popup />
          <q-btn
            flat
            label="Create"
            color="primary"
            :disable="!newRoomName.trim() || !canCreateRoom || creatingRoom"
            :loading="creatingRoom"
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
            :disable="!joinCode.trim() || joiningRoom"
            :loading="joiningRoom"
            @click="confirmJoin"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Notify } from 'quasar'
import UserWalletService from '../services/cashscript-service.js'
import RoomCreateArtifact from '../contracts/RoomCreate.json'
import { Contract, ElectrumNetworkProvider, Network } from 'cashscript'
import { v4 as uuidv4 } from 'uuid'
import { decodeCashAddress } from '@bitauth/libauth'

const router = useRouter()
const search = ref('')
const activeId = ref(null)

// Create dialog state
const createDialog = ref(false)
const newRoomName = ref('')
const newRoomMinBalance = ref(0.00018)
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
      minBalanceRequired: r.min_balance_required || 0.00018,
    }))
  } catch {
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
  newRoomMinBalance.value = 0.00018
  createDialog.value = true
}

const roomFee = 3700n
const fee = 1000n
const totalRequired = roomFee + fee
const canCreateRoom = ref(false)

async function updateCanCreateRoom() {
  try {
    const token = localStorage.getItem('access')
    if (!token) {
      canCreateRoom.value = false
      return
    }
    const { data: profile } = await axios.get('/api/profile/', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const username = profile.username
    const userId = profile.id
    const userWallet = new UserWalletService(username, userId)
    const currentBalance = await userWallet.getBalance()
    canCreateRoom.value = BigInt(Math.floor(parseFloat(currentBalance) * 1e8)) >= totalRequired
  } catch {
    canCreateRoom.value = false
  }
}

watch(createDialog, (val) => {
  if (val) updateCanCreateRoom()
})

const creatingRoom = ref(false)

async function confirmCreate() {
  const name = newRoomName.value.trim()
  if (!name) return

  creatingRoom.value = true
  try {
    const token = localStorage.getItem('access')
    const { data: profile } = await axios.get('/api/profile/', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const username = profile.username
    const userId = profile.id
    const userWallet = new UserWalletService(username, userId)

    // Check balance first
    const currentBalance = await userWallet.getBalance()
    if (BigInt(Math.floor(parseFloat(currentBalance) * 1e8)) < totalRequired) {
      Notify.create({
        type: 'negative',
        message: `Insufficient balance. You have ${currentBalance} BCH, but need ${(Number(totalRequired) / 1e8).toFixed(8)} BCH (room fee + fee)`,
      })
      return
    }

    const roomId = uuidv4()
    const roomIdBytes = new TextEncoder().encode(roomId)
    const payeeAddress = 'bitcoincash:qp5le2vn7hjs73tlgskfdswzy60s908ly5wtll9lm9'
    const payeeLockingBytecode = addressToLockingBytecode(payeeAddress)

    // Get the UserWallet contract address and extract the 32-byte hash256
    const userWalletContractAddress = userWallet.getAddress()
    const decoded = decodeCashAddress(userWalletContractAddress)

    // The UserWallet contract is P2SH32, so we can use the payload directly as adminLockingHash256
    const adminLockingHash256 = decoded.payload

    const provider = new ElectrumNetworkProvider(Network.MAINNET)
    const roomCreateContract = new Contract(
      RoomCreateArtifact,
      [roomIdBytes, payeeLockingBytecode, adminLockingHash256],
      { provider },
    )

    Notify.create({ type: 'info', message: 'Processing room creation payment...' })

    // Send roomFee + fee to the RoomCreate contract
    await userWallet.contract.functions
      .transfer(username, userWallet.userIdBytes)
      .to(roomCreateContract.address, roomFee + fee)
      .withHardcodedFee(500n)
      .send()

    Notify.create({ type: 'info', message: 'Payment sent, waiting for confirmation...' })

    // Wait for the payment to appear in the RoomCreate contract
    let paymentReceived = false
    let attempts = 0
    const minUtxo = roomFee + 1000n // at least enough for payout
    const maxAttempts = 30
    while (!paymentReceived && attempts < maxAttempts) {
      const utxos = await roomCreateContract.getUtxos().catch(() => [])
      paymentReceived = utxos.some((utxo) => BigInt(utxo.satoshis) >= minUtxo)
      if (!paymentReceived) {
        await new Promise((resolve) => setTimeout(resolve, 10000))
        attempts++
      }
    }
    if (!paymentReceived) {
      throw new Error('Payment not received by room creation contract')
    }

    // Now execute the room creation contract to pay the service provider
    Notify.create({ type: 'info', message: 'Payment received, finalizing room creation...' })
    await roomCreateContract.functions
      .pay(roomIdBytes)
      .to(payeeAddress, roomFee)
      .withHardcodedFee(500n)
      .send()

    // Wait a bit for the final transaction to process
    await new Promise((resolve) => setTimeout(resolve, 5000))

    // Create the room in the backend only after successful payment
    const { data: room } = await axios.post(
      '/api/rooms/',
      {
        name,
        id: roomId,
        contract_address: roomCreateContract.address,
        min_balance_required: newRoomMinBalance.value,
      },
      { headers: { Authorization: `Bearer ${token}` } },
    )

    Notify.create({
      type: 'positive',
      message: 'Room created successfully! Payment confirmed.',
    })

    createDialog.value = false
    await Promise.all([loadRooms(), loadContractAndBalance()])
    router.push(`/rooms/${room.id}`)
  } catch (err) {
    let errorMessage = 'Failed to create room.'
    if (err.message.includes('Insufficient balance')) {
      errorMessage += ' Insufficient wallet balance.'
    } else if (err.message.includes('Payment not received')) {
      errorMessage += ' Payment processing failed.'
    } else if (err.message.includes('network')) {
      errorMessage += ' Network connection issue.'
    }
    Notify.create({
      type: 'negative',
      message: errorMessage,
    })
  } finally {
    creatingRoom.value = false
  }
}

function openJoinDialog() {
  joinCode.value = ''
  joinDialog.value = true
}

const joiningRoom = ref(false)

async function confirmJoin() {
  const codeRaw = joinCode.value.trim()
  if (!codeRaw) return

  joiningRoom.value = true
  // Extract just the UUID if they pasted the full URL
  const matches = codeRaw.match(/[0-9A-Fa-f-]{36}/)
  const code = matches ? matches[0] : codeRaw

  try {
    const token = localStorage.getItem('access')

    // 1. Fetch room info using the invite code
    const { data: inviteInfo } = await axios.get(`/api/rooms/invite-info/${code}/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const minRequired = parseFloat(inviteInfo.min_balance_required)

    // 2. Get user balance
    const { data: profile } = await axios.get('/api/profile/', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const username = profile.username
    const userId = profile.id
    const userWallet = new UserWalletService(username, userId)
    const currentBalance = await userWallet.getBalance()

    // 3. Check
    if (currentBalance < minRequired) {
      Notify.create({
        type: 'negative',
        message: `Insufficient balance. You need at least ${minRequired} BCH to join this room. Current balance: ${currentBalance} BCH`,
      })
      return
    }

    // 4. Proceed to join
    const { data } = await axios.post(
      `/api/rooms/join/${code}/`,
      {},
      { headers: { Authorization: `Bearer ${token}` } },
    )

    joinDialog.value = false
    Notify.create({ type: 'positive', message: `Joined "${data.name}"` })
    router.push(`/rooms/${data.id}`)
  } catch (error) {
    if (error.response && error.response.data && error.response.data.error) {
      Notify.create({
        type: 'negative',
        message: error.response.data.error,
      })
    } else {
      Notify.create({ type: 'negative', message: 'Invalid invite code.' })
    }
  } finally {
    joiningRoom.value = false
  }
}

// New balance functionality
const balance = ref('0.00000')
const contractAddress = ref('')
const utxos = ref([])
const accessHex = ref('')
let walletSvc = null

async function loadContractAndBalance() {
  try {
    const token = localStorage.getItem('access')
    if (!token) throw new Error('Missing access token')
    // Fetch user profile from backend
    const { data: profile } = await axios.get('/api/profile/', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const username = profile.username
    const userId = profile.id

    // 1) new service instance
    walletSvc = new UserWalletService(username, userId)

    // 2) read address & balance
    contractAddress.value = walletSvc.getAddress()
    balance.value = await walletSvc.getBalance()

    // 3) fetch on-chain UTXOs
    utxos.value = await walletSvc.getUtxos()

    // 4) show the raw userId bytes in hex
    accessHex.value = walletSvc.getUserIdHex()
  } catch {
    Notify.create({
      type: 'negative',
      message: 'Failed to load wallet contract',
    })
    balance.value = '0.00000'
    contractAddress.value = ''
    utxos.value = []
    accessHex.value = ''
  }
}

onMounted(() => {
  loadMe()
  loadContractAndBalance()
})

// Helper function for address to locking bytecode using @bitauth/libauth
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
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  min-width: 120px; /* Ensures some space for symmetry, adjust as needed */
}

.header-center {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
  display: flex;
  align-items: center;
}

.balance-display {
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 18px;
  background-color: rgba(0, 150, 136, 0.1);
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  width: auto;
  min-width: 0;
  max-width: 180px;
  white-space: nowrap;

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

.header-right {
  justify-content: flex-end;
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

.fab-create-room {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}
</style>
