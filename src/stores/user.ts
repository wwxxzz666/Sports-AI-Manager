import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const nickname = ref('用户')
  const avatar = ref('')
  const isLoggedIn = computed(() => !!token.value)

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('auth_token', newToken)
  }

  function setProfile(name: string, avatarUrl: string) {
    nickname.value = name
    avatar.value = avatarUrl
  }

  function logout() {
    token.value = ''
    nickname.value = '用户'
    avatar.value = ''
    localStorage.removeItem('auth_token')
  }

  function initFromStorage() {
    const savedToken = localStorage.getItem('auth_token')
    if (savedToken) {
      token.value = savedToken
    }
  }

  return {
    token,
    nickname,
    avatar,
    isLoggedIn,
    setToken,
    setProfile,
    logout,
    initFromStorage,
  }
})
