import axios, { AxiosInstance } from 'axios'
import { useAuthStore } from '../store/authStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

let apiClient: AxiosInstance

export const initializeAPI = () => {
  apiClient = axios.create({
    baseURL: API_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Add token to requests
  apiClient.interceptors.request.use((config) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  // Handle token refresh on 401
  apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
      if (error.response?.status === 401) {
        const refreshToken = useAuthStore.getState().refreshToken
        if (refreshToken) {
          try {
            // Refresh token logic would go here
            useAuthStore.getState().logout()
          } catch {
            useAuthStore.getState().logout()
          }
        }
      }
      return Promise.reject(error)
    }
  )
}

export const getAPI = () => apiClient

// Auth APIs
export const authAPI = {
  register: (email: string, password: string, firstName: string, lastName: string) =>
    apiClient.post('/auth/register/', { email, password, password2: password, first_name: firstName, last_name: lastName }),
  
  login: (email: string, password: string) =>
    apiClient.post('/auth/login/', { email, password }),
  
  getMe: () =>
    apiClient.get('/auth/users/me/'),
  
  changePassword: (oldPassword: string, newPassword: string) =>
    apiClient.post('/auth/users/change_password/', {
      old_password: oldPassword,
      new_password: newPassword,
      new_password2: newPassword
    }),
}

// Organization APIs
export const organizationAPI = {
  list: () =>
    apiClient.get('/organizations/'),
  
  create: (data: any) =>
    apiClient.post('/organizations/', data),
  
  get: (slug: string) =>
    apiClient.get(`/organizations/${slug}/`),
  
  members: (slug: string) =>
    apiClient.get(`/organizations/${slug}/members/`),
  
  inviteUser: (slug: string, email: string, role: string) =>
    apiClient.post(`/organizations/${slug}/invite_member/`, { email, role }),
  
  removeUser: (slug: string, userId: string) =>
    apiClient.post(`/organizations/${slug}/remove_member/`, { user_id: userId }),
}

// Camera APIs
export const cameraAPI = {
  list: (orgSlug: string) =>
    apiClient.get('/cameras/', { params: { organization: orgSlug } }),
  
  create: (orgSlug: string, data: any) =>
    apiClient.post('/cameras/', data, { params: { organization: orgSlug } }),
  
  get: (id: string) =>
    apiClient.get(`/cameras/${id}/`),
  
  update: (id: string, data: any) =>
    apiClient.patch(`/cameras/${id}/`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/cameras/${id}/`),
  
  testConnection: (data: any) =>
    apiClient.post('/cameras/test_connection/', data),
  
  enable: (id: string) =>
    apiClient.post(`/cameras/${id}/enable/`),
  
  disable: (id: string) =>
    apiClient.post(`/cameras/${id}/disable/`),
  
  healthLogs: (id: string) =>
    apiClient.get(`/cameras/${id}/health_logs/`),
  
  snapshots: (id: string) =>
    apiClient.get(`/cameras/${id}/snapshots/`),
}

// Event APIs
export const eventAPI = {
  list: (orgSlug: string) =>
    apiClient.get('/events/', { params: { organization: orgSlug } }),
  
  unprocessed: () =>
    apiClient.get('/events/unprocessed/'),
  
  markProcessed: (id: string) =>
    apiClient.post(`/events/${id}/mark_processed/`),
}

// Alert APIs
export const alertAPI = {
  list: (orgSlug: string) =>
    apiClient.get('/alerts/', { params: { organization: orgSlug } }),
  
  active: () =>
    apiClient.get('/alerts/active/'),
  
  acknowledge: (id: string) =>
    apiClient.post(`/alerts/${id}/acknowledge/`),
  
  resolve: (id: string) =>
    apiClient.post(`/alerts/${id}/resolve/`),
}

// Rule APIs
export const ruleAPI = {
  list: (orgSlug: string) =>
    apiClient.get('/rules/', { params: { organization: orgSlug } }),
  
  create: (orgSlug: string, data: any) =>
    apiClient.post('/rules/', data, { params: { organization: orgSlug } }),
  
  get: (id: string) =>
    apiClient.get(`/rules/${id}/`),
  
  update: (id: string, data: any) =>
    apiClient.patch(`/rules/${id}/`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/rules/${id}/`),
}

// Analytics APIs
export const analyticsAPI = {
  summary: (orgSlug: string) =>
    apiClient.get('/analytics/summary/', { params: { organization: orgSlug } }),
  
  daily: (cameraId?: string, days?: number) =>
    apiClient.get('/analytics/daily/', {
      params: { camera_id: cameraId, days }
    }),
  
  hourly: (cameraId?: string, hours?: number) =>
    apiClient.get('/analytics/hourly/', {
      params: { camera_id: cameraId, hours }
    }),
}
