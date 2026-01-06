from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import traceback

from app.rag import get_rag_chain

# -------------------------------
# FastAPI app
# -------------------------------
app = FastAPI(title="Policy RAG Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Load RAG chain once
# -------------------------------
qa_chain = get_rag_chain()

# -------------------------------
# Request schema
# -------------------------------
class QuestionRequest(BaseModel):
    question: str

# -------------------------------
# API endpoint
# -------------------------------
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        result = qa_chain(request.question)

        return {
            "answer": result["result"],
            "sources": result.get("sources", [])
        }

    except Exception:
        print("❌ ERROR in /ask")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import traceback
from fastapi.middleware.cors import CORSMiddleware

from app.rag import get_rag_chain

app = FastAPI(title="Policy RAG Bot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

qa_chain = get_rag_chain()

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(request: QuestionRequest):
    try:
        result = qa_chain(request.question)
        return {
            "answer": result["result"],
            "sources": result["sources"]
        }

    except Exception:
        print("❌ ERROR:")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
