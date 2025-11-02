import requests
import joblib
import numpy as np
import sys
import time
import os
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================
# 🧩 Create Embedding Function
# ============================================================
def create_embedding(text):
    try:
        response = requests.post("http://localhost:11434/api/embeddings", json={
            "model": "bge-m3",
            "prompt": text
        })
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"❌ Embedding Error: {e}")
        return None

# ============================================================
# 💬 Generate AI Response (RAG + Intent + Memory)
# ============================================================
def generate_response(memory, context, question, use_context=True, summarize=False):
    q_lower = question.lower()

    # 🎯 1️⃣ Intent: Generate Questions Mode
    if any(word in q_lower for word in ["question", "quiz", "mcq", "interview"]):
        prompt = f"""
You are AppsterGPT — a professional AI developed by Arpit Kumar Mishra.
Generate 10–15 **clear and relevant questions** about:
"{question}"

Guidelines:
- Mix beginner and advanced levels.
- Use a numbered list.
- Add hints or subtopics in parentheses if useful.

Answer:
"""

    # 🧠 2️⃣ Intent: Summarization Mode
    elif summarize:
        prompt = f"""
You are AppsterGPT — a summarization expert AI built by Arpit Kumar Mishra.
Your task is to create a **concise summary** of the conversation below.

Keep only key facts, important context, and user preferences.
Make it natural and readable, like a short memory summary.

Conversation:
{memory}

Summary:
"""

    # 💡 3️⃣ Normal RAG or General QA Mode
    else:
        context_part = f"\nContext:\n{context}\n" if use_context and context.strip() else ""
        memory_part = f"\nConversation Memory:\n{memory}\n" if memory.strip() else ""

        prompt = f"""
You are AppsterGPT — a highly advanced AI assistant created by Arpit Kumar Mishra.
Use both the retrieved context and conversation memory to give a clear, natural, and structured answer.

{memory_part}
{context_part}

Question: {question}

Answer in detail, with examples or bullet points where helpful:
"""

    payload = {"model": "llama3", "prompt": prompt, "stream": False}

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"❌ Generation Error: {e}")
        return "Sorry, I couldn’t generate a response right now."

# ============================================================
# 🎞️ Typing Effect
# ============================================================
def type_effect(text, delay=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# ============================================================
# 💾 Memory Handling
# ============================================================
HISTORY_FILE = "chat_history.txt"

def load_memory():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            memory = f.read().strip()
        print("🧠 Loaded previous chat history.")
        return memory
    else:
        print("⚠️ Starting new session (no history found).")
        return ""

def save_memory(memory):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write(memory.strip())

# ============================================================
# 📊 Load Embeddings
# ============================================================
try:
    df = joblib.load("embeddings.joblib")
    print("✅ Embeddings loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load embeddings: {e}")
    sys.exit(1)

# ============================================================
# 🧠 Initialize Memory
# ============================================================
conversation_memory = load_memory()

# ============================================================
# 💬 Chat Loop
# ============================================================
print("\n🚀 Welcome to AppsterGPT (by Arpit Kumar Mishra)!")
print("Type 'exit' to quit or 'clear memory' to reset history.\n")

while True:
    question = input("\n💬 You: ").strip()

    if question.lower() in ["exit", "quit"]:
        print("\n💾 Saving memory before exit...")
        save_memory(conversation_memory)
        print("✅ Memory saved.")
        print("👋 Goodbye from AppsterGPT! Have a great day!\n")
        break

    if question.lower() in ["clear memory", "reset"]:
        conversation_memory = ""
        save_memory(conversation_memory)
        print("🧹 Memory cleared successfully!")
        continue

    # 🧩 Create embedding
    query_embedding = create_embedding(question)
    if query_embedding is None:
        continue

    # 🧮 RAG similarity
    similarity = cosine_similarity(np.vstack(df['embedding']), [query_embedding]).flatten()
    top_indices = similarity.argsort()[::-1][:5]
    top_chunks = df.iloc[top_indices]["text"].tolist()

    context = "\n\n".join(top_chunks)
    max_sim = float(similarity[top_indices[0]])
    use_context = max_sim > 0.45

    # 🧠 Check if memory is too large
    if len(conversation_memory.split()) > 1200:
        print("\n🧩 Memory too long — summarizing...\n")
        summary = generate_response(conversation_memory, "", "Summarize memory", summarize=True)
        conversation_memory = summary
        save_memory(conversation_memory)
        print("✅ Memory summarized successfully!\n")

    # 🤖 Generate answer
    answer = generate_response(conversation_memory, context, question, use_context=use_context)

    # 🧠 Update memory
    conversation_memory += f"\nUser: {question}\nAppsterGPT: {answer}\n"
    save_memory(conversation_memory)

    # 🗣️ Display answer
    print("\n🤖 AppsterGPT:\n")
    type_effect(answer)
    print("\n" + "-" * 60)
