<template>
  <div
    class="bg-black text-zinc-400 antialiased h-screen w-full flex flex-col items-center justify-center relative overflow-hidden selection:bg-indigo-500/30 selection:text-indigo-200"
  >
    <!-- Background Decoration -->
    <div class="absolute inset-0 z-0 flex justify-center">
      <div class="w-full h-full bg-grid opacity-[0.15]"></div>
      <div
        class="absolute top-0 w-full h-px bg-gradient-to-r from-transparent via-zinc-800 to-transparent"
      ></div>
      <div
        class="absolute bottom-0 w-full h-px bg-gradient-to-r from-transparent via-zinc-800 to-transparent"
      ></div>
      <div
        class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none"
      ></div>
    </div>

    <!-- Signup Container -->
    <div class="w-full max-w-sm px-6 relative z-10">
      <!-- Header / Logo -->
      <div class="flex flex-col items-center mb-8 space-y-2">
        <div class="p-3 bg-zinc-900/50 rounded-xl border border-zinc-800 shadow-xl mb-4">
          <ShoppingCart class="text-indigo-400 w-6 h-6" />
        </div>
        <h1 class="text-2xl font-medium text-white tracking-tight">Create account</h1>
        <p class="text-sm text-zinc-500">Sign up to get started</p>
      </div>

      <!-- Flash Messages -->
      <div v-if="message" class="mb-6">
        <div
          :class="[
            'p-3 rounded-lg text-sm text-center',
            messageType === 'error'
              ? 'bg-red-500/10 text-red-400 border border-red-500/20'
              : messageType === 'info'
                ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
          ]"
        >
          {{ message }}
        </div>
      </div>

      <!-- Signup Form -->
      <form
        class="bg-zinc-950/50 backdrop-blur-xl border border-zinc-800/60 rounded-2xl p-6 sm:p-8 shadow-2xl ring-1 ring-white/5"
        @submit.prevent="handleSignup"
      >
        <div class="space-y-4">
          <!-- Name Field (optional) -->
          <div>
            <label for="name" class="block text-sm font-medium text-zinc-300 mb-2"
              >Name (optional)</label
            >
            <input
              id="name"
              v-model="name"
              type="text"
              autocomplete="name"
              class="w-full px-3 py-2 bg-zinc-900/50 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
              placeholder="Enter your name"
            />
          </div>

          <!-- Email Field -->
          <div>
            <label for="email" class="block text-sm font-medium text-zinc-300 mb-2">Email</label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              autocomplete="email"
              class="w-full px-3 py-2 bg-zinc-900/50 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
              placeholder="Enter your email"
            />
          </div>

          <!-- Password Field -->
          <div>
            <label for="password" class="block text-sm font-medium text-zinc-300 mb-2"
              >Password</label
            >
            <input
              id="password"
              v-model="password"
              type="password"
              required
              autocomplete="new-password"
              class="w-full px-3 py-2 bg-zinc-900/50 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
              placeholder="Enter your password"
            />
          </div>

          <!-- Sign Up Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 px-4 rounded-lg shadow-[0_0_20px_-5px_rgba(99,102,241,0.3)] transition-all duration-200 active:scale-[0.98] text-sm disabled:opacity-50"
          >
            <span>{{ loading ? 'Creating account...' : 'Create account' }}</span>
            <ArrowRight class="w-4 h-4" />
          </button>

          <!-- Sign In Link -->
          <div class="text-center">
            <router-link
              to="/login"
              class="text-sm text-zinc-400 hover:text-zinc-200 transition-colors"
            >
              Already have an account? Sign in
            </router-link>
          </div>
        </div>
      </form>

      <!-- Footer -->
      <p class="mt-8 text-center text-xs text-zinc-600">Protected System</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ShoppingCart, ArrowRight } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const name = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const message = ref('')
const messageType = ref('error')

async function handleSignup() {
  loading.value = true
  message.value = ''

  const result = await authStore.signup(email.value, password.value, name.value)

  if (result.success) {
    if (result.requiresVerification) {
      message.value = result.message
      messageType.value = 'info'
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      router.push('/')
    }
  } else {
    message.value = result.message
    messageType.value = 'error'
  }

  loading.value = false
}
</script>

<style scoped>
.bg-grid {
  background-size: 40px 40px;
  background-image:
    linear-gradient(to right, #27272a 1px, transparent 1px),
    linear-gradient(to bottom, #27272a 1px, transparent 1px);
  mask-image: radial-gradient(circle at center, black 40%, transparent 100%);
  -webkit-mask-image: radial-gradient(circle at center, black 40%, transparent 100%);
}
</style>
