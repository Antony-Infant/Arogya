import axios from 'axios'
const api = axios.create({ baseURL: '/api' })
api.interceptors.request.use(c => {
  const t = localStorage.getItem('access_token')
  if (t) c.headers.Authorization = 'Bearer ' + t
  return c
})
api.interceptors.response.use(r => r, async err => {
  if (err.response?.status === 401 && !err.config._retry) {
    err.config._retry = true
    const rf = localStorage.getItem('refresh_token')
    if (rf) {
      try {
        const { data } = await axios.post('/api/auth/token/refresh/', { refresh: rf })
        localStorage.setItem('access_token', data.access)
        err.config.headers.Authorization = 'Bearer ' + data.access
        return api(err.config)
      } catch { localStorage.clear(); window.location.href = '/login' }
    }
  }
  return Promise.reject(err)
})
export default api
export const login = d => api.post('/auth/token/', d)
export const register = d => api.post('/users/register/', d)
export const listSessions = () => api.get('/chat/sessions/')
export const createSession = () => api.post('/chat/sessions/', {})
export const getSession = id => api.get('/chat/sessions/' + id + '/')
export const sendMessage = (id, b) => api.post('/chat/sessions/' + id + '/send-message/', b)
export const sendVoice = (id, fd) => api.post('/chat/sessions/' + id + '/send-voice/', fd, {headers:{'Content-Type':'multipart/form-data'}})
export const sendImage = (id, fd) => api.post('/chat/sessions/' + id + '/send-image/', fd, {headers:{'Content-Type':'multipart/form-data'}})
export const sendPdf = (id, fd) => api.post('/chat/sessions/' + id + '/send-pdf/', fd, {headers:{'Content-Type':'multipart/form-data'}})
export const submitFeedback = d => api.post('/feedback/submit/', d)
export const downloadPDF = id => api.get('/reports/pdf/' + id + '/', {responseType:'blob'})
