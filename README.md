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
