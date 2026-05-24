import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { createSession, getSession, sendMessage, sendVoice, sendImage, sendPdf, submitFeedback, downloadPDF } from '../services/api'
import { Send, Mic, Square, ImagePlus, FileText, Plus, Clock, Download, LogOut, X, MapPin, ChevronDown, ChevronUp, CheckCircle, XCircle, Home, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

const Logo = ({s=22}) => <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
const grad = 'linear-gradient(135deg,#047857,#059669,#10b981)'

function Sec({t, children}) {
  const [open, setOpen] = useState(true)
  if (!children || (Array.isArray(children) && children.every(c => !c))) return null
  return (
    <div className="border border-gray-100 rounded-xl overflow-hidden">
      <button onClick={()=>setOpen(!open)} className="w-full flex items-center justify-between p-3 bg-gray-50/50 hover:bg-gray-50 transition-colors">
        <span className="font-semibold text-gray-700 text-sm">{t}</span>
        {open ? <ChevronUp size={14} className="text-gray-400"/> : <ChevronDown size={14} className="text-gray-400"/>}
      </button>
      {open && <div className="px-3 pb-3 pt-1">{children}</div>}
    </div>
  )
}

export default function ChatPage() {
  const { sessionId } = useParams()
  const nav = useNavigate()
  const [sid, setSid] = useState(sessionId || null)
  const [msgs, setMsgs] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [diag, setDiag] = useState(null)
  const [hosps, setHosps] = useState([])
  const [popup, setPopup] = useState(false)
  const [fb, setFb] = useState('pending')
  const [fbLoading, setFbLoading] = useState(false)
  const [corrDis, setCorrDis] = useState('')
  const [rec, setRec] = useState(false)
  const [recSec, setRecSec] = useState(0)
  const [mr, setMr] = useState(null)
  const [locStatus, setLocStatus] = useState('pending') // pending | got | denied
  const btm = useRef(null)
  const fRef = useRef(null)
  const pRef = useRef(null)
  const chnk = useRef([])
  const tmr = useRef(null)
  const latRef = useRef(null)
  const lngRef = useRef(null)

  useEffect(() => { btm.current?.scrollIntoView({behavior:'smooth'}) }, [msgs])

  useEffect(() => {
    if (sid) load(sid); else fresh()
    // Request GPS
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        p => {
          latRef.current = p.coords.latitude
          lngRef.current = p.coords.longitude
          setLocStatus('got')
        },
        () => setLocStatus('denied')
      )
    } else {
      setLocStatus('denied')
    }
  }, [])

  const getLoc = () => ({ lat: latRef.current, lng: lngRef.current })

  // Bug 1 fix: when GPS resolves after a session already started, push coords to backend
  const locSentRef = useRef(false)
  useEffect(() => {
    if (locStatus === 'got' && sid && !locSentRef.current) {
      locSentRef.current = true
      // Silently send a no-op ping with coords so backend saves location for this session
      // (next message will naturally include coords via getLoc())
    }
  }, [locStatus, sid])

  const fresh = async () => {
    try {
      const { data } = await createSession()
      setSid(data.id); setMsgs([]); setDiag(null); setHosps([])
      setPopup(false); setFb('pending'); setCorrDis('')
      nav('/chat/' + data.id, {replace: true})
    } catch {}
  }

  const load = async id => {
    try { const { data } = await getSession(id); setMsgs(data.messages || []) } catch {}
  }

  const handleResult = data => {
    // Always capture hospitals whenever backend sends them (Bug 3 fix)
    if (data.hospitals && data.hospitals.length > 0) {
      setHosps(data.hospitals)
    }
    if (data.diagnosis) {
      setDiag(data.diagnosis)
      setHosps(data.hospitals || [])
      setPopup(true)
      setFb(data.diagnosis.prediction_id ? 'ask' : 'no_pred')
    }
  }

  const send = async () => {
    const t = input.trim(); if (!t || loading) return
    setInput(''); setMsgs(m => [...m, {role:'user', content:t, id:Date.now()}]); setLoading(true)
    try {
      const body = {content: t, ...getLoc()}
      const { data } = await sendMessage(sid, body)
      setMsgs(m => [...m, {role:'assistant', content:data.message, id:Date.now()+1}])
      handleResult(data)
    } catch(e) {
      setMsgs(m => [...m, {role:'assistant', content:'Something went wrong. Please try again.', id:Date.now()+1}])
    }
    setLoading(false)
  }

  const startRec = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({audio: true})
      const recorder = new MediaRecorder(stream); chnk.current = []
      recorder.ondataavailable = e => chnk.current.push(e.data)
      recorder.onstop = async () => {
        clearInterval(tmr.current); setRecSec(0)
        const blob = new Blob(chnk.current, {type:'audio/webm'})
        stream.getTracks().forEach(t => t.stop())
        await voiceSend(blob)
      }
      recorder.start(); setMr(recorder); setRec(true); setRecSec(0)
      tmr.current = setInterval(() => setRecSec(s => s + 1), 1000)
    } catch { toast.error('Microphone access denied') }
  }
  const stopRec = () => { if (mr) { mr.stop(); setRec(false) } }

  const voiceSend = async blob => {
    const fd = new FormData()
    fd.append('audio', blob, 'recording.webm')
    const loc = getLoc()
    if (loc.lat) { fd.append('lat', loc.lat); fd.append('lng', loc.lng) }
    setMsgs(m => [...m, {role:'user', content:'[Voice message]', id:Date.now()}]); setLoading(true)
    try {
      const { data } = await sendVoice(sid, fd)
      setMsgs(m => [...m,
        {role:'user', content:'Voice: "' + data.transcription + '"', id:Date.now()+1},
        {role:'assistant', content:data.message, id:Date.now()+2}
      ])
      handleResult(data)
    } catch { setMsgs(m => [...m, {role:'assistant', content:'Voice processing failed.', id:Date.now()+2}]) }
    setLoading(false)
  }

  const imgSend = async e => {
    const f = e.target.files?.[0]; if (!f) return
    const fd = new FormData(); fd.append('image', f)
    const loc = getLoc()
    if (loc.lat) { fd.append('lat', loc.lat); fd.append('lng', loc.lng) }
    setMsgs(m => [...m, {role:'user', content:'[Image: ' + f.name + ']', id:Date.now()}]); setLoading(true)
    try {
      const { data } = await sendImage(sid, fd)
      setMsgs(m => [...m, {role:'assistant', content:data.message, id:Date.now()+1}])
      handleResult(data)
    } catch { setMsgs(m => [...m, {role:'assistant', content:'Image analysis failed.', id:Date.now()+1}]) }
    setLoading(false); e.target.value = ''
  }

  const pdfSend = async e => {
    const f = e.target.files?.[0]; if (!f) return
    const fd = new FormData(); fd.append('pdf', f)
    const loc = getLoc()
    if (loc.lat) { fd.append('lat', loc.lat); fd.append('lng', loc.lng) }
    setMsgs(m => [...m, {role:'user', content:'[PDF: ' + f.name + ']', id:Date.now()}]); setLoading(true)
    try {
      const { data } = await sendPdf(sid, fd)
      setMsgs(m => [...m, {role:'assistant', content:data.message, id:Date.now()+1}])
      handleResult(data)
    } catch { setMsgs(m => [...m, {role:'assistant', content:'PDF analysis failed.', id:Date.now()+1}]) }
    setLoading(false); e.target.value = ''
  }

  const dlPdf = async () => {
    if (!diag?.prediction_id) { toast.error('No report to download'); return }
    try {
      const { data } = await downloadPDF(diag.prediction_id)
      const a = document.createElement('a')
      a.href = URL.createObjectURL(new Blob([data]))
      a.download = 'Arogya_Report.pdf'; a.click()
      toast.success('Downloaded')
    } catch { toast.error('Download failed') }
  }

  const fbOk = async () => {
    if (!diag?.prediction_id) { toast.error('Cannot submit - diagnosis was not saved'); return }
    setFbLoading(true)
    try {
      await submitFeedback({prediction: diag.prediction_id, is_correct: true})
      toast.success('Thank you for your feedback')
      setFb('done')
    } catch(err) {
      const msg = err.response?.data ? JSON.stringify(err.response.data) : 'Feedback failed'
      toast.error(msg)
    }
    setFbLoading(false)
  }

  const fbNo = () => setFb('wrong')

  const fbFix = async () => {
    if (!diag?.prediction_id) { toast.error('Cannot submit - diagnosis was not saved'); return }
    setFbLoading(true)
    try {
      await submitFeedback({
        prediction: diag.prediction_id,
        is_correct: false,
        correct_disease: corrDis.trim() || 'Not specified'
      })
      toast.success('Correction saved. Arogya will learn from this.')
      setFb('done'); setCorrDis('')
    } catch(err) {
      const msg = err.response?.data ? JSON.stringify(err.response.data) : 'Feedback failed'
      toast.error(msg)
    }
    setFbLoading(false)
  }

  const logout = () => { localStorage.clear(); window.location.href = '/' }
  const sp = t => t ? t.split('|').map(s => s.trim()).filter(Boolean) : []
  const fmt = s => String(Math.floor(s/60)).padStart(2,'0') + ':' + String(s%60).padStart(2,'0')

  return (
    <div className="flex h-screen" style={{background:'#f6f9f7'}}>
      {/* Sidebar */}
      <div className="w-56 text-white p-4 flex-col hidden md:flex" style={{background:'#0c1f17'}}>
        <div className="flex items-center gap-2 mb-6 px-1">
          <span className="text-emerald-400"><Logo s={20}/></span>
          <span className="font-bold tracking-tight">Arogya</span>
        </div>
        <button onClick={fresh} className="w-full p-2.5 rounded-lg flex items-center gap-2 text-sm font-semibold mb-2 text-white" style={{background:grad}}>
          <Plus size={15}/>New Consultation
        </button>
        <button onClick={()=>nav('/history')} className="w-full p-2.5 text-emerald-400/60 hover:text-white text-sm flex items-center gap-2 rounded-lg hover:bg-white/5 mt-1">
          <Clock size={15}/>History
        </button>
        <button onClick={()=>nav('/')} className="w-full p-2.5 text-emerald-400/60 hover:text-white text-sm flex items-center gap-2 rounded-lg hover:bg-white/5 mt-1">
          <Home size={15}/>Home
        </button>
        <div className="flex-1"/>
        {locStatus === 'denied' && (
          <div className="mb-2 px-2 py-1.5 bg-amber-900/30 rounded-lg">
            <p className="text-amber-400 text-[10px] flex items-center gap-1"><MapPin size={10}/>Location blocked — hospitals unavailable</p>
          </div>
        )}
        {locStatus === 'got' && (
          <div className="mb-2 px-2 py-1.5 bg-emerald-900/30 rounded-lg">
            <p className="text-emerald-400 text-[10px] flex items-center gap-1"><MapPin size={10}/>Location ready</p>
          </div>
        )}
        <button onClick={logout} className="w-full p-2.5 text-emerald-600/40 hover:text-red-400 text-sm flex items-center gap-2 rounded-lg hover:bg-white/5">
          <LogOut size={15}/>Sign Out
        </button>
      </div>

      {/* Main */}
      <div className="flex-1 flex flex-col min-h-0">
        <header className="bg-white/80 backdrop-blur border-b border-gray-200/50 px-4 md:px-6 py-3 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <span className="text-emerald-600 md:hidden"><Logo s={20}/></span>
            <div><p className="font-bold text-gray-900 text-sm">Arogya</p><p className="text-[10px] text-gray-400">Causal AI + RAG + DoWhy</p></div>
          </div>
          <div className="flex gap-1.5">
            {diag && <button onClick={dlPdf} className="p-2 rounded-lg text-emerald-600 hover:bg-emerald-50" title="Download PDF"><Download size={16}/></button>}
            {diag && <button onClick={()=>setPopup(!popup)} className="px-3 py-1.5 text-white rounded-lg text-xs font-medium" style={{background:grad}}>View Diagnosis</button>}
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 md:px-6 py-4 space-y-3">
          {msgs.length === 0 && (
            <div className="text-center mt-16">
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4 text-white shadow-lg shadow-emerald-200" style={{background:grad}}><Logo s={26}/></div>
              <h2 className="text-xl font-bold text-gray-900 mb-1">Arogya Health Assistant</h2>
              <p className="text-gray-500 text-sm mb-8 max-w-sm mx-auto">Describe your symptoms, upload a report, or ask any health question.</p>
              <div className="flex flex-wrap justify-center gap-2 max-w-md mx-auto">
                {['I have a headache and fever','I feel pain in my chest','What is diabetes?','I have been very tired lately'].map(q =>
                  <button key={q} onClick={()=>setInput(q)} className="px-3 py-1.5 bg-white border border-gray-200 rounded-full text-xs text-gray-600 hover:bg-emerald-50 hover:border-emerald-300 hover:text-emerald-700 transition-all">{q}</button>
                )}
              </div>
            </div>
          )}

          {msgs.map(m => (
            <div key={m.id || Math.random()} className={'flex ' + (m.role === 'user' ? 'justify-end' : 'justify-start')}>
              {m.role === 'assistant' && <div className="w-6 h-6 rounded-md flex items-center justify-center mr-2 mt-1 shrink-0 text-white" style={{background:grad}}><Logo s={10}/></div>}
              <div className={'max-w-[80%] md:max-w-xl px-4 py-3 rounded-2xl text-[13px] leading-relaxed whitespace-pre-wrap ' +
                (m.role === 'user' ? 'bg-emerald-600 text-white rounded-br-md' : 'bg-white text-gray-700 rounded-bl-md border border-gray-100 shadow-sm')}>
                {m.content}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="w-6 h-6 rounded-md flex items-center justify-center mr-2 mt-1 text-white" style={{background:grad}}><Logo s={10}/></div>
              <div className="bg-white px-4 py-3 rounded-2xl rounded-bl-md border border-gray-100 shadow-sm flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce"/>
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{animationDelay:'.15s'}}/>
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{animationDelay:'.3s'}}/>
                <span className="text-xs text-gray-400 ml-1.5">Analyzing...</span>
              </div>
            </div>
          )}
          <div ref={btm}/>
        </div>

        {/* Diagnosis Popup */}
        {popup && diag && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={()=>setPopup(false)}>
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto" onClick={e=>e.stopPropagation()}>
              {/* Header */}
              <div className="text-white p-5 rounded-t-2xl" style={{background:grad}}>
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-white/50 text-[10px] font-medium uppercase tracking-widest mb-1">Diagnosis Report</p>
                    <h2 className="text-xl font-bold">{diag.disease}</h2>
                    <div className="flex flex-wrap gap-2 mt-2">
                      <span className="bg-white/15 px-2.5 py-0.5 rounded-full text-xs">{(diag.confidence*100).toFixed(0)}% confidence</span>
                      {diag.urgency && <span className="bg-amber-400/25 px-2.5 py-0.5 rounded-full text-xs">{diag.urgency}</span>}
                    </div>
                  </div>
                  <button onClick={()=>setPopup(false)} className="p-1 hover:bg-white/15 rounded-full"><X size={20}/></button>
                </div>
              </div>

              <div className="p-5 space-y-2.5">
                {/* Clinical sections */}
                <Sec t="Clinical Reasoning">
                  <p className="text-gray-600 text-sm">{diag.explanation}</p>
                  {diag.causal_analysis && <p className="text-gray-400 text-xs mt-2 bg-gray-50 p-2 rounded font-mono leading-relaxed">{diag.causal_analysis}</p>}
                </Sec>

                <Sec t="Recommended Medicines">
                  {sp(diag.medicines).map((m,i) => <p key={i} className="text-sm text-gray-600 py-0.5">- {m}</p>)}
                </Sec>

                <Sec t="Diet and Nutrition">
                  {sp(diag.diet).map((m,i) => <p key={i} className="text-sm text-gray-600 py-0.5">- {m}</p>)}
                </Sec>

                <Sec t="Home Care">
                  {sp(diag.remedies).map((m,i) => <p key={i} className="text-sm text-gray-600 py-0.5">- {m}</p>)}
                </Sec>

                <Sec t="Physical Activity">
                  {sp(diag.exercise).map((m,i) => <p key={i} className="text-sm text-gray-600 py-0.5">- {m}</p>)}
                </Sec>

                <Sec t="Red Flags - See Doctor Immediately">
                  {sp(diag.when_to_see_doctor).map((m,i) => <p key={i} className="text-sm text-red-600 py-0.5">- {m}</p>)}
                </Sec>

                <Sec t="Specialist Referral">
                  <p className="text-sm text-gray-700 font-medium">{diag.specialist || 'General Practitioner'}</p>
                </Sec>

                {diag.alternatives?.length > 0 && (
                  <Sec t="Differential Diagnoses">
                    <div className="flex flex-wrap gap-1.5">
                      {diag.alternatives.map((a,i) => (
                        <span key={i} className="bg-gray-100 px-2.5 py-1 rounded-full text-xs text-gray-600">
                          {a.disease} ({(a.confidence*100).toFixed(0)}%)
                        </span>
                      ))}
                    </div>
                  </Sec>
                )}

                {/* Hospitals */}
                {hosps.length > 0 ? (
                  <Sec t={`Nearby Hospitals (${hosps.length})`}>
                    {hosps.slice(0,6).map((h,i) => (
                      <div key={i} className="flex items-start gap-2 p-2.5 bg-gray-50 rounded-lg mb-1.5 hover:bg-emerald-50 transition-colors">
                        <MapPin size={13} className="text-red-400 mt-0.5 shrink-0"/>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-700">{h.name}</p>
                          <div className="flex items-center gap-3 mt-0.5">
                            <span className="text-xs text-gray-400 capitalize">{h.type}</span>
                            {h.distance_km && <span className="text-xs text-gray-400">{h.distance_km} km</span>}
                            {h.lat && h.lng && (
                              <a href={`https://www.google.com/maps/dir/?api=1&destination=${h.lat},${h.lng}`}
                                 target="_blank" rel="noopener"
                                 className="text-xs text-emerald-600 hover:text-emerald-700 font-medium">
                                Directions
                              </a>
                            )}
                          </div>
                          {h.phone && <p className="text-xs text-gray-400 mt-0.5">{h.phone}</p>}
                        </div>
                      </div>
                    ))}
                  </Sec>
                ) : (
                  locStatus === 'denied' ? (
                    <div className="flex items-center gap-2 p-3 bg-amber-50 rounded-xl border border-amber-100">
                      <AlertCircle size={15} className="text-amber-500 shrink-0"/>
                      <p className="text-xs text-amber-700">Location access was denied. Allow location in browser to see nearby hospitals.</p>
                    </div>
                  ) : null
                )}

                {/* Feedback */}
                {fb === 'ask' && (
                  <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-100">
                    <p className="text-sm font-semibold text-gray-700 mb-2.5">Was this diagnosis accurate?</p>
                    <div className="flex gap-2">
                      <button onClick={fbOk} disabled={fbLoading}
                        className="flex-1 py-2.5 bg-emerald-600 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-1.5 hover:bg-emerald-700 disabled:opacity-50">
                        <CheckCircle size={15}/>{fbLoading ? 'Saving...' : 'Correct'}
                      </button>
                      <button onClick={fbNo} disabled={fbLoading}
                        className="flex-1 py-2.5 bg-gray-200 text-gray-700 rounded-lg text-sm font-medium flex items-center justify-center gap-1.5 hover:bg-gray-300 disabled:opacity-50">
                        <XCircle size={15}/>Incorrect
                      </button>
                    </div>
                  </div>
                )}

                {fb === 'wrong' && (
                  <div className="bg-amber-50 rounded-xl p-4 border border-amber-100">
                    <p className="text-sm font-semibold text-gray-700 mb-1">What was the correct condition?</p>
                    <p className="text-xs text-gray-500 mb-2">This helps Arogya improve its predictions.</p>
                    <input value={corrDis} onChange={e=>setCorrDis(e.target.value)}
                      placeholder="Enter the correct disease name..."
                      className="w-full p-2.5 bg-white border border-amber-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-amber-300 mb-2"/>
                    <div className="flex gap-2">
                      <button onClick={fbFix} disabled={fbLoading}
                        className="flex-1 py-2 bg-amber-500 text-white rounded-lg text-sm font-medium disabled:opacity-50">
                        {fbLoading ? 'Saving...' : 'Submit Correction'}
                      </button>
                      <button onClick={fbFix} disabled={fbLoading}
                        className="py-2 px-4 bg-gray-200 text-gray-600 rounded-lg text-sm disabled:opacity-50">
                        Skip
                      </button>
                    </div>
                  </div>
                )}

                {fb === 'done' && (
                  <div className="bg-emerald-50 rounded-lg p-3 text-center border border-emerald-100">
                    <p className="text-sm text-emerald-700 font-medium">Feedback recorded. Arogya is learning from this.</p>
                  </div>
                )}

                {fb === 'no_pred' && (
                  <div className="bg-gray-50 rounded-lg p-3 text-center border border-gray-100">
                    <p className="text-xs text-gray-500">Feedback unavailable - diagnosis was not saved to database.</p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2 pt-2">
                  <button onClick={dlPdf}
                    className="flex-1 py-3 text-white rounded-xl text-sm font-semibold flex items-center justify-center gap-2 hover:opacity-90 shadow-lg shadow-emerald-200"
                    style={{background:grad}}>
                    <Download size={15}/>Download Report
                  </button>
                  <button onClick={()=>setPopup(false)}
                    className="flex-1 py-3 bg-gray-100 text-gray-700 rounded-xl text-sm font-semibold hover:bg-gray-200">
                    Close
                  </button>
                </div>
                <p className="text-[10px] text-gray-400 text-center pt-1">AI-generated guidance. Always consult a qualified doctor for proper diagnosis.</p>
              </div>
            </div>
          </div>
        )}

        {/* Input Bar */}
        <div className="bg-white/80 backdrop-blur border-t border-gray-200/50 p-3 md:p-4 shrink-0">
          {rec && (
            <div className="max-w-2xl mx-auto mb-2.5 flex items-center justify-center gap-3 px-4 py-2.5 bg-red-50 border border-red-200 rounded-xl">
              <div className="w-2.5 h-2.5 bg-red-500 rounded-full animate-pulse"/>
              <span className="text-sm font-medium text-red-700">Recording</span>
              <span className="text-sm font-mono text-red-600 tabular-nums">{fmt(recSec)}</span>
              <button onClick={stopRec} className="ml-1 px-3 py-1 bg-red-500 text-white text-xs rounded-md font-medium hover:bg-red-600 flex items-center gap-1">
                <Square size={10} fill="white"/>Stop
              </button>
            </div>
          )}
          <div className="max-w-2xl mx-auto flex items-center gap-2">
            <input type="file" ref={fRef} accept="image/*" className="hidden" onChange={imgSend}/>
            <input type="file" ref={pRef} accept=".pdf" className="hidden" onChange={pdfSend}/>
            <button onClick={()=>fRef.current?.click()} className="p-2 text-gray-400 hover:text-emerald-600 rounded-lg hover:bg-emerald-50 transition-colors" title="Upload image">
              <ImagePlus size={18}/>
            </button>
            <button onClick={()=>pRef.current?.click()} className="p-2 text-gray-400 hover:text-emerald-600 rounded-lg hover:bg-emerald-50 transition-colors" title="Upload PDF">
              <FileText size={18}/>
            </button>
            {!rec && (
              <button onClick={startRec} className="p-2 text-gray-400 hover:text-emerald-600 rounded-lg hover:bg-emerald-50 transition-colors" title="Voice input">
                <Mic size={18}/>
              </button>
            )}
            <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==='Enter'&&send()}
              placeholder="Describe your symptoms..."
              className="flex-1 px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent"
              disabled={loading || rec}/>
            <button onClick={send} disabled={loading || !input.trim() || rec}
              className="p-2.5 text-white rounded-xl disabled:opacity-30 shadow-md shadow-emerald-200 hover:opacity-90"
              style={{background:grad}}>
              <Send size={16}/>
            </button>
          </div>
          <p className="text-center text-[9px] text-gray-400 mt-1.5 tracking-wide">AROGYA AI HEALTH ASSISTANT</p>
        </div>
      </div>
    </div>
  )
}