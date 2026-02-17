import { betterAuth } from 'better-auth'
import { Pool } from 'pg'
import dotenv from 'dotenv'

// Load environment variables (Railway sets these automatically)
dotenv.config()

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),
  baseURL: process.env.BETTER_AUTH_URL,
  basePath: '/api/auth',
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60, // 1 hour
    updateAge: 60 * 60 * 24, // 1 day
  },
  trustedOrigins: ['http://localhost:5173', 'http://localhost:5174', 'http://localhost:5175', 'http://localhost:5176', 'http://localhost:3000'],
})
