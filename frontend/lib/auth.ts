/**
 * Authentication API Functions
 */
import apiClient from './api'

export interface LoginCredentials {
  username: string  // FastAPI-Users uses 'username' field for email
  password: string
}

export interface RegisterData {
  email: string
  password: string
  full_name?: string
}

export interface User {
  id: number
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  is_verified: boolean
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export const authApi = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await apiClient.post<AuthResponse>('/auth/jwt/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    // Store token
    localStorage.setItem('access_token', response.data.access_token)
    return response.data
  },

  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', data)
    return response.data
  },

  async logout(): Promise<void> {
    await apiClient.post('/auth/jwt/logout')
    localStorage.removeItem('access_token')
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/users/me')
    return response.data
  },

  async updateUser(data: Partial<User>): Promise<User> {
    const response = await apiClient.patch<User>('/users/me', data)
    return response.data
  },
}
