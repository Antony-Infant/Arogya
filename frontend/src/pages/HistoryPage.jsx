import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { listSessions } from '../services/api'
import { ArrowLeft, MessageCircle, Clock } from 'lucide-react'

export default function HistoryPage() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    if (!localStorage.getItem('access_token')) { navigate('/login'); return }
    listSessions().then(({ data }) => { setSessions(data.results || data); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <button onClick={() => navigate('/chat')} className="p-2 hover:bg-gray-200 rounded-full transition-colors"><ArrowLeft size={24} /></button>
          <h1 className="text-2xl font-bold text-gray-800">Chat History</h1>
        </div>
        {loading ? (
          <div className="text-center py-20 text-gray-400">Loading...</div>
        ) : sessions.length === 0 ? (
          <div className="text-center py-20 text-gray-400">No conversations yet. Start chatting!</div>
        ) : (
          <div className="space-y-3">
            {sessions.map(s => (
              <div key={s.id} onClick={() => navigate(`/chat/${s.id}`)}
                className="bg-white p-4 rounded-xl border hover:border-emerald-300 cursor-pointer transition-all hover:shadow-md">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-blue-50 rounded-lg"><MessageCircle size={20} className="text-emerald-500" /></div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-800 truncate">{s.title}</h3>
                    <p className="text-sm text-gray-500 mt-1 truncate">{s.last_message?.content || 'No messages'}</p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                      <span className="flex items-center gap-1"><Clock size={12} />{new Date(s.created_at).toLocaleDateString()}</span>
                      <span>{s.message_count} messages</span>
                      <span className="bg-gray-100 px-2 py-0.5 rounded">{s.channel}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
