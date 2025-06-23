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
      <div class="balance-card q-pa-md">
        <div class="text-caption text-grey-6">Your Balance</div>
        <div class="text-h4 text-primary">{{ balance }} BCH</div>
      </div>

      <!-- Deposit Address -->
      <div class="deposit-address-section q-pa-md">
        <div class="text-body1 q-mb-sm">Your Deposit Address</div>

        <div class="address-display row items-center justify-between q-pa-sm">
          <span class="text-caption text-grey-8 ellipsis">{{ contractAddress }}</span>
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

      <!-- Recent Transactions -->
      <div class="transactions-section q-pa-md" v-if="utxos.length > 0">
        <div class="text-body1 q-mb-md">UTXOs</div>

        <q-list bordered separator>
          <q-item v-for="utxo in utxos" :key="utxo.tx_hash + utxo.tx_pos" class="transaction-item">
            <q-item-section>
              <q-item-label
                >{{ utxo.tx_hash }}: {{ (utxo.value / 1e8).toFixed(8) }} BCH</q-item-label
              >
            </q-item-section>
          </q-item>
        </q-list>
      </div>

      <!-- New fields -->
      <div class="contract-address text-caption text-grey-7 q-mt-sm">
        Address: {{ contractAddress }}
      </div>
      <div class="user-pubkey text-caption text-grey-7 q-mt-sm">PubKey: {{ userPubKey }}</div>
    </q-scroll-area>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Notify } from 'quasar'
import QrcodeVue from 'qrcode.vue'
import { cashScriptService } from '../services/cashscript-service.js'

const router = useRouter()
const contractAddress = ref('')
const balance = ref('0.00000')
const utxos = ref([])
const userPubKey = ref('')

const loadContractAndBalance = async () => {
  try {
    await cashScriptService.createUserWalletContract()
    contractAddress.value = cashScriptService.getContractAddress()
    balance.value = await cashScriptService.fetchBalance()
    userPubKey.value = cashScriptService.userPubKey
    fetchUtxos()
  } catch (error) {
    console.error('Error creating contract:', error)
    Notify.create({ message: 'Failed to create contract address', color: 'negative' })
  }
}

const fetchUtxos = async () => {
  if (!contractAddress.value) return
  try {
    const address = contractAddress.value.replace('bitcoincash:', '')
    const apiUrl = `https://api.blockchair.com/bitcoin-cash/dashboards/address/${address}`
    const res = await fetch(apiUrl)

    if (res.status === 430) {
      utxos.value = []
      Notify.create({
        message: 'No UTXOs yet. Send BCH to this address and click "Refresh" after a few minutes.',
        color: 'warning',
        timeout: 0,
        multiLine: true,
        style: 'min-height: 60px;',
        actions: [
          { label: 'Refresh', color: 'primary', handler: () => fetchUtxos() },
          { label: 'Dismiss', color: 'grey', handler: () => {} },
        ],
      })
      return
    }

    if (!res.ok) {
      Notify.create({
        message: `Failed to fetch UTXOs (HTTP ${res.status})`,
        color: 'negative',
      })
      return
    }

    const data = await res.json()
    if (data && data.data && data.data[address] && data.data[address].utxo) {
      utxos.value = data.data[address].utxo
    } else {
      utxos.value = []
      Notify.create({
        message: 'No UTXO data found in response',
        color: 'warning',
        timeout: 0,
        multiLine: true,
        style: 'min-height: 60px;',
        actions: [
          { label: 'Refresh', color: 'primary', handler: () => fetchUtxos() },
          { label: 'Dismiss', color: 'grey', handler: () => {} },
        ],
      })
    }
  } catch (error) {
    console.error('Error fetching UTXOs:', error)
    Notify.create({
      message: 'Failed to fetch UTXOs',
      color: 'negative',
    })
  }
}

const copyAddress = () => {
  navigator.clipboard.writeText(contractAddress.value)
  Notify.create({ message: 'Address copied', color: 'positive' })
}

const goBack = () => router.back()

onMounted(() => {
  loadContractAndBalance()
})
</script>
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
}

.deposit-content {
  flex: 1 1 auto;
}

.balance-card {
  background-color: white;
  margin: 8px 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
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

.instructions-section {
  background-color: white;
  margin: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.instruction-item {
  padding: 4px 0;
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

.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.contract-address {
  margin-top: 8px;
}

.user-pubkey {
  margin-top: 4px;
}
</style>
