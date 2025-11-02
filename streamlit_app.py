import streamlit as st
import requests
import time
import json
import os

# =========================================
# 🌐 API Configuration
# =========================================
API_BASE = "http://127.0.0.1:8000"

# =========================================
# 💾 Chat Storage Path
# =========================================
CHAT_FILE = "saved_chats.json"

# =========================================
# 📂 Load & Save Helpers
# =========================================
def load_saved_chats():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_chats(chats):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False, indent=4)

# =========================================
# 🎨 Page Setup
# =========================================
st.set_page_config(page_title="StarGPT", page_icon="🌟", layout="wide")

# =========================================
# 💬 Custom CSS (ChatGPT Look)
# =========================================
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: #0e1117;
            color: white;
        }
        [data-testid="stSidebar"] {
            background-color: #1a1a1a !important;
            color: white;
            border-right: 1px solid #333;
        }
        .sidebar-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: #00b4d8;
            padding: 1rem 0 0.5rem 0;
        }
        .chat-btn {
            display: block;
            width: 100%;
            background-color: transparent;
            color: #e1e1e1;
            border: none;
            text-align: left;
            padding: 0.6rem 0.8rem;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .chat-btn:hover {
            background-color: #2a2a2a;
        }
        .chat-container {
            padding: 1rem 2rem;
            max-width: 850px;
            margin: auto;
        }
        .user-bubble, .bot-bubble {
            border-radius: 15px;
            padding: 0.9rem 1rem;
            margin-bottom: 1rem;
            width: fit-content;
            max-width: 80%;
            line-height: 1.5;
            word-wrap: break-word;
            box-shadow: 0px 0px 5px rgba(255,255,255,0.05);
        }
        .user-bubble {
            background-color: #0078ff;
            color: white;
            margin-left: auto;
        }
        .bot-bubble {
            background-color: #1e1e1e;
            color: #e1e1e1;
        }
        .typing {
            display: inline-block;
            border-right: 3px solid #0078ff;
            animation: blink 0.8s infinite;
        }
        @keyframes blink {
            50% { border-color: transparent; }
        }
    </style>
""", unsafe_allow_html=True)

# =========================================
# 💾 Session State Initialization
# =========================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = load_saved_chats()
if "current_chat_title" not in st.session_state:
    st.session_state.current_chat_title = "New Chat"
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# =========================================
# 🧭 Sidebar Controls (ChatGPT Style)
# =========================================
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🌟 StarGPT</div>", unsafe_allow_html=True)

    # ➕ New Chat Button
    if st.button("➕ New Chat"):
        if st.session_state.chat_history:
            first_message = st.session_state.chat_history[0]["content"] if st.session_state.chat_history else "Untitled"
            chat_title = first_message[:40] + "..." if len(first_message) > 40 else first_message
            st.session_state.saved_chats.append({
                "title": chat_title,
                "messages": st.session_state.chat_history
            })
            save_chats(st.session_state.saved_chats)
        st.session_state.chat_history = []
        st.session_state.current_chat_title = "New Chat"
        st.rerun()

    # 🔍 Search Chat
    st.markdown("#### 🔍 Search chats")
    search = st.text_input("Search")
    st.session_state.search_query = search.strip().lower()

    # 📜 Display Saved Chats
    st.markdown("#### 💬 All Chats")
    filtered_chats = [
        c for c in st.session_state.saved_chats
        if st.session_state.search_query in c["title"].lower()
    ]

    if filtered_chats:
        for i, chat in enumerate(filtered_chats):
            if st.button(chat["title"], key=f"chat_{i}", use_container_width=True):
                st.session_state.chat_history = chat["messages"]
                st.session_state.current_chat_title = chat["title"]
                st.rerun()
    else:
        st.caption("No saved chats yet.")

    st.markdown("---")

    # 🧹 Clear Server Memory
    if st.button("🧹 Clear Memory (Server)"):
        try:
            res = requests.post(f"{API_BASE}/clear")
            if res.status_code == 200:
                st.session_state.chat_history = []
                st.success("✅ Server memory cleared!")
            else:
                st.error("❌ Failed to clear memory.")
        except Exception as e:
            st.error(f"🚫 Connection error: {e}")

    # 🗑️ Delete All Saved Chats
    if st.button("🗑️ Delete All Chats"):
        st.session_state.saved_chats = []
        save_chats([])
        st.session_state.chat_history = []
        st.success("🗑️ All chats deleted!")
        st.rerun()

# =========================================
# 💬 Chat Section
# =========================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
st.title(f"🤖 {st.session_state.current_chat_title}")
st.caption("RAG + LLM Smart Assistant • Built by 🌟AppStar")
st.markdown("---")

# =========================================
# 🧠 Chat Display
# =========================================
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{chat['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>{chat['content']}</div>", unsafe_allow_html=True)

# =========================================
# ✍️ User Input
# =========================================
user_input = st.chat_input("💭 Ask StarGPT anything...")

if user_input:
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='user-bubble'>{user_input}</div>", unsafe_allow_html=True)

    # API Call
    with st.spinner("🤖 Thinking..."):
        try:
            response = requests.post(f"{API_BASE}/chat", json={"question": user_input})
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "⚠️ No response received.")
            else:
                answer = f"❌ API Error {response.status_code}"
        except Exception as e:
            answer = f"🚫 Connection error: {e}"

    # Typing effect
    placeholder = st.empty()
    full_text = ""
    for char in answer:
        full_text += char
        placeholder.markdown(f"<div class='bot-bubble'>{full_text}<span class='typing'></span></div>", unsafe_allow_html=True)
        time.sleep(0.02)
    placeholder.markdown(f"<div class='bot-bubble'>{answer}</div>", unsafe_allow_html=True)

    # Store bot response
    st.session_state.chat_history.append({"role": "bot", "content": answer})

    # Auto-save chat progress
    if st.session_state.current_chat_title != "New Chat":
        for chat in st.session_state.saved_chats:
            if chat["title"] == st.session_state.current_chat_title:
                chat["messages"] = st.session_state.chat_history
                break
        save_chats(st.session_state.saved_chats)

st.markdown('</div>', unsafe_allow_html=True)
