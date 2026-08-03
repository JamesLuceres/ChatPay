// src/services/cashscript-service.js
import { ElectrumNetworkProvider, Network, Contract } from 'cashscript'
import artifact from '../contracts/UserWallet.json'

export default class UserWalletService {
  /**
   * @param {string} username      – the userName constructor arg
   * @param {string|number} userId – the userId, to be converted to bytes
   */
  constructor(username, userId) {
    this.username = username
    this.userId = userId

    // 1) set up the provider
    this.provider = new ElectrumNetworkProvider(Network.MAINNET)

    // 2) turn the userId into bytes (as string)
    this.userIdBytes = UserWalletService.userIdToBytes(userId)

    // 3) instantiate your UserWallet contract
    this.contract = new Contract(artifact, [this.username, this.userIdBytes], {
      provider: this.provider,
    })
  }

  /** Helper: convert userId to bytes (Uint8Array) */
  static userIdToBytes(userId) {
    // Convert to string, then to UTF-8 bytes
    return new TextEncoder().encode(String(userId))
  }

  /** On-chain contract address */
  getAddress() {
    return this.contract.address
  }

  /** All UTXOs held by your contract */
  async getUtxos() {
    return this.contract.getUtxos()
  }

  /** BCH balance (in BCH units, not satoshis) */
  async getBalance() {
    const utxos = await this.contract.getUtxos()
    const sats = utxos.reduce((sum, u) => sum + Number(u.satoshis), 0)
    return sats / 1e8
  }

  /** If you need to display your userId bytes as hex */
  getUserIdHex() {
    return Buffer.from(this.userIdBytes).toString('hex')
  }
}
