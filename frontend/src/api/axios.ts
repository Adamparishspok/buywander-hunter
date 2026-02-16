import axios, { type AxiosInstance } from 'axios'
import { authClient } from '../lib/auth-client'

const api: AxiosInstance = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to include auth token from Better Auth
api.interceptors.request.use(
  async (config) => {
    // Get session from Better Auth
    const session = await authClient.getSession()

    if (session?.session?.token) {
      config.headers.Authorization = `Bearer ${session.session.token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Better Auth handles session refresh automatically
      // If we get 401, it means token is truly invalid
    }
    return Promise.reject(error)
  }
)

export default api
