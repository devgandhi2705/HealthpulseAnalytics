import axios from 'axios'

/**
 * Central axios instance.
 *
 * Development  : set VITE_API_BASE_URL=http://localhost:8000 in .env
 *                Vite's proxy also handles /api → :8000 as a fallback.
 *
 * Production   : leave VITE_API_BASE_URL empty when the frontend is served
 *                from the same origin as the FastAPI backend (e.g. Docker /
 *                Hugging Face Spaces).  Axios will use relative paths so
 *                requests hit the same host automatically.
 *
 * External API : set VITE_API_BASE_URL=https://api.example.com to point to
 *                a separately deployed backend.
 */
const api = axios.create({
  // Empty string = same-origin (production).  Explicit URL = cross-origin (dev/external).
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
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
