import { Dark } from 'quasar'

class DarkModeService {
  constructor() {
    this.isDark = false
    this.init()
  }

  init() {
    // Load saved preference from localStorage
    const savedMode = localStorage.getItem('chatpay_dark_mode')
    if (savedMode !== null) {
      this.isDark = savedMode === '1'
      this.setDarkMode(this.isDark)
    }
  }

  setDarkMode(isDark) {
    this.isDark = isDark
    Dark.set(isDark)
    localStorage.setItem('chatpay_dark_mode', isDark ? '1' : '0')
  }

  toggle() {
    this.setDarkMode(!this.isDark)
  }

  get isDarkMode() {
    return this.isDark
  }
}

// Create a singleton instance
const darkModeService = new DarkModeService()

export default darkModeService
