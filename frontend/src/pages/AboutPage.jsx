import { useNavigate } from 'react-router-dom'
import { Brain, Activity, Shield, MessageSquare, Mic, Camera, FileText, MapPin, Smartphone, ArrowRight } from 'lucide-react'

const Logo = ({s=28}) => <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>

export default function AboutPage() {
  const nav = useNavigate()
  const isLoggedIn = !!localStorage.getItem('access_token')

  const F = ({icon:I, title, desc}) => (
    <div className="bg-white/70 backdrop-blur border border-gray-100 rounded-xl p-5 hover:shadow-lg hover:border-emerald-200 transition-all duration-300 hover:-translate-y-0.5">
      <div className="w-10 h-10 bg-emerald-50 rounded-lg flex items-center justify-center mb-3 text-emerald-600"><I size={20}/></div>
      <h3 className="font-semibold text-gray-800 text-sm mb-1.5">{title}</h3>
      <p className="text-gray-500 text-xs leading-relaxed">{desc}</p>
    </div>
  )

  const Step = ({n, title, desc}) => (
    <div className="flex gap-4">
      <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-sm font-bold shrink-0">{n}</div>
      <div><p className="font-semibold text-gray-800 text-sm">{title}</p><p className="text-gray-500 text-xs mt-0.5 leading-relaxed">{desc}</p></div>
    </div>
  )

  return (
    <div className="min-h-screen" style={{background:'linear-gradient(160deg,#ecfdf5 0%,#f0fdf4 30%,#f8fafc 70%,#ecfdf5 100%)'}}>

      {/* Hero */}
      <div className="max-w-5xl mx-auto px-4 pt-12 pb-8">
        <nav className="flex items-center justify-between mb-16">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg flex items-center justify-center text-white" style={{background:'linear-gradient(135deg,#047857,#059669)'}}>
              <Logo s={18}/>
            </div>
            <span className="font-bold text-gray-900 text-lg tracking-tight">Arogya</span>
          </div>
          <div className="flex gap-2">
            {isLoggedIn ? (
              <button onClick={()=>nav('/chat')} className="px-5 py-2 text-white rounded-lg text-sm font-medium hover:opacity-90 transition-opacity flex items-center gap-1.5"
                style={{background:'linear-gradient(135deg,#047857,#059669)'}}>
                Open Chat <ArrowRight size={14}/>
              </button>
            ) : (
              <>
                <button onClick={()=>nav('/login')} className="px-4 py-2 text-gray-600 hover:text-gray-900 text-sm font-medium">Sign In</button>
                <button onClick={()=>nav('/register')} className="px-5 py-2 text-white rounded-lg text-sm font-medium hover:opacity-90"
                  style={{background:'linear-gradient(135deg,#047857,#059669)'}}>
                  Get Started
                </button>
              </>
            )}
          </div>
        </nav>

        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl text-white shadow-xl shadow-emerald-200 mb-6"
            style={{background:'linear-gradient(135deg,#047857,#059669,#10b981)'}}>
            <Logo s={32}/>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 tracking-tight mb-4">
            Your AI Health Assistant
          </h1>
          <p className="text-lg text-gray-500 max-w-2xl mx-auto mb-8 leading-relaxed">
            Arogya combines Causal AI, medical knowledge retrieval, and natural doctor-like conversation to provide intelligent health guidance. Describe your symptoms, upload reports, or ask any health question.
          </p>
          <div className="flex justify-center gap-3">
            <button onClick={()=>nav(isLoggedIn ? '/chat' : '/register')}
              className="px-8 py-3.5 text-white rounded-xl text-sm font-semibold hover:opacity-90 shadow-lg shadow-emerald-200 flex items-center gap-2 transition-all"
              style={{background:'linear-gradient(135deg,#047857,#059669,#10b981)'}}>
              Start Consultation <ArrowRight size={16}/>
            </button>
            <button onClick={()=>document.getElementById('features')?.scrollIntoView({behavior:'smooth'})}
              className="px-8 py-3.5 bg-white text-gray-700 rounded-xl text-sm font-semibold border border-gray-200 hover:border-emerald-300 hover:bg-emerald-50 transition-all">
              Learn More
            </button>
          </div>
        </div>

        {/* Core Tech */}
        <div id="features" className="mb-16">
          <h2 className="text-center text-2xl font-bold text-gray-900 mb-2">Three AI Systems Working Together</h2>
          <p className="text-center text-gray-500 text-sm mb-8 max-w-xl mx-auto">Unlike simple symptom checkers, Arogya uses causal reasoning, evidence retrieval, and natural conversation in one unified pipeline.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <F icon={Brain} title="Causal AI Engine"
              desc="Disease-symptom causal graph with 1,088 nodes and 2,107 weighted edges. DoWhy calculates Average Treatment Effects for scientifically grounded predictions, not just statistical correlation." />
            <F icon={Activity} title="RAG Knowledge Pipeline"
              desc="4,614 medical vectors in ChromaDB indexed from 505 diseases and the Gale Encyclopedia of Medicine. Every response is grounded in verified medical literature." />
            <F icon={MessageSquare} title="Multi-Turn Doctor Chat"
              desc="Full conversation history passed as structured message turns to LLaMA 3, identical to how Claude and ChatGPT work. The AI decides when it has enough info to diagnose." />
          </div>
        </div>

        {/* Features */}
        <div className="mb-16">
          <h2 className="text-center text-2xl font-bold text-gray-900 mb-2">Complete Health Platform</h2>
          <p className="text-center text-gray-500 text-sm mb-8">Every feature runs 100% locally. No cloud costs. No data leaves your device.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <F icon={Mic} title="Voice Input" desc="Speak your symptoms using OpenAI Whisper speech-to-text running locally. Supports multiple languages and accents." />
            <F icon={Camera} title="Medical Image Analysis" desc="Upload prescriptions, lab reports, or skin conditions. LLaMA 3.2 Vision extracts clinical data from medical images." />
            <F icon={FileText} title="PDF Report Upload" desc="Share lab results and discharge summaries as PDF files. Text is extracted and analyzed in context of your consultation." />
            <F icon={MapPin} title="Hospital Finder" desc="GPS-based nearby hospital, clinic, and pharmacy search using OpenStreetMap with Google Maps directions." />
            <F icon={Smartphone} title="WhatsApp Channel" desc="Full consultation via WhatsApp with text, voice, image, PDF, hospital recommendations, and feedback support." />
            <F icon={Shield} title="Antifragile Learning" desc="The system improves from wrong predictions. Your feedback adjusts causal weights and updates the knowledge base." />
          </div>
        </div>

        {/* How it works */}
        <div className="mb-16">
          <h2 className="text-center text-2xl font-bold text-gray-900 mb-2">How a Consultation Works</h2>
          <p className="text-center text-gray-500 text-sm mb-8">A real doctor conversation, not a checkbox form.</p>
          <div className="max-w-xl mx-auto bg-white/70 backdrop-blur rounded-2xl border border-gray-100 p-6 space-y-5">
            <Step n="1" title="Describe Your Symptoms" desc="Type, speak, upload an image, or share a PDF report. Arogya understands natural language." />
            <Step n="2" title="AI Doctor Asks Follow-ups" desc="Clinically relevant questions about duration, severity, and context. Not a fixed script." />
            <Step n="3" title="You Confirm When Done" desc="The AI asks 'anything else?' and only diagnoses when you say you have shared everything." />
            <Step n="4" title="Comprehensive Diagnosis" desc="Causal AI + RAG + LLM generate: condition, medicines, diet, home care, exercise, red flags, specialist." />
            <Step n="5" title="Your Feedback Improves Arogya" desc="Mark correct or incorrect. Wrong predictions make the system stronger over time." />
          </div>
        </div>

        {/* Dataset */}
        <div className="mb-16 text-center">
          <div className="inline-grid grid-cols-3 gap-6 bg-white/70 backdrop-blur rounded-2xl border border-gray-100 p-8">
            <div><p className="text-3xl font-bold text-emerald-600">505</p><p className="text-xs text-gray-500 mt-1">Diseases Covered</p></div>
            <div><p className="text-3xl font-bold text-emerald-600">4,614</p><p className="text-xs text-gray-500 mt-1">Medical Vectors</p></div>
            <div><p className="text-3xl font-bold text-emerald-600">18</p><p className="text-xs text-gray-500 mt-1">Medical Categories</p></div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center mb-12">
          <button onClick={()=>nav(isLoggedIn ? '/chat' : '/register')}
            className="px-10 py-4 text-white rounded-xl text-base font-semibold hover:opacity-90 shadow-xl shadow-emerald-200 inline-flex items-center gap-2"
            style={{background:'linear-gradient(135deg,#047857,#059669,#10b981)'}}>
            Start Your Consultation <ArrowRight size={18}/>
          </button>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200/50 pt-6 pb-8 text-center">
          <p className="text-xs text-gray-400 mb-1">Department of Computer Science and Engineering, PMIST Thanjavur</p>
          <p className="text-xs text-gray-400 mb-1">Antony Infant Akash G, Manikandan M, Vignesh A | Guide: Ms. U. Elamathi</p>
          <p className="text-xs text-gray-400">Arogya is AI-generated guidance and is not a substitute for professional medical advice.</p>
        </div>
      </div>
    </div>
  )
}
