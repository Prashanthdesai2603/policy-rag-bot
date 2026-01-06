from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from pathlib import Path
import time

# -------------------------------
# Cache
# -------------------------------
CACHE = {}
CACHE_TTL = 300  # seconds

# -------------------------------
# Paths
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DIR = BASE_DIR / "vectorstore"

# -------------------------------
# Load shared components ONCE
# -------------------------------
_embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

_db = FAISS.load_local(
    VECTOR_DIR,
    _embeddings,
    allow_dangerous_deserialization=True
)

_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0
)

# -------------------------------
# Internal helper
# -------------------------------
def _ask_llm(messages: list[str]) -> str:
    response = _llm.invoke(messages)
    return response.content.strip().split("\n")[0]


# -------------------------------
# RAG Chain
# -------------------------------
def get_rag_chain():

    def qa_chain(question: str):
        now = time.time()

        # 1️⃣ Cache
        cached = CACHE.get(question)
        if cached and now - cached[2] < CACHE_TTL:
            return {"result": cached[0], "sources": cached[1]}

        # 2️⃣ FAISS search WITH SCORE
        docs_with_scores = _db.similarity_search_with_score(question, k=3)

        # Lower score = better match
        RELEVANCE_THRESHOLD = 0.6

        relevant_docs = [
            doc for doc, score in docs_with_scores if score < RELEVANCE_THRESHOLD
        ]

        # -------------------------
        # 3️⃣ GENERAL QUESTION → OpenAI
        # -------------------------
        if not relevant_docs:
            answer = _ask_llm([
                {
                    "role": "system",
                    "content": "Give ONLY the final short answer. No explanation."
                },
                {
                    "role": "user",
                    "content": question
                }
            ])

            CACHE[question] = (answer, [], now)
            return {"result": answer, "sources": []}

        # -------------------------
        # 4️⃣ POLICY QUESTION → RAG
        # -------------------------
        context = "\n\n".join(d.page_content[:800] for d in relevant_docs)

        answer = _ask_llm([
            {
                "role": "system",
                "content": (
                    "Answer ONLY from the given context. "
                    "Return ONLY the final answer. "
                    "If not found, reply exactly: Not mentioned."
                )
            },
            {
                "role": "user",
                "content": f"""
Context:
{context}

Question:
{question}
"""
            }
        ])

        CACHE[question] = (
            answer,
            [d.metadata for d in relevant_docs],
            now
        )

        return {
            "result": answer,
            "sources": [d.metadata for d in relevant_docs]
        }

    return qa_chain

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM # pyright: ignore[reportMissingImports]
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DIR = BASE_DIR / "vectorstore"

def get_rag_chain():
    # Embeddings must match ingest.py
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Load FAISS index
    db = FAISS.load_local(
        VECTOR_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = db.as_retriever(search_kwargs={"k": 3})

    # Local LLM via Ollama
    llm = OllamaLLM(model="llama3")

    def qa_chain(question: str):
        # ✅ NEW LangChain API
        docs = retriever.invoke(question)

        context = "\n\n".join(d.page_content for d in docs)

        prompt = f"""
You are a policy assistant.
Answer ONLY from the provided context.
If the answer is not found, say "Not mentioned in the policy".

Context:
{context}

Question:
{question}

Answer:
"""

        answer = llm.invoke(prompt)

        return {
            "result": answer,
            "sources": [d.metadata for d in docs]
        }

    return qa_chain
