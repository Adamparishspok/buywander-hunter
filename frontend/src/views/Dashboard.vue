<template>
  <div
    class="bg-black text-zinc-400 antialiased h-screen w-full flex overflow-hidden selection:bg-indigo-500/30 selection:text-indigo-200"
  >
    <!-- Sidebar -->
    <aside
      class="w-72 bg-zinc-950 border-r border-zinc-800/60 hidden md:flex flex-col justify-between flex-shrink-0 relative z-20"
    >
      <div class="p-6 space-y-8">
        <!-- Brand -->
        <div class="flex items-center gap-3 text-zinc-100">
          <div class="p-2 bg-indigo-500/10 rounded-lg border border-indigo-500/20">
            <ShoppingCart class="text-indigo-400 w-5 h-5" />
          </div>
          <span class="font-medium text-lg tracking-tight">Deal Hunter</span>
        </div>
        <!-- Controls Section -->
        <div class="space-y-4">
          <button
            type="button"
            :disabled="scrapeStatus.running"
            class="w-full group relative flex items-center justify-center gap-2.5 bg-gradient-to-b from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white px-4 py-3 rounded-lg shadow-[0_0_0_1px_rgba(225,29,72,1),0_1px_2px_rgba(0,0,0,0.5),inset_0_1px_1px_rgba(255,255,255,0.15)] transition-all duration-200 active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed"
            @click="startPull"
          >
            <Download class="w-4 h-4" />
            <span class="font-medium text-sm">{{
              scrapeStatus.running ? 'Pulling...' : 'Pull Products'
            }}</span>
          </button>
          <div class="space-y-1 pt-2">
            <router-link
              to="/"
              class="w-full flex items-center gap-3 px-3 py-2 text-sm text-zinc-300 bg-zinc-900/50 rounded-md border border-zinc-800 hover:border-zinc-700 hover:bg-zinc-800 transition-colors"
            >
              <Home class="w-4 h-4 text-zinc-500" />
              Home
            </router-link>
            <router-link
              to="/settings"
              class="w-full flex items-center gap-3 px-3 py-2 text-sm text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50 rounded-md transition-colors"
            >
              <Settings2 class="w-4 h-4 text-zinc-500" />
              Configuration
            </router-link>
          </div>
        </div>
      </div>
      <!-- User/Footer -->
      <div class="p-4 border-t border-zinc-800/60 bg-zinc-950">
        <div class="flex items-center gap-3 px-2">
          <div
            class="w-8 h-8 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center"
          >
            <span class="text-xs font-medium text-zinc-300">{{ userInitials }}</span>
          </div>
          <div class="flex flex-col">
            <span class="text-sm font-medium text-zinc-200">{{ userDisplayName }}</span>
            <span class="text-xs text-zinc-500">Deal Hunter</span>
          </div>
          <button
            class="ml-auto text-zinc-500 hover:text-red-400 transition-colors"
            title="Logout"
            @click="handleLogout"
          >
            <LogOut class="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col h-full bg-black relative overflow-hidden">
      <!-- Top Header -->
      <header class="flex-shrink-0 border-b border-zinc-800/60 bg-black/50 backdrop-blur-xl z-10">
        <div class="max-w-7xl mx-auto px-6 py-6 md:py-8">
          <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <h1 class="text-3xl font-medium text-white tracking-tight mb-1">Scrape History</h1>
              <p class="text-zinc-500 text-sm">View past scraping runs and their results</p>
            </div>
          </div>
        </div>
      </header>

      <!-- Flash Messages -->
      <div v-if="message" class="max-w-7xl mx-auto px-6 mt-4">
        <div
          :class="[
            'p-4 rounded-md',
            messageType === 'error'
              ? 'bg-red-500/10 text-red-400 border border-red-500/20'
              : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
          ]"
        >
          {{ message }}
        </div>
      </div>

      <!-- Scrollable Content Area -->
      <div class="flex-1 overflow-y-auto p-4 md:p-8 custom-scrollbar relative">
        <!-- Loading Overlay -->
        <div
          v-if="scrapeStatus.running"
          class="absolute inset-0 bg-black/80 backdrop-blur-sm z-50 flex flex-col items-center justify-center"
        >
          <div class="flex flex-col items-center gap-4">
            <div class="relative">
              <div
                class="w-16 h-16 border-4 border-zinc-700 border-t-rose-500 rounded-full animate-spin"
              ></div>
            </div>
            <div class="text-center">
              <p class="text-zinc-200 font-medium text-lg mb-1">Pulling Products...</p>
              <p class="text-zinc-500 text-sm">
                {{ scrapeStatus.message || 'This may take 30-60 seconds' }}
              </p>
            </div>
          </div>
        </div>

        <div class="max-w-4xl mx-auto space-y-4">
          <!-- History Entries -->
          <template v-if="history.length > 0">
            <router-link
              v-for="entry in history"
              :key="entry.pull_id"
              :to="`/pull/${entry.pull_id}`"
              class="block border border-zinc-800 rounded-xl bg-zinc-900/20 p-4 md:p-6 hover:border-zinc-700 transition-colors cursor-pointer"
            >
              <div
                class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
              >
                <div class="flex items-start gap-4 flex-1">
                  <!-- Status Icon -->
                  <div class="mt-1">
                    <div
                      v-if="entry.status === 'success'"
                      class="p-2 bg-emerald-500/10 rounded-lg border border-emerald-500/20"
                    >
                      <CheckCircle class="text-emerald-400 w-5 h-5" />
                    </div>
                    <div v-else class="p-2 bg-red-500/10 rounded-lg border border-red-500/20">
                      <XCircle class="text-red-400 w-5 h-5" />
                    </div>
                  </div>
                  <!-- Details -->
                  <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                      <h3 class="text-base font-medium text-zinc-200">
                        {{ formatDate(entry.timestamp) }}
                      </h3>
                      <span
                        :class="[
                          'px-2 py-0.5 rounded text-xs font-medium',
                          entry.status === 'success'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-red-500/10 text-red-400 border border-red-500/20',
                        ]"
                      >
                        {{
                          entry.status === 'success' ? `${entry.items_found} items found` : 'Error'
                        }}
                      </span>
                    </div>
                    <div class="flex flex-col gap-1">
                      <div class="flex items-center gap-2 text-sm text-zinc-500">
                        <CheckCircle class="w-3 h-3" />
                        <span>
                          {{
                            entry.status === 'success'
                              ? 'Pull completed successfully'
                              : 'Pull failed'
                          }}
                        </span>
                      </div>
                      <div
                        v-if="entry.error"
                        class="flex items-center gap-2 text-sm text-red-400 mt-2"
                      >
                        <AlertCircle class="w-3 h-3" />
                        <span>{{ entry.error }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </router-link>
          </template>
          <!-- Empty State -->
          <div
            v-else
            class="text-center py-12 md:py-16 px-6 border border-dashed border-zinc-800 rounded-xl"
          >
            <div
              class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-zinc-900/50 border border-zinc-800 mb-4"
            >
              <History class="w-8 h-8 text-zinc-600" />
            </div>
            <h3 class="text-xl md:text-lg font-medium text-zinc-300 mb-3">No History Yet</h3>
            <p class="text-zinc-500 max-w-md mx-auto text-base md:text-sm">
              Click "Pull Products" to start tracking your scraping history.
            </p>
          </div>
        </div>
        <!-- Bottom spacing -->
        <div class="h-12"></div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api/axios'
import {
  ShoppingCart,
  Download,
  Home,
  Settings2,
  LogOut,
  CheckCircle,
  XCircle,
  AlertCircle,
  History,
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const history = ref([])
const scrapeStatus = ref({ running: false, message: '', items_found: 0, pull_id: null })
const message = ref('')
const messageType = ref('error')
let pollInterval = null

const userDisplayName = computed(() => authStore.user?.display_name || 'User')
const userInitials = computed(() => authStore.user?.initials || 'U')

async function loadHistory() {
  try {
    const response = await api.get('/history')
    if (response.data.success) {
      history.value = response.data.history
    }
  } catch (error) {
    console.error('Failed to load history:', error)
    message.value = 'Error loading history from database'
    messageType.value = 'error'
  }
}

async function startPull() {
  if (scrapeStatus.value.running) return

  try {
    const response = await api.post('/scrape')
    if (response.data.success) {
      scrapeStatus.value.running = true
      pollInterval = setInterval(pollStatus, 2000)
    } else {
      message.value = response.data.message
      messageType.value = 'error'
    }
  } catch (error) {
    console.error('Failed to start pull:', error)
    message.value = error.response?.data?.message || 'Failed to start pull'
    messageType.value = 'error'
  }
}

async function pollStatus() {
  try {
    const response = await api.get('/scrape/status')
    if (response.data.success) {
      const status = response.data.status
      scrapeStatus.value = { ...status }

      if (!status.running) {
        clearInterval(pollInterval)
        pollInterval = null
        await loadHistory()
      }
    }
  } catch (error) {
    console.error('Poll error:', error)
  }
}

async function checkScrapeStatus() {
  try {
    const response = await api.get('/scrape/status')
    if (response.data.success && response.data.status.running) {
      scrapeStatus.value = response.data.status
      pollInterval = setInterval(pollStatus, 2000)
    }
  } catch (error) {
    console.error('Failed to check scrape status:', error)
  }
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })
}

onMounted(() => {
  loadHistory()
  checkScrapeStatus()
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #09090b;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #27272a;
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #3f3f46;
}
</style>
