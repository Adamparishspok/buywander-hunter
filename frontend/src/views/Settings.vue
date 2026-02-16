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
          <div class="space-y-1 pt-2">
            <router-link
              to="/"
              class="w-full flex items-center gap-3 px-3 py-2 text-sm text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50 rounded-md transition-colors"
            >
              <Home class="w-4 h-4 text-zinc-500" />
              Home
            </router-link>
            <router-link
              to="/settings"
              class="w-full flex items-center gap-3 px-3 py-2 text-sm text-zinc-300 bg-zinc-900/50 rounded-md border border-zinc-800 hover:border-zinc-700 hover:bg-zinc-800 transition-colors"
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
              <h1 class="text-3xl font-medium text-white tracking-tight mb-1">Configuration</h1>
              <p class="text-zinc-500 text-sm">Manage scraping interests and keywords</p>
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
      <div class="flex-1 overflow-y-auto p-4 md:p-8 custom-scrollbar">
        <div class="max-w-4xl mx-auto space-y-8">
          <!-- Schedule Settings -->
          <section
            class="border border-zinc-800 rounded-xl bg-zinc-900/20 overflow-hidden shadow-sm p-6"
          >
            <h2 class="text-lg font-medium text-zinc-200 mb-4">Scheduled Scans</h2>
            <form class="space-y-4" @submit.prevent="updateSchedule">
              <div class="flex items-center justify-between">
                <div>
                  <label for="nightly_scan" class="block text-sm font-medium text-zinc-200"
                    >Nightly Scan</label
                  >
                  <p class="text-xs text-zinc-500 mt-1">
                    Automatically pull products every day at 6:00 PM
                  </p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    id="nightly_scan"
                    v-model="scheduleEnabled"
                    type="checkbox"
                    class="sr-only peer"
                  />
                  <div
                    class="w-11 h-6 bg-zinc-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"
                  ></div>
                </label>
              </div>

              <div class="pt-2 border-t border-zinc-800/50 mt-4">
                <button
                  type="submit"
                  class="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Save Schedule
                </button>
              </div>
            </form>
          </section>

          <!-- Add New Interest Form -->
          <section
            class="border border-zinc-800 rounded-xl bg-zinc-900/20 overflow-hidden shadow-sm p-6"
          >
            <h2 class="text-lg font-medium text-zinc-200 mb-4">Add New Interest</h2>
            <form class="space-y-4" @submit.prevent="addInterest">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label for="category" class="block text-sm font-medium text-zinc-400 mb-1"
                    >Category Name</label
                  >
                  <input
                    id="category"
                    v-model="newCategory"
                    type="text"
                    required
                    placeholder="e.g. Gaming Consoles"
                    class="block w-full px-3 py-2 bg-zinc-900/50 border border-zinc-800 rounded-lg text-zinc-200 placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label for="keywords" class="block text-sm font-medium text-zinc-400 mb-1"
                    >Keywords (comma separated)</label
                  >
                  <input
                    id="keywords"
                    v-model="newKeywords"
                    type="text"
                    required
                    placeholder="e.g. ps5, xbox, nintendo switch"
                    class="block w-full px-3 py-2 bg-zinc-900/50 border border-zinc-800 rounded-lg text-zinc-200 placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  />
                </div>
              </div>
              <div class="flex justify-end">
                <button
                  type="submit"
                  class="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Add Interest
                </button>
              </div>
            </form>
          </section>

          <!-- Data Management -->
          <section
            class="border border-zinc-800 rounded-xl bg-zinc-900/20 overflow-hidden shadow-sm p-6"
          >
            <h2 class="text-lg font-medium text-zinc-200 mb-4">Data Management</h2>
            <div class="space-y-4">
              <div>
                <h3 class="text-sm font-medium text-zinc-200 mb-2">Automatic Cleanup</h3>
                <p class="text-xs text-zinc-500 mb-4">
                  Old scrape runs are automatically deleted after 2 days to save storage space. This
                  runs daily at 2:00 AM.
                </p>
              </div>
              <div class="pt-2 border-t border-zinc-800/50">
                <button
                  class="bg-orange-600 hover:bg-orange-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  @click="runCleanup"
                >
                  Run Manual Cleanup
                </button>
                <p class="text-xs text-zinc-600 mt-2">
                  Use this to manually clean up old data if needed.
                </p>
              </div>
            </div>
          </section>

          <!-- Existing Interests List -->
          <section class="space-y-4">
            <h2 class="text-lg font-medium text-zinc-200">Current Interests</h2>
            <template v-if="interests && Object.keys(interests).length > 0">
              <div
                v-for="(keywords, category) in interests"
                :key="category"
                class="border border-zinc-800 rounded-xl bg-zinc-900/20 p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 group hover:border-zinc-700 transition-colors"
              >
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-2">
                    <h3 class="text-base font-medium text-zinc-200">{{ category }}</h3>
                    <span
                      class="px-2 py-0.5 rounded text-xs font-medium bg-zinc-800 text-zinc-400 border border-zinc-700"
                    >
                      {{ keywords.length }} keywords
                    </span>
                  </div>
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="keyword in keywords"
                      :key="keyword"
                      class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
                    >
                      {{ keyword }}
                    </span>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    class="p-2 text-zinc-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                    title="Delete Category"
                    @click="deleteInterest(category)"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </template>
            <div v-else class="text-center py-12 border border-dashed border-zinc-800 rounded-xl">
              <p class="text-zinc-500">No interests configured yet. Add one above!</p>
            </div>
          </section>
        </div>
        <!-- Bottom spacing -->
        <div class="h-12"></div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api/axios'
import { ShoppingCart, Home, Settings2, LogOut, Trash2 } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const interests = ref({})
const scheduleEnabled = ref(false)
const newCategory = ref('')
const newKeywords = ref('')
const message = ref('')
const messageType = ref('error')

const userDisplayName = computed(() => authStore.user?.display_name || 'User')
const userInitials = computed(() => authStore.user?.initials || 'U')

async function loadSettings() {
  try {
    const response = await api.get('/settings')
    if (response.data.success) {
      interests.value = response.data.settings.interests || {}
      scheduleEnabled.value = response.data.settings.schedule?.enabled || false
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
    showMessage('Error loading settings', 'error')
  }
}

async function updateSchedule() {
  try {
    const response = await api.post('/settings/schedule', {
      enabled: scheduleEnabled.value,
    })
    if (response.data.success) {
      showMessage(response.data.message, 'success')
    } else {
      showMessage(response.data.message, 'error')
    }
  } catch (error) {
    console.error('Failed to update schedule:', error)
    showMessage('Error saving schedule settings', 'error')
  }
}

async function addInterest() {
  if (!newCategory.value || !newKeywords.value) return

  try {
    const response = await api.post('/settings/interests', {
      category: newCategory.value,
      keywords: newKeywords.value,
    })
    if (response.data.success) {
      showMessage(response.data.message, 'success')
      newCategory.value = ''
      newKeywords.value = ''
      await loadSettings()
    } else {
      showMessage(response.data.message, 'error')
    }
  } catch (error) {
    console.error('Failed to add interest:', error)
    showMessage('Error saving interest', 'error')
  }
}

async function deleteInterest(category) {
  if (!confirm(`Are you sure you want to delete the category "${category}"?`)) return

  try {
    const response = await api.delete(`/settings/interests/${encodeURIComponent(category)}`)
    if (response.data.success) {
      showMessage(response.data.message, 'success')
      await loadSettings()
    } else {
      showMessage(response.data.message, 'error')
    }
  } catch (error) {
    console.error('Failed to delete interest:', error)
    showMessage('Error deleting category', 'error')
  }
}

async function runCleanup() {
  if (
    !confirm(
      'Are you sure you want to run manual cleanup? This will delete all scrape data older than 2 days.'
    )
  )
    return

  try {
    const response = await api.post('/cleanup')
    if (response.data.success) {
      showMessage(response.data.message, 'success')
    } else {
      showMessage(response.data.message, 'error')
    }
  } catch (error) {
    console.error('Failed to run cleanup:', error)
    showMessage('Cleanup failed', 'error')
  }
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

function showMessage(msg, type = 'error') {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

onMounted(() => {
  loadSettings()
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
