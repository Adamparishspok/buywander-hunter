import express from 'express'
import cors from 'cors'
import { toNodeHandler } from 'better-auth/node'
import { auth } from './auth'

const app = express()
const PORT = process.env.PORT || 3001

// CORS middleware
app.use(
  cors({
    origin: ['http://localhost:5173', 'http://localhost:5174', 'http://localhost:5175', 'http://localhost:5176', 'http://localhost:3000'],
    credentials: true,
  })
)

// Mount Better Auth handlers (before express.json)
app.all('/api/auth/*splat', toNodeHandler(auth))

// Other middleware after Better Auth
app.use(express.json())

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'auth-server' })
})

app.listen(PORT, () => {
  console.log(`🔐 Auth server running on http://localhost:${PORT}`)
})
