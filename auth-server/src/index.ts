import express from 'express'
import cors from 'cors'
import dotenv from 'dotenv'
import { auth } from './auth'

// Load environment variables
dotenv.config()

const app = express()
const PORT = process.env.PORT || 3001

// Middleware
app.use(
  cors({
    origin: ['http://localhost:5173', 'http://localhost:3000'],
    credentials: true,
  })
)
app.use(express.json())

// Mount Better Auth handlers
app.all('/api/auth/*', async (req, res) => {
  return auth.handler(req, res)
})

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'auth-server' })
})

app.listen(PORT, () => {
  console.log(`🔐 Auth server running on http://localhost:${PORT}`)
})
