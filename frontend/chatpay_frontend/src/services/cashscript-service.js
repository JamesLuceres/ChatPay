// src/services/cashscript-service.js

import { BCHJS, ECPair } from '@psf/bch-js'
// Pull the UMD globals that the <script> tag injected:
function getCashScript() {
  if (!window.cashscript) {
    throw new Error('CashScript library not loaded')
  }
  return window.cashscript
}
import artifact from '../contracts/UserWallet.json'

export class CashScriptService {
  constructor() {
    this.contract = null
    this.userName = null
    this.accessToken = null
    this.userPubKey = null
  }

  /** (Optional) Compile a CashScript contract from source */
  async compileContract() {
    console.log('Contract compilation would happen here')
    return null
  }

  /** Create a Contract instance from a compiled artifact */
  createContract(artifact, constructorArgs = []) {
    try {
      const { Contract } = getCashScript()
      return new Contract(artifact, constructorArgs)
    } catch (error) {
      console.error('Error creating contract:', error)
      throw error
    }
  }

  /** Retrieve current user data (username & access token) */
  getCurrentUserData() {
    const accessToken = localStorage.getItem('access')
    if (!accessToken) throw new Error('No access token found')
    try {
      const payload = JSON.parse(atob(accessToken.split('.')[1]))
      const username = payload.username || payload.name || 'unknown'
      return { username, accessToken }
    } catch {
      throw new Error('Invalid access token format')
    }
  }

  /** Convert a UTF-8 string to 64-byte Uint8Array */
  stringToBytes64(str) {
    const encoder = new TextEncoder()
    const bytes = encoder.encode(str)
    const bytes64 = new Uint8Array(64)
    bytes64.set(bytes.slice(0, 64))
    return bytes64
  }

  /** Generate a deterministic private key (WIF) and store public key hex */
  generatePrivateKey() {
    try {
      const seed = this.userName + this.accessToken
      let hash = 0
      for (let i = 0; i < seed.length; i++) {
        hash = (hash << 5) - hash + seed.charCodeAt(i)
        hash &= hash
      }
      const seedBytes = new Uint8Array(32)
      for (let i = 0; i < 32; i++) {
        seedBytes[i] = (hash + i) & 0xff
      }
      const kp = ECPair.fromSeed(seedBytes)
      this.userPubKey = kp.publicKey.toString('hex')
      return kp.toWIF()
    } catch {
      // fallback
      const fallback = new Uint8Array(32)
      const s = (this.userName + this.accessToken).padEnd(32, '0')
      for (let i = 0; i < 32; i++) {
        fallback[i] = s.charCodeAt(i % s.length)
      }
      const kp = ECPair.fromSeed(fallback)
      this.userPubKey = kp.publicKey.toString('hex')
      return kp.toWIF()
    }
  }

  /** Instantiate UserWallet contract on Mainnet using HTTP provider */
  async createUserWalletContract() {
    const { username, accessToken } = this.getCurrentUserData()
    this.userName = username
    this.accessToken = accessToken
    const accessBytes64 = this.stringToBytes64(accessToken)

    const bchjs = new BCHJS()
    const { FullStackNetworkProvider, Network, Contract } = getCashScript()
    const provider = new FullStackNetworkProvider(Network.MAINNET, bchjs)

    this.contract = new Contract(artifact, [username, accessBytes64], { provider })
    return this.contract
  }

  /** Instantiate UserWallet contract on Testnet */
  async createUserWalletContractTestnet() {
    const { username, accessToken } = this.getCurrentUserData()
    this.userName = username
    this.accessToken = accessToken
    this.generatePrivateKey()
    const accessBytes64 = this.stringToBytes64(accessToken)

    const bchjs = new BCHJS({
      restURL: 'https://testnet3.fullstack.cash/v5/',
      apiToken: process.env.FULLSTACK_API_TOKEN,
    })
    const { FullStackNetworkProvider, Network, Contract } = getCashScript()
    const provider = new FullStackNetworkProvider(Network.TESTNET, bchjs)

    this.contract = new Contract(artifact, [username, accessBytes64], { provider })
    return this.contract
  }

  /** Get the deployed contract's address */
  getContractAddress() {
    if (!this.contract) throw new Error('Contract not instantiated')
    return this.contract.address
  }

  /** Fetch and sum UTXOs to return BCH balance */
  async fetchBalance() {
    if (!this.contract) throw new Error('Contract not instantiated')
    try {
      const utxos = await this.contract.getUtxos()
      const total = utxos.reduce((sum, u) => sum + Number(u.satoshis), 0)
      return (total / 1e8).toFixed(8)
    } catch {
      return '0.00000000'
    }
  }

  /** Generic contract function caller */
  async createContractTransaction(contract, functionName, functionArgs = [], options = {}) {
    const fn = contract.functions[functionName]
    if (!fn) throw new Error(`Function ${functionName} not found`)
    return await fn(...functionArgs).to(options)
  }

  /** Build a transfer transaction */
  async createTransferTransaction(toAddress, amount) {
    if (!this.contract) throw new Error('Contract not instantiated')
    const { username, accessToken } = this.getCurrentUserData()
    const accessBytes64 = this.stringToBytes64(accessToken)
    return this.createContractTransaction(this.contract, 'transfer', [username, accessBytes64], {
      [toAddress]: amount,
    })
  }

  /** Transfer the full balance minus a fee reserve */
  async createSimpleTransferTransaction(toAddress) {
    if (!this.contract) throw new Error('Contract not instantiated')
    const utxos = await this.contract.getUtxos()
    if (!utxos.length) throw new Error('No funds')
    const total = utxos.reduce((sum, u) => sum + Number(u.satoshis), 0)
    const amount = Math.max(0, total - 1000)
    if (amount <= 0) throw new Error('Insufficient funds')
    return this.createTransferTransaction(toAddress, amount)
  }

  /** Sign & broadcast a transaction */
  async signAndBroadcast(tx, privateKey) {
    const kp = ECPair.fromWIF(privateKey)
    const signed = tx.sign([kp])
    return signed.send()
  }

  /** Fetch raw contract UTXOs */
  async getContractUtxos() {
    if (!this.contract) throw new Error('Contract not instantiated')
    return this.contract.getUtxos()
  }

  /** Simple credentials validator */
  validateCredentials(username, accessToken) {
    return username === this.userName && accessToken === this.accessToken
  }
}

export const cashScriptService = new CashScriptService()

/** Utility: encode string to Uint8Array */
export function stringToBytes(str) {
  return new TextEncoder().encode(str)
}

/** Utility: decode Uint8Array to string */
export function bytesToString(bytes) {
  return new TextDecoder().decode(bytes)
}
