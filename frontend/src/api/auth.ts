import client from './client'
import { AuthResponse, User } from '../types'

export const authAPI = {
  adminLogin: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await client.post('/api/auth/admin/login', { email, password })
    return response.data
  },

  googleLogin: async (idToken: string): Promise<AuthResponse> => {
    const response = await client.post('/api/auth/google', { id_token: idToken })
    return response.data
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await client.get('/api/auth/me')
    return response.data
  },

  logout: async (): Promise<void> => {
    await client.post('/api/auth/logout')
  },
}
