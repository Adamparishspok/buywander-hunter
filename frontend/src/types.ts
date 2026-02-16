// Type definitions for the application

export interface User {
  id: number
  email: string
  display_name: string
  initials: string
}

export interface AuthResponse {
  success: boolean
  message?: string
  user?: User
  access_token?: string
  token_type?: string
  requiresVerification?: boolean
}

export interface ScrapeHistoryEntry {
  pull_id: string
  timestamp: string
  status: string
  items_found: number
  error?: string | null
}

export interface ScrapeStatus {
  running: boolean
  message: string
  items_found: number
  pull_id: string | null
}

export interface Deal {
  Title: string
  URL: string
  'Image URL'?: string | null
  'Current Bid': number
  Retail?: number | null
  'Deal Score'?: number | null
  Bids: number
  'End Date': string
  'Interest Category': string
}

export interface PullDetail {
  pull_id: string
  pull_name: string
  deals: Deal[]
  total_items: number
  categories: string[]
}

export interface Settings {
  interests: Record<string, string[]>
  schedule: {
    enabled: boolean
  }
}

export interface APIResponse<T = any> {
  success: boolean
  message?: string
  data?: T
  error?: string
}
