import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { register } from '../services/api'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const [f, setF] = useState({ username:'', email:'', password:'', password2:'' })
  const [loading, setLoading] = useState(false)
  const nav = useNavigate()
  const s = k => e => setF({...f, [k]: e.target.value})

  const handle = async e => {
    e.preventDefault()
    if (f.password !== f.password2) return toast.error('Passwords do not match')
    setLoading(true)
    try {
      await register(f)
      toast.success('Account created')
      nav('/login')
    } catch(err) {
      toast.error(err.response?.data ? Object.values(err.response.data).flat()[0] : 'Failed')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{background:'linear-gradient(160deg,#ecfdf5,#f0fdf4,#f8fafc)'}}>
      <div className="w-full max-w-sm">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl mb-4" style={{background:'linear-gradient(135deg,#047857,#059669,#10b981)'}}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Join Arogya</h1>
        </div>
        <form onSubmit={handle} className="space-y-3">
          <input value={f.username} onChange={s('username')} placeholder="Username" className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 outline-none" required />
          <input type="email" value={f.email} onChange={s('email')} placeholder="Email" className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 outline-none" required />
          <input type="password" value={f.password} onChange={s('password')} placeholder="Password (8+)" className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 outline-none" required minLength={8} />
          <input type="password" value={f.password2} onChange={s('password2')} placeholder="Confirm password" className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 outline-none" required />
          <button disabled={loading} className="w-full py-3 text-white rounded-xl font-semibold text-sm hover:opacity-90 disabled:opacity-50 shadow-lg shadow-emerald-500/20"
            style={{background:'linear-gradient(135deg,#047857,#059669,#10b981)'}}>
            {loading ? 'Creating...' : 'Create Account'}
          </button>
        </form>
        <p className="text-center mt-6 text-sm text-gray-500">Have account? <Link to="/login" className="text-emerald-600 font-medium">Sign in</Link></p>
      </div>
    </div>
  )
}
