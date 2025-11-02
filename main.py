from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import joblib
import numpy as np
import os
import time
import sys
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================
# ⚙️ Configuration
# ============================================================
EMBED_MODEL = "bge-m3"
LLM_MODEL = "llama3"
OLLAMA_URL = "http://localhost:11434/api"
HISTORY_FILE = "chat_history.txt"
EMBED_FILE = "embeddings.joblib"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================
# 🌐 FastAPI App Setup
# ============================================================
app = FastAPI(
    title="AppsterGPT FastAPI",
    description="RAG + Memory chatbot API by Arpit Kumar Mishra",
    version="1.0.0",
)

# Enable CORS (frontend support)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 🧩 Utilities
# ============================================================
def create_embedding(text: str):
    try:
        res = requests.post(f"{OLLAMA_URL}/embeddings", json={"model": EMBED_MODEL, "prompt": text})
        res.raise_for_status()
        return res.json()["embedding"]
    except Exception as e:
        print("❌ Embedding Error:", e)
        return None


def query_llm(prompt: str):
    try:
        res = requests.post(f"{OLLAMA_URL}/generate", json={"model": LLM_MODEL, "prompt": prompt, "stream": False})
        res.raise_for_status()
        return res.json().get("response", "").strip()
    except Exception as e:
        print("❌ LLM Error:", e)
        return "⚠️ LLM generation failed."


def load_memory():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def save_memory(memory: str):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write(memory.strip())


# ============================================================
# 📊 Load Embeddings
# ============================================================
try:
    df = joblib.load(EMBED_FILE)
    print(f"✅ Loaded embeddings ({len(df)} chunks).")
except Exception as e:
    print(f"❌ Error loading embeddings: {e}")
    df = None

# ============================================================
# 🧠 RAG Retrieval
# ============================================================
def retrieve_top_chunks(query, top_k=5):
    emb = create_embedding(query)
    if emb is None or df is None:
        return [], 0.0
    sims = cosine_similarity(np.vstack(df["embedding"]), [emb]).flatten()
    idx = sims.argsort()[::-1][:top_k]
    return df.iloc[idx]["text"].tolist(), float(sims[idx[0]])

# ============================================================
# 💬 Response Generation Logic
# ============================================================
def generate_response(memory, context, question, use_context=True, summarize=False):
    q_lower = question.lower()

    # 🎯 Question mode
    if any(word in q_lower for word in ["question", "quiz", "mcq", "interview"]):
        prompt = f"""
You are AppsterGPT — a professional AI by Arpit Kumar Mishra.
Generate 10–15 relevant questions on: "{question}"

Guidelines:
- Mix beginner and advanced.
- Use a numbered list.
- Add hints/subtopics if useful.
"""
    elif summarize:
        prompt = f"""
Summarize the conversation concisely:
{memory}
"""
    else:
        context_part = f"\nContext:\n{context}\n" if use_context else ""
        memory_part = f"\nMemory:\n{memory}\n" if memory.strip() else ""
        prompt = f"""
You are AppsterGPT — a helpful AI by Arpit Kumar Mishra.
{memory_part}
{context_part}
User Question: {question}
Answer in detail with structure and examples:
"""
    return query_llm(prompt)


# ============================================================
# 🌍 API Routes
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h2>🚀 AppsterGPT FastAPI</h2>
    <p>Go to <a href='/docs'>/docs</a> for the interactive chat API.</p>
    """


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    question = data.get("question", "").strip()
    if not question:
        return JSONResponse({"error": "Question is empty"}, status_code=400)

    memory = load_memory()

    # RAG retrieval
    top_chunks, max_sim = retrieve_top_chunks(question)
    context = "\n\n".join(top_chunks)
    use_context = max_sim > 0.45

    # Summarize memory if large
    if len(memory.split()) > 1200:
        summary = generate_response(memory, "", "Summarize memory", summarize=True)
        memory = summary
        save_memory(memory)

    answer = generate_response(memory, context, question, use_context)

    # Update memory
    memory += f"\nUser: {question}\nAppsterGPT: {answer}\n"
    save_memory(memory)

    return {"answer": answer, "context_used": use_context, "context_snippets": top_chunks[:2]}


@app.get("/history")
async def get_history():
    memory = load_memory()
    return {"history": memory}


@app.post("/clear")
async def clear_memory():
    save_memory("")
    return {"status": "cleared"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    # Optional: extract + embed later
    return {"uploaded": filename, "path": path}


# ============================================================
# ▶️ Run Server
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
