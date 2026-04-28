import { useState } from 'react'
import { Link } from 'react-router-dom'
import { login } from '../services/api'
import toast from 'react-hot-toast'

const Logo = () => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>

export default function LoginPage() {
  const [u, setU] = useState('')
  const [p, setP] = useState('')
  const [loading, setLoading] = useState(false)

  const handle = async e => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await login({ username: u, password: p })
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      window.location.href = '/chat'
    } catch {
      toast.error('Invalid credentials')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{background:'linear-gradient(160deg,#ecfdf5,#f0fdf4,#f8fafc)'}}>
      <div className="w-full max-w-sm">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl mb-4" style={{background:'linear-gradient(135deg,#047857,#059669,#10b981)'}}>
            <Logo />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Arogya</h1>
          <p className="text-sm text-gray-500 mt-1">Sign in to continue</p>
        </div>
        <form onSubmit={handle} className="space-y-3">
          <input value={u} onChange={e=>setU(e.target.value)} placeholder="Username"
            className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none" required />
          <input type="password" value={p} onChange={e=>setP(e.target.value)} placeholder="Password"
            className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none" required />
          <button disabled={loading} className="w-full py-3 text-white rounded-xl font-semibold text-sm hover:opacity-90 disabled:opacity-50 transition-opacity shadow-lg shadow-emerald-500/20"
            style={{background:'linear-gradient(135deg,#047857,#059669,#10b981)'}}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p className="text-center mt-6 text-sm text-gray-500">
          New here? <Link to="/register" className="text-emerald-600 font-medium">Create account</Link>
        </p>
        <p className="text-center mt-2 text-sm">
          <Link to="/" className="text-gray-400 hover:text-emerald-600">Back to home</Link>
        </p>
      </div>
    </div>
  )
}
