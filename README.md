**Policy RAG Bot**

A simple Retrieval-Augmented Generation (RAG) system that answers questions from company policy documents (HR, Leave, Security, Code of Conduct, etc.). It uses semantic search (FAISS) over embedded policy text and a local LLM to generate answers grounded in the retrieved content.

Features
- Clear, retrieval-first answers sourced from your PDFs
- Local FAISS vector store for privacy and speed
- FastAPI backend with a React (Vite) frontend
- Simple ingestion pipeline for PDF policy documents

Quick Start

1) Setup Python environment and install dependencies

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2) Add your policy PDFs

Place PDFs in the `data/policies/` folder (example: `HR_Policy.pdf`).

3) Ingest documents (build vector index)

```powershell
python -m app.ingest
```

This creates/updates the FAISS index under `vectorstore/`.

4) Start the backend API

```powershell
uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

5) Start the frontend (in a separate terminal)

```bash
cd policy-rag-ui
npm install
npm run dev
```

Open the UI at `http://localhost:5173` (or the port shown by Vite).

Project Structure (important files)
- `app/` — backend code
	- `main.py` — FastAPI app
	- `ingest.py` — ingestion & embedding pipeline
	- `rag.py` — retrieval + generation logic
	- `prompts.py` — prompt templates
- `data/policies/` — drop your PDFs here
- `vectorstore/` — FAISS index files
- `policy-rag-ui/` — React frontend (Vite)

How it works (high level)
- PDFs → split into chunks → embed → store in FAISS
- User query → retrieve relevant chunks → pass context to LLM → return grounded answer

Troubleshooting
- If ingestion fails, check `requirements.txt` for missing packages and ensure the `data/policies/` files are readable.
- If the frontend does not start, run `npm install` inside `policy-rag-ui` and check the terminal for errors.

Next steps / Suggestions
- Add answer citation (document name + page)
- Add confidence scores and chat history
- Add access controls for sensitive policies

Author
- Prashanth Desai

License
- (Add project license here if needed)