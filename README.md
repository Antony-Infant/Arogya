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
