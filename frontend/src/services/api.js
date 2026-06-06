import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
  timeout: 15000,
})

// Only attach Content-Type for requests that carry a JSON body.
api.interceptors.request.use((config) => {
  if (['post', 'put', 'patch'].includes(config.method?.toLowerCase())) {
    config.headers['Content-Type'] = 'application/json'
  }
  return config
})

// Unwrap .data so callers receive the payload directly.
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const detail =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'Unexpected error'
    return Promise.reject(new Error(detail))
  },
)

export default api
