/**
 * Authentication State Management with Zustand
 */
import { create } from 'zustand'
import { authApi, User } from '@/lib/auth'

interface AuthState {
  user: User | null
  isLoading: boolean
  error: string | null
  isAuthenticated: boolean

  // Actions
  setUser: (user: User | null) => void
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  fetchCurrentUser: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: false,
  error: null,
  isAuthenticated: false,

  setUser: (user) => set({ user, isAuthenticated: !!user }),

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      await authApi.login({ username: email, password })
      const user = await authApi.getCurrentUser()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'ログインに失敗しました',
        isLoading: false,
      })
      throw error
    }
  },

  logout: async () => {
    set({ isLoading: true, error: null })
    try {
      await authApi.logout()
      set({ user: null, isAuthenticated: false, isLoading: false })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'ログアウトに失敗しました',
        isLoading: false,
      })
      throw error
    }
  },

  fetchCurrentUser: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ user: null, isAuthenticated: false })
      return
    }

    set({ isLoading: true, error: null })
    try {
      const user = await authApi.getCurrentUser()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch (error: any) {
      localStorage.removeItem('access_token')
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      })
    }
  },

  clearError: () => set({ error: null }),
}))
