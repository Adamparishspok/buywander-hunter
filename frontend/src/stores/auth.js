import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { authClient } from '../lib/auth-client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = computed(() => !!user.value)

  async function login(email, password) {
    const { data, error } = await authClient.signIn.email({
      email,
      password,
    })

    if (error) {
      return {
        success: false,
        message: error.message || 'Login failed',
      }
    }

    if (data?.user) {
      user.value = {
        id: data.user.id,
        email: data.user.email,
        name: data.user.name,
      }
      return { success: true }
    }

    return { success: false, message: 'Login failed' }
  }

  async function signup(email, password, name) {
    const { data, error } = await authClient.signUp.email({
      email,
      password,
      name,
    })

    if (error) {
      return {
        success: false,
        message: error.message || 'Signup failed',
      }
    }

    if (data?.user) {
      user.value = {
        id: data.user.id,
        email: data.user.email,
        name: data.user.name,
      }
      return { success: true }
    }

    return { success: false, message: 'Signup failed' }
  }

  async function logout() {
    await authClient.signOut()
    user.value = null
    return { success: true }
  }

  async function checkAuth() {
    const { data } = await authClient.getSession()

    if (data?.user) {
      user.value = {
        id: data.user.id,
        email: data.user.email,
        name: data.user.name,
      }
      return true
    }

    user.value = null
    return false
  }

  return {
    user,
    isAuthenticated,
    login,
    signup,
    logout,
    checkAuth,
  }
})
