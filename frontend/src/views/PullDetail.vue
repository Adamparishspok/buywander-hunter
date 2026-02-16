<template>
  <div
    class="bg-black text-zinc-400 antialiased h-screen w-full flex overflow-hidden selection:bg-indigo-500/30 selection:text-indigo-200"
  >
    <!-- Sidebar -->
    <aside
      class="w-72 bg-zinc-950 border-r border-zinc-800/60 hidden md:flex flex-col justify-between flex-shrink-0 relative z-20"
    >
      <div class="p-6 space-y-8">
        <div class="flex items-center gap-3 text-zinc-100">
          <div class="p-2 bg-indigo-500/10 rounded-lg border border-indigo-500/20">
            <ShoppingCart class="text-indigo-400 w-5 h-5" />
          </div>
          <span class="font-medium text-lg tracking-tight">Deal Hunter</span>
        </div>
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
              class="w-full flex items-center gap-3 px-3 py-2 text-sm text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50 rounded-md transition-colors"
            >
              <Settings2 class="w-4 h-4 text-zinc-500" />
              Configuration
            </router-link>
          </div>
        </div>
      </div>
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
      <header class="flex-shrink-0 border-b border-zinc-800/60 bg-black/50 backdrop-blur-xl z-10">
        <div class="max-w-7xl mx-auto px-6 py-6 md:py-8">
          <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <div class="flex items-center gap-3 mb-1">
                <button
                  class="text-zinc-500 hover:text-zinc-300 transition-colors"
                  @click="router.back()"
                >
                  <ArrowLeft class="w-5 h-5" />
                </button>
                <h1 class="text-3xl font-medium text-white tracking-tight">{{ pullName }}</h1>
              </div>
              <p class="text-zinc-500 text-sm pl-8">Pull results</p>
            </div>
            <div class="flex items-center gap-4">
              <div class="bg-zinc-900/50 border border-zinc-800 rounded-lg px-4 py-3 min-w-[140px]">
                <span class="block text-xs font-medium text-zinc-500 uppercase tracking-wider mb-1"
                  >Total Items</span
                >
                <span class="text-2xl font-medium text-zinc-100 tracking-tight">{{
                  totalItems
                }}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div class="flex-1 overflow-y-auto p-4 md:p-8 custom-scrollbar">
        <div class="max-w-7xl mx-auto space-y-8">
          <template v-if="deals.length > 0">
            <!-- Filter Bar -->
            <section class="space-y-3">
              <div class="flex flex-col md:flex-row gap-4">
                <div class="relative flex-1 group">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search
                      class="h-4 w-4 text-zinc-500 group-focus-within:text-zinc-300 transition-colors"
                    />
                  </div>
                  <input
                    v-model="searchQuery"
                    type="text"
                    class="block w-full pl-10 pr-3 py-2.5 bg-zinc-900/30 border border-zinc-800 rounded-lg leading-5 text-zinc-200 placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-zinc-600 focus:border-zinc-600 sm:text-sm transition-all shadow-sm"
                    placeholder="Search by title, keyword..."
                  />
                </div>
                <div class="relative min-w-[200px]">
                  <button
                    class="w-full flex items-center justify-between bg-zinc-900/30 border border-zinc-800 rounded-lg px-3 py-2.5 text-sm text-zinc-300 hover:bg-zinc-900/60 hover:border-zinc-700 transition-all"
                    @click="showCategoryDropdown = !showCategoryDropdown"
                  >
                    <span class="flex items-center gap-2">
                      <Filter class="w-4 h-4 text-zinc-500" />
                      <span>{{
                        selectedCategory === 'all' ? 'Interest Category' : selectedCategory
                      }}</span>
                    </span>
                    <ChevronDown class="w-4 h-4 text-zinc-600" />
                  </button>
                  <div
                    v-if="showCategoryDropdown"
                    class="absolute top-full mt-2 w-full bg-zinc-950 border border-zinc-800 rounded-lg shadow-xl z-50 overflow-hidden"
                  >
                    <div class="max-h-60 overflow-y-auto">
                      <button
                        class="w-full text-left px-4 py-2.5 text-sm text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 transition-colors border-b border-zinc-800/50"
                        @click="selectCategory('all')"
                      >
                        All Categories
                      </button>
                      <button
                        v-for="category in categories"
                        :key="category"
                        class="w-full text-left px-4 py-2.5 text-sm text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 transition-colors"
                        @click="selectCategory(category)"
                      >
                        {{ category }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <!-- View Toggle -->
            <section class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <button
                  :class="[
                    'flex items-center gap-2 px-3 py-2 text-sm rounded-lg transition-colors',
                    viewMode === 'list'
                      ? 'bg-zinc-800 text-zinc-200'
                      : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800',
                  ]"
                  @click="viewMode = 'list'"
                >
                  <List class="w-4 h-4" />
                  List
                </button>
                <button
                  :class="[
                    'flex items-center gap-2 px-3 py-2 text-sm rounded-lg transition-colors',
                    viewMode === 'grid'
                      ? 'bg-zinc-800 text-zinc-200'
                      : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800',
                  ]"
                  @click="viewMode = 'grid'"
                >
                  <Grid class="w-4 h-4" />
                  Grid
                </button>
              </div>
              <div class="text-sm text-zinc-500">{{ filteredDeals.length }} products</div>
            </section>

            <!-- List View -->
            <section
              v-if="viewMode === 'list'"
              class="border border-zinc-800 rounded-xl bg-zinc-900/20 overflow-hidden shadow-sm"
            >
              <div class="overflow-x-auto">
                <table class="min-w-full text-left border-collapse">
                  <thead>
                    <tr class="border-b border-zinc-800/80 bg-zinc-900/40">
                      <th
                        class="px-6 py-4 text-xs font-medium uppercase tracking-wider text-zinc-500 w-[80px]"
                      >
                        Image
                      </th>
                      <th
                        class="px-6 py-4 text-xs font-medium uppercase tracking-wider text-zinc-500 w-[140px]"
                      >
                        Category
                      </th>
                      <th
                        class="px-6 py-4 text-xs font-medium uppercase tracking-wider text-zinc-500"
                      >
                        Title
                      </th>
                      <th
                        class="px-6 py-4 text-xs font-medium uppercase tracking-wider text-zinc-500 text-right"
                      >
                        Retail
                      </th>
                      <th
                        class="px-6 py-4 text-xs font-medium uppercase tracking-wider text-zinc-500 text-right"
                      >
                        Bid
                      </th>
                      <th
                        class="px-6 py-4 text-xs font-medium uppercase tracking-wider text-zinc-500 text-right"
                      >
                        Score
                      </th>
                      <th
                        class="px-6 py-4 text-xs font-medium uppercase tracking-wider text-zinc-500 text-right w-[80px]"
                      >
                        Bids
                      </th>
                      <th
                        class="px-6 py-4 text-xs font-medium uppercase tracking-wider text-zinc-500"
                      >
                        Ends At
                      </th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-zinc-800/60 text-sm">
                    <tr
                      v-for="deal in filteredDeals"
                      :key="deal.URL"
                      class="group hover:bg-zinc-800/30 transition-colors"
                    >
                      <td class="px-6 py-4 whitespace-nowrap">
                        <img
                          v-if="deal['Image URL']"
                          :src="deal['Image URL']"
                          :alt="deal.Title"
                          class="w-12 h-12 object-cover rounded-lg border border-zinc-700 bg-zinc-800"
                        />
                        <div
                          v-else
                          class="w-12 h-12 rounded-lg border border-zinc-700 bg-zinc-800 flex items-center justify-center"
                        >
                          <ImageIcon class="w-6 h-6 text-zinc-600" />
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div
                          class="inline-flex items-center px-2 py-1 rounded border border-zinc-700 bg-zinc-800/50 text-xs font-medium text-zinc-300"
                        >
                          {{ deal['Interest Category'] }}
                        </div>
                      </td>
                      <td class="px-6 py-4">
                        <a
                          :href="deal.URL"
                          target="_blank"
                          class="text-zinc-200 font-medium truncate max-w-md group-hover:text-indigo-400 transition-colors hover:underline"
                          :title="deal.Title"
                        >
                          {{ deal.Title }}
                        </a>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-right text-zinc-400 line-through">
                        ${{ deal.Retail }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-right">
                        <span class="text-emerald-400 font-medium">${{ deal['Current Bid'] }}</span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-right">
                        <span v-if="deal['Deal Score']" :class="getScoreClass(deal['Deal Score'])">
                          {{ deal['Deal Score'] }}%
                        </span>
                        <span v-else class="text-zinc-600">-</span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-right text-zinc-500">
                        {{ deal.Bids }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-zinc-400">
                        <div class="flex items-center gap-1.5">
                          <Clock class="w-3 h-3 text-orange-500" />
                          <span class="text-orange-400/90 text-xs">{{ deal['End Date'] }}</span>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div
                class="px-6 py-4 border-t border-zinc-800/80 bg-zinc-900/40 flex items-center justify-between"
              >
                <span class="text-xs text-zinc-500"
                  >Showing {{ filteredDeals.length }} entries</span
                >
              </div>
            </section>

            <!-- Grid View -->
            <div
              v-if="viewMode === 'grid'"
              class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
            >
              <a
                v-for="deal in filteredDeals"
                :key="deal.URL"
                :href="deal.URL"
                target="_blank"
                class="group border border-zinc-800 rounded-xl bg-zinc-900/20 p-4 hover:border-zinc-700 transition-all cursor-pointer"
              >
                <!-- Product Image -->
                <div class="aspect-square mb-3 overflow-hidden rounded-lg bg-zinc-800">
                  <img
                    v-if="deal['Image URL']"
                    :src="deal['Image URL']"
                    :alt="deal.Title"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center">
                    <ImageIcon class="w-12 h-12 text-zinc-600" />
                  </div>
                </div>

                <!-- Product Info -->
                <div class="space-y-2">
                  <div
                    class="inline-flex items-center px-2 py-1 rounded border border-zinc-700 bg-zinc-800/50 text-xs font-medium text-zinc-300"
                  >
                    {{ deal['Interest Category'] }}
                  </div>

                  <h3
                    class="text-sm font-medium text-zinc-200 line-clamp-2 group-hover:text-indigo-400 transition-colors"
                    :title="deal.Title"
                  >
                    {{ deal.Title }}
                  </h3>

                  <div class="flex items-center justify-between">
                    <div class="flex flex-col">
                      <span class="text-lg font-bold text-emerald-400"
                        >${{ deal['Current Bid'] }}</span
                      >
                      <span v-if="deal.Retail" class="text-xs text-zinc-500 line-through"
                        >${{ deal.Retail }}</span
                      >
                    </div>
                    <span v-if="deal['Deal Score']" :class="getScoreClass(deal['Deal Score'])">
                      {{ deal['Deal Score'] }}%
                    </span>
                  </div>

                  <div class="flex items-center justify-between text-xs text-zinc-500">
                    <span>{{ deal.Bids }} bids</span>
                    <div class="flex items-center gap-1">
                      <Clock class="w-3 h-3 text-orange-500" />
                      <span class="text-orange-400/90">{{ deal['End Date'] }}</span>
                    </div>
                  </div>
                </div>
              </a>
            </div>
          </template>

          <!-- Empty State -->
          <div v-else class="text-center py-16 border border-dashed border-zinc-800 rounded-xl">
            <div
              class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-zinc-900/50 border border-zinc-800 mb-4"
            >
              <Inbox class="w-8 h-8 text-zinc-600" />
            </div>
            <h3 class="text-lg font-medium text-zinc-300 mb-2">No Products Found</h3>
            <p class="text-zinc-500 max-w-md mx-auto">
              This pull didn't find any matching products.
            </p>
            <router-link
              to="/"
              class="inline-flex items-center gap-2 mt-6 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors"
            >
              <ArrowLeft class="w-4 h-4" />
              Back to History
            </router-link>
          </div>
        </div>
        <div class="h-12"></div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api/axios'
import {
  ShoppingCart,
  Home,
  Settings2,
  LogOut,
  ArrowLeft,
  Search,
  Filter,
  ChevronDown,
  List,
  Grid,
  Clock,
  ImageIcon,
  Inbox,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const deals = ref([])
const pullName = ref('')
const totalItems = ref(0)
const categories = ref([])
const searchQuery = ref('')
const selectedCategory = ref('all')
const showCategoryDropdown = ref(false)
const viewMode = ref('list')

const userDisplayName = computed(() => authStore.user?.display_name || 'User')
const userInitials = computed(() => authStore.user?.initials || 'U')

const filteredDeals = computed(() => {
  let filtered = deals.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter((deal) => deal.Title?.toLowerCase().includes(query))
  }

  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter((deal) => deal['Interest Category'] === selectedCategory.value)
  }

  return filtered
})

async function loadPullDetails() {
  try {
    const pullId = route.params.pullId
    const response = await api.get(`/pull/${pullId}`)
    if (response.data.success) {
      const pull = response.data.pull
      deals.value = pull.deals || []
      pullName.value = formatDate(pull.pull_name) || pull.pull_id
      totalItems.value = pull.total_items || 0
      categories.value = pull.categories || []
    }
  } catch (error) {
    console.error('Failed to load pull details:', error)
  }
}

function selectCategory(category) {
  selectedCategory.value = category
  showCategoryDropdown.value = false
}

function getScoreClass(score) {
  const scoreNum = parseInt(score)
  if (scoreNum >= 90) {
    return 'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
  } else if (scoreNum >= 70) {
    return 'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
  } else if (scoreNum >= 50) {
    return 'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
  } else {
    return 'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-zinc-800 text-zinc-400 border border-zinc-700'
  }
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

function formatDate(dateString) {
  try {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    })
  } catch {
    return dateString
  }
}

onMounted(() => {
  loadPullDetails()
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

.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
</style>
