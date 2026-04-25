import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

// Request interceptor: attach session_id
client.interceptors.request.use((config) => {
  const sessionId = localStorage.getItem('session_id')
  if (sessionId) {
    config.params = { ...config.params, session_id: sessionId }
  }
  return config
})

// Response interceptor: unwrap data
client.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || err.message || '请求失败'
    return Promise.reject(new Error(msg))
  },
)

export default client
