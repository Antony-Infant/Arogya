<<<<<<< HEAD
# 🏥 Antifragile Causal AI & RAG Medical Chatbot

## Architecture
- **Backend**: Django REST Framework + MySQL
- **Frontend**: Vite React + TailwindCSS
- **LLM**: LLaMA 3 via Ollama (local, free)
- **Vision**: LLaMA 3.2 Vision via Ollama
- **Causal AI**: DoWhy + CausalNex
- **RAG**: LangChain + ChromaDB + Sentence Transformers
- **Voice**: OpenAI Whisper (STT) + gTTS (TTS)
- **Translation**: LibreTranslate
- **WhatsApp**: Twilio
- **Antifragile**: Evidently AI + Celery + Redis

## Quick Start

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt --break-system-packages
cp .env.example .env  # Edit with your settings
python manage.py migrate
python manage.py createsuperuser
```

### 2. Ollama Models
```bash
ollama pull llama3
ollama pull llama3.2-vision
```

### 3. Load Data
```bash
cd backend
python scripts/load_dataset.py
python scripts/build_causal_graph.py
python scripts/index_rag.py
```

### 4. Start Backend
```bash
redis-server &
cd backend
celery -A config worker -l info &
python manage.py runserver
```

### 5. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 6. Access
- Web: http://localhost:5173
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

## Project Structure
```
medical_chatbot/
├── backend/
│   ├── config/          # Django settings, URLs, WSGI, Celery
│   ├── apps/
│   │   ├── users/       # User auth & profiles
│   │   ├── chat/        # Chat sessions & messages
│   │   ├── diagnosis/   # Causal AI + RAG engines
│   │   ├── feedback/    # Antifragile feedback loop
│   │   ├── reports/     # PDF report generation
│   │   └── whatsapp/    # Twilio WhatsApp
│   ├── services/
│   │   ├── llm_service.py         # Ollama LLaMA 3
│   │   ├── chat_engine.py         # Main orchestrator
│   │   ├── prompt_templates.py    # All LLM prompts
│   │   ├── causal_engine.py       # DoWhy/CausalNex
│   │   ├── rag_engine.py          # LangChain + ChromaDB
│   │   ├── symptom_extractor.py   # Symptom extraction
│   │   ├── vision_service.py      # LLaMA 3.2 Vision
│   │   ├── whisper_service.py     # Speech-to-Text
│   │   ├── tts_service.py         # Text-to-Speech
│   │   ├── translate_service.py   # LibreTranslate
│   │   ├── hospital_service.py    # OpenStreetMap
│   │   └── pdf_generator.py       # ReportLab
│   ├── scripts/         # Setup & data processing
│   ├── data/            # Dataset, causal graph, ChromaDB
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page views
│   │   ├── services/    # API calls
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```
=======
# Arogya
AI-powered medical chatbot with Causal AI + RAG for symptom-based disease diagnosis
## What is Arogya?

Arogya ("health" in Sanskrit) is a full-stack AI medical assistant that behaves like 
a real doctor — it asks focused follow-up questions, gathers symptoms over multiple 
turns, and only diagnoses when it has enough information.

Unlike simple symptom checkers, Arogya uses three layers of intelligence:

- **Causal AI** — DoWhy + CausalNex model *why* a disease is predicted, not just 
  pattern-matching. Each diagnosis includes an Average Treatment Effect (ATE) score 
  explaining the causal link between symptoms and disease.
- **RAG** — LangChain + ChromaDB retrieves relevant medical knowledge at query time, 
  grounding the LLM response in real medical literature.
- **LLaMA 3 (local)** — Runs entirely on your machine via Ollama. No OpenAI API key, 
  no cloud costs, no data leaving your device.

## Key Features

- 🩺 Multi-turn conversational diagnosis with patient profiling
- 🧠 Causal inference engine (DoWhy ATE analysis per diagnosis)
- 📚 RAG pipeline with ChromaDB vector search
- 🖼️ Medical image analysis via LLaMA 3.2 Vision
- 🎙️ Voice input (OpenAI Whisper) + voice output (gTTS)
- 🌐 Multilingual support via LibreTranslate
- 📱 WhatsApp integration via Twilio
- 🗺️ Nearby hospital finder via OpenStreetMap
- 📄 PDF diagnosis report generation
- 🔄 Antifragile feedback loop (Evidently AI + Celery) — improves over time
- 🔐 JWT authentication with full user medical profiles
>>>>>>> 1d4af8d8151bb2a6a3aff42d6dedf1cef0cb6704
