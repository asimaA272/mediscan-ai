/**
 * services/api.js
 * Every backend call in the app goes through this file.
 * If the backend URL changes (e.g. after deploying to Railway), update
 * only the .env file — never hardcode URLs in components.
 */
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 60000, // scans can take a while (AI calls + NVIDIA call)
})

// --- Scan pipeline ---
export const uploadScan = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/api/scan', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// --- Pipeline status (for the live agent monitor page) ---
export const getPipelineStatus = () => api.get('/api/pipeline/status')

// --- Chat ---
export const sendChat = (message) => api.post('/api/chat', { message })
export const detectEmotion = (message) =>
  api.get('/api/chat/emotion', { params: { message } })

export default api
