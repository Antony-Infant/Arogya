#!/usr/bin/env python3
"""
Index all documents into ChromaDB for RAG pipeline.
Uses chromadb==0.4.24 (pure Python, no Rust DLL - Windows compatible).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

import pandas as pd
# Use langchain_community - works with chromadb 0.4.24 (pure Python, no Rust)
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from django.conf import settings


def index_dataset():
    print("Indexing disease dataset...")
    df = pd.read_csv(settings.DISEASE_DATASET_PATH)
    docs = []
    for _, row in df.iterrows():
        text = (
            f"Disease: {row['disease_name']}\n"
            f"Category: {row['category']} - {row.get('subcategory','')}\n"
            f"ICD-10: {row.get('icd10_code','')}\n"
            f"Description: {row.get('description','')}\n"
            f"Pathophysiology: {row.get('pathophysiology','')}\n"
            f"Primary Symptoms: {row.get('primary_symptoms','')}\n"
            f"All Symptoms: {row.get('all_symptoms','')}\n"
            f"Risk Factors: {row.get('risk_factors','')}\n"
            f"Causes: {row.get('common_causes','')}\n"
            f"Diagnosis: {row.get('diagnostic_tests','')}\n"
            f"Treatment: {row.get('treatment_approach','')}\n"
            f"Medicines: {row.get('recommended_medicines','')}\n"
            f"Diet: {row.get('diet_recommendations','')}\n"
            f"Home Remedies: {row.get('home_remedies','')}\n"
            f"Exercise: {row.get('exercise_recommendations','')}\n"
            f"Complications: {row.get('complications_if_untreated','')}\n"
            f"Red Flags: {row.get('red_flags','')}"
        )
        docs.append(Document(
            page_content=text,
            metadata={
                'source': 'disease_dataset',
                'disease': str(row['disease_name']),
                'category': str(row.get('category', '')),
            }
        ))
    print(f"  Created {len(docs)} disease documents")
    return docs


def index_pdf():
    print("Looking for Gale Encyclopedia PDF...")
    docs = []
    pdf_dir = settings.RAG_DOCUMENTS_DIR
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir, exist_ok=True)
        print(f"  No PDF directory found. Created: {pdf_dir}")
        print("  Place PDFs there and re-run to include them.")
        return docs

    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"  No PDFs found in {pdf_dir}. Indexing dataset only.")
        return docs

    for fname in pdf_files:
        path = os.path.join(pdf_dir, fname)
        print(f"  Indexing: {fname}")
        try:
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(path)
            pages = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(pages)
            for chunk in chunks:
                chunk.metadata['source'] = fname
            docs.extend(chunks)
            print(f"  Created {len(chunks)} chunks from {fname}")
        except Exception as e:
            print(f"  Error indexing {fname}: {e}")

    return docs


def main():
    print("=" * 50)
    print("Arogya RAG Indexing")
    print("Using chromadb 0.4.x (pure Python, Windows safe)")
    print("=" * 50)

    embeddings = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2'
    )

    all_docs = []
    all_docs.extend(index_dataset())
    all_docs.extend(index_pdf())

    print(f"\nTotal documents to index: {len(all_docs)}")

    if not all_docs:
        print("No documents found! Check dataset path.")
        return

    # Clear old index if exists
    persist_dir = settings.CHROMA_PERSIST_DIR
    if os.path.exists(persist_dir):
        import shutil
        print(f"Clearing old index at {persist_dir}...")
        shutil.rmtree(persist_dir)

    os.makedirs(persist_dir, exist_ok=True)

    print("Creating ChromaDB index (takes 2-5 minutes)...")
    print("Do not close this window...")

    # Index in batches to avoid memory issues
    batch_size = 500
    vectorstore = None

    for i in range(0, len(all_docs), batch_size):
        batch = all_docs[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(all_docs) + batch_size - 1) // batch_size
        print(f"  Batch {batch_num}/{total_batches} ({len(batch)} docs)...")

        if vectorstore is None:
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                persist_directory=persist_dir,
            )
        else:
            vectorstore.add_documents(batch)

    if vectorstore:
        vectorstore.persist()
        count = vectorstore._collection.count()
        print(f"\nDone! Indexed {count} vectors")
        print(f"Saved to: {persist_dir}")
    else:
        print("Indexing failed.")


if __name__ == '__main__':
    main()
