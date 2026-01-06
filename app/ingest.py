from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

import os
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ FIXED PATH
PDF_DIR = BASE_DIR / "data" / "policies"
VECTOR_DIR = BASE_DIR / "vectorstore"


def ingest_pdfs():
    if not PDF_DIR.exists():
        print(f"❌ PDF directory not found: {PDF_DIR}")
        return

    documents = []

    for pdf in PDF_DIR.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf))
        documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(str(VECTOR_DIR))

    print("✅ Policy PDFs ingested successfully.")


if __name__ == "__main__":
    ingest_pdfs()
