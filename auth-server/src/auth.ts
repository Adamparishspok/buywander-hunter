import { betterAuth } from 'better-auth'
import { Pool } from 'pg'

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60, // 1 hour
    updateAge: 60 * 60 * 24, // 1 day
  },
  trustedOrigins: ['http://localhost:5173', 'http://localhost:3000'],
})
