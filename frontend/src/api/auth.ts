/**
 * Auth API calls.
 */
import apiClient from '@/api/client'
import type { CurrentUser, LoginRequest, TokenResponse } from '@/types'

export const authApi = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login', data)
    return response.data
  },

  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  logout: async (refreshToken: string): Promise<void> => {
    await apiClient.post('/auth/logout', { refresh_token: refreshToken })
  },

  me: async (): Promise<CurrentUser> => {
    const response = await apiClient.get<CurrentUser>('/auth/me')
    return response.data
  },
}
