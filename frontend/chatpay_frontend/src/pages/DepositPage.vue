<template>
  <div class="deposit-page-wrapper">
    <!-- Header -->
    <div class="deposit-header row items-center q-px-md">
      <q-btn flat round icon="arrow_back" @click="goBack" />
      <span class="text-h6 q-ml-sm">Deposit BCH</span>
    </div>

    <!-- Deposit Content -->
    <q-scroll-area class="deposit-content">
      <!-- Balance Card -->
      <div
        class="balance-card q-pa-lg row items-center justify-between shadow-2"
        style="
          background: linear-gradient(90deg, #f5f8fa 60%, #e0f7fa 100%);
          border-radius: 16px;
          margin-bottom: 24px;
        "
      >
        <div class="row items-center">
          <q-icon
            name="mdi-currency-btc"
            :style="{ color: '#0AC18E' }"
            size="40px"
            class="q-mr-md"
          />
          <div>
            <div class="text-caption text-grey-6">Your Balance</div>
            <div class="text-h3 text-weight-bold text-primary" style="letter-spacing: 1px">
              {{ balance }} BCH
            </div>
          </div>
        </div>
        <q-btn
          color="primary"
          icon="mdi-cash-minus"
          label="Withdraw"
          @click="withdrawDialog = true"
          size="lg"
          class="q-ml-lg"
          style="border-radius: 8px; font-weight: 600"
        />
      </div>

      <!-- Withdraw Dialog -->
      <q-dialog v-model="withdrawDialog">
        <q-card style="width: 370px; border-radius: 16px">
          <q-card-section>
            <div class="text-h6">Withdraw BCH</div>
          </q-card-section>
          <q-card-section>
            <q-input
              v-model="withdrawAddress"
              label="Recipient BCH Address"
              placeholder="e.g. paytaca..."
              :rules="[(val) => !!val || 'Address required']"
              autofocus
              outlined
              dense
            />
            <div class="text-caption text-grey-6 q-mt-xs q-mb-md">
              Paste your BCH address
            </div>
            <q-input
              v-model="withdrawAmount"
              label="Amount (BCH)"
              type="number"
              min="0"
              :rules="[
                (val) => !!val || 'Amount required',
                (val) => parseFloat(val) > 0 || 'Must be > 0',
              ]"
              outlined
              dense
              class="q-mt-md"
            >
              <template #append>
                <q-btn flat size="sm" label="Max" @click="withdrawAmount = balance.toString()" />
              </template>
            </q-input>
            <div class="row items-center q-mt-sm">
              <q-icon name="mdi-information-outline" size="16px" color="grey" class="q-mr-xs" />
              <span class="text-caption text-grey-7"
                >Available: <b>{{ balance }}</b> BCH &nbsp;|&nbsp; Fee: <b>0.00001</b> BCH</span
              >
            </div>
          </q-card-section>
          <q-card-actions align="right" class="q-pb-md q-pr-md">
            <q-btn flat label="Cancel" color="grey" v-close-popup />
            <q-btn
              unelevated
              icon="mdi-cash-minus"
              label="Withdraw"
              color="primary"
              :disable="!withdrawAddress || !withdrawAmount || parseFloat(withdrawAmount) <= 0"
              @click="handleWithdraw"
              style="border-radius: 8px; font-weight: 600"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <!-- Deposit Address -->
      <div class="deposit-address-section q-pa-md">
        <div class="text-body1 q-mb-sm">Your Deposit Address</div>
        <div class="address-display row items-center justify-between q-pa-sm">
          <span class="text-caption text-grey-8 ellipsis">
            {{ contractAddress }}
          </span>
          <q-btn flat round icon="mdi-content-copy" @click="copyAddress" class="text-grey-6" />
        </div>
        <qrcode-vue :value="contractAddress" :size="200" level="H" class="q-my-md" />
        <div class="text-caption text-grey-6 q-mt-sm">Scan or copy this address to receive BCH</div>
      </div>

      <!-- Deposit Instructions -->
      <div class="instructions-section q-pa-md">
        <div class="text-body1 q-mb-md">Deposit Instructions</div>

        <div class="instruction-item row items-start q-mb-sm">
          <q-icon name="mdi-numeric-1-circle" size="sm" color="primary" class="q-mr-sm" />
          <div class="text-caption">Send only Bitcoin Cash (BCH) to this address</div>
        </div>

        <div class="instruction-item row items-start q-mb-sm">
          <q-icon name="mdi-numeric-2-circle" size="sm" color="primary" class="q-mr-sm" />
          <div class="text-caption">Deposits will be credited after 1 confirmation</div>
        </div>

        <div class="instruction-item row items-start">
          <q-icon name="mdi-numeric-3-circle" size="sm" color="primary" class="q-mr-sm" />
          <div class="text-caption">Minimum deposit: 0.00001 BCH</div>
        </div>
      </div>
    </q-scroll-area>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Notify } from 'quasar'
import QrcodeVue from 'qrcode.vue'
import UserWalletService from '../services/cashscript-service.js'
import axios from 'axios'
import { decodeCashAddress } from '@bitauth/libauth'

const router = useRouter()
const contractAddress = ref('')
const balance = ref('0.00000')
const utxos = ref([])
const accessHex = ref('')
const withdrawDialog = ref(false)
const withdrawAddress = ref('')
const withdrawAmount = ref('')

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
  }
}

function copyAddress() {
  navigator.clipboard.writeText(contractAddress.value)
  Notify.create({ message: 'Address copied!', color: 'positive' })
}

function goBack() {
  router.back()
}

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

async function handleWithdraw() {
  if (!withdrawAddress.value || !withdrawAmount.value || parseFloat(withdrawAmount.value) <= 0) {
    Notify.create({ type: 'negative', message: 'Please enter a valid address and amount.' })
    return
  }
  try {
    // Validate address
    addressToLockingBytecode(withdrawAddress.value)
    // Convert BCH to satoshis
    const sats = Math.floor(parseFloat(withdrawAmount.value) * 1e8)
    if (sats <= 0) throw new Error('Amount must be greater than 0')
    // Check balance
    const currentBalance = await walletSvc.getBalance()
    if (parseFloat(withdrawAmount.value) > currentBalance) {
      throw new Error('Insufficient balance')
    }
    // Call the UserWallet contract's transfer function
    const txResult = await walletSvc.contract.functions
      .transfer(walletSvc.username, walletSvc.userIdBytes)
      .to(withdrawAddress.value, BigInt(sats))
      .withHardcodedFee(1000n)
      .send()
    Notify.create({
      type: 'positive',
      message: `Withdrawal sent! TXID: ${txResult.txid || 'unknown'}`,
    })
    withdrawDialog.value = false
    await loadContractAndBalance()
  } catch {
    Notify.create({
      type: 'negative',
      message: 'Withdrawal failed',
    })
  }
}

onMounted(loadContractAndBalance)
</script>

<style lang="scss">
:root,
body {
  font-family: 'Inter', 'Roboto', 'Segoe UI', Arial, system-ui, sans-serif;
  font-size: 16px;
  color: #222;
}
</style>

<style scoped lang="scss">
.deposit-page-wrapper {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f8fa;
}

.deposit-header {
  flex: 0 0 auto;
  height: 56px;
  background-color: white;
  border-bottom: 1px solid #e0e0e0;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.deposit-content {
  flex: 1 1 auto;
}

.balance-card {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.07);
  margin: 24px 0 0 0;
  font-size: 18px;
}

.text-h3,
.text-h4 {
  font-family: inherit;
  font-weight: 700;
  font-size: 2.2rem;
  line-height: 1.1;
}

.text-h6 {
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: 0.2px;
}

.text-caption {
  font-size: 14px;
  color: #6b7280;
  font-family: inherit;
}

.q-btn {
  font-family: inherit;
  font-size: 1rem;
  font-weight: 500;
}

.q-input__control,
.q-field__control {
  font-family: inherit;
  font-size: 1rem;
}

.instructions-section,
.deposit-address-section {
  font-size: 16px;
  font-family: inherit;
}

.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.deposit-address-section {
  background-color: white;
  margin: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.address-display {
  background-color: #f5f5f5;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.transactions-section {
  background-color: white;
  margin: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.transaction-item {
  border-bottom: 1px solid #f0f0f0;
  &:last-child {
    border-bottom: none;
  }
}

.contract-address {
  margin-top: 8px;
}

.user-pubkey {
  margin-top: 4px;
}
</style>
