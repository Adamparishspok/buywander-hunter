import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Ref, ComputedRef } from 'vue'
import { authClient } from '../lib/auth-client'

interface LoginResult {
  success: boolean
  message?: string
  requiresVerification?: boolean
}

export const useAuthStore = defineStore('auth', () => {
  // Use Better Auth's session management
  const session = authClient.useSession()

  const user: ComputedRef<any> = computed(() => session.data.value?.user || null)
  const isAuthenticated: ComputedRef<boolean> = computed(() => !!session.data.value?.session)

  async function login(email: string, password: string): Promise<LoginResult> {
    try {
      const result = await authClient.signIn.email({
        email,
        password,
      })

      if (result.error) {
        return {
          success: false,
          message: result.error.message || 'Login failed',
        }
      }

      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        message: error.message || 'Login failed',
      }
    }
  }

  async function signup(email: string, password: string, name?: string): Promise<LoginResult> {
    try {
      const result = await authClient.signUp.email({
        email,
        password,
        name: name || email.split('@')[0],
      })

      if (result.error) {
        return {
          success: false,
          message: result.error.message || 'Signup failed',
        }
      }

      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        message: error.message || 'Signup failed',
      }
    }
  }

  async function logout(): Promise<LoginResult> {
    try {
      await authClient.signOut()
      return { success: true }
    } catch (error: any) {
      return { success: false, message: 'Logout failed' }
    }
  }

  async function checkAuth(): Promise<boolean> {
    // Better Auth automatically manages session state
    // Just return whether we have an active session
    return !!session.data.value?.session
  }

  return {
    user,
    isAuthenticated,
    session,
    login,
    signup,
    logout,
    checkAuth,
  }
})
