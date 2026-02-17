import { createAuthClient } from 'better-auth/vue'

export const authClient = createAuthClient({
  baseURL: '', // Empty string means same origin - Vite proxy handles routing
})
