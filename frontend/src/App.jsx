import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import ChatPage from './pages/ChatPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import HistoryPage from './pages/HistoryPage'
import AboutPage from './pages/AboutPage'

function Auth({children}) {
  return localStorage.getItem('access_token') ? children : <Navigate to="/login" />
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-center" toastOptions={{style:{background:'#0c1f17',color:'#fff',borderRadius:'10px',fontSize:'13px'}}} />
      <Routes>
        <Route path="/" element={<AboutPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/chat" element={<Auth><ChatPage /></Auth>} />
        <Route path="/chat/:sessionId" element={<Auth><ChatPage /></Auth>} />
        <Route path="/history" element={<Auth><HistoryPage /></Auth>} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}
