"""
RAG Engine - ChromaDB 0.4.x compatible (pure Python, no Rust DLL).
Uses langchain_community.vectorstores.Chroma which works with chromadb==0.4.24.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class RAGEngine:
    _instance = None
    _vectorstore = None
    _embeddings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._embeddings is None:
            self._load_embeddings()
        if self._vectorstore is None:
            self._load_vectorstore()

    def _load_embeddings(self):
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            RAGEngine._embeddings = HuggingFaceEmbeddings(
                model_name='sentence-transformers/all-MiniLM-L6-v2'
            )
            logger.info("Embeddings loaded")
        except Exception as e:
            logger.error(f"Embeddings failed: {e}")
            RAGEngine._embeddings = None

    def _load_vectorstore(self):
        try:
            # Use langchain_community - works with chromadb 0.4.x (pure Python)
            from langchain_community.vectorstores import Chroma
            RAGEngine._vectorstore = Chroma(
                persist_directory=settings.CHROMA_PERSIST_DIR,
                embedding_function=self._embeddings,
            )
            count = self._vectorstore._collection.count()
            logger.info(f"ChromaDB loaded: {count} vectors")
        except Exception as e:
            logger.warning(f"ChromaDB not available: {e}. Run scripts/index_rag.py first.")
            RAGEngine._vectorstore = None

    def retrieve(self, query: str, k: int = 5) -> list:
        if not self._vectorstore:
            return []
        try:
            results = self._vectorstore.similarity_search_with_score(query, k=k)
            return [
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'relevance_score': round(max(0, 1 - score), 3),
                }
                for doc, score in results
            ]
        except Exception as e:
            logger.error(f"RAG retrieve error: {e}")
            return []

    def retrieve_for_symptoms(self, symptoms: list) -> list:
        query = (
            f"Patient symptoms: {', '.join(symptoms)}. "
            "What disease could this indicate? Causes, diagnosis, treatment."
        )
        return self.retrieve(query, k=5)

    def retrieve_for_disease(self, disease_name: str) -> list:
        query = (
            f"Complete medical information about {disease_name}: "
            "definition, causes, symptoms, diagnosis, treatment, prognosis, complications."
        )
        return self.retrieve(query, k=3)

    def is_available(self) -> bool:
        return self._vectorstore is not None
