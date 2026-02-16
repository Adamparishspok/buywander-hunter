import { createAuthClient } from 'better-auth/vue'

export const authClient = createAuthClient({
  baseURL: 'http://localhost:3001', // Auth server URL
})

export type Session = typeof authClient.$Infer.Session
