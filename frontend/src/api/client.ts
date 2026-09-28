/**
 * Axios HTTP client with JWT interceptors.
 * Automatically attaches access token and handles 401 refresh.
 */
import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'

const BASE_URL = '/api/v1'

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000,
})

// ── Request Interceptor — attach access token ─────────────────
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// ── Response Interceptor — handle token expiry ────────────────
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: string) => void
  reject: (reason: unknown) => void
}> = []

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((p) => {
    if (error) p.reject(error)
    else p.resolve(token!)
  })
  failedQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !original._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            original.headers.Authorization = `Bearer ${token}`
            return apiClient(original)
          })
          .catch((err) => Promise.reject(err))
      }

      original._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        processQueue(error, null)
        isRefreshing = false
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        const response = await axios.post(`${BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })
        const { access_token, refresh_token: newRefresh } = response.data
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', newRefresh)
        apiClient.defaults.headers.common.Authorization = `Bearer ${access_token}`
        processQueue(null, access_token)
        original.headers.Authorization = `Bearer ${access_token}`
        return apiClient(original)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  },
)

export default apiClient
