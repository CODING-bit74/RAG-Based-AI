import requests
import os
import json
import re
import pandas as pd
import time
import joblib
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------
# 🧩 Function: Create Embedding with Retry
# --------------------------
def create_embedding(text, retries=3, delay=2):
    """Generate embedding using local Ollama API with retry on failure."""
    for attempt in range(retries):
        try:
            response = requests.post("http://localhost:11434/api/embeddings", json={
                "model": "bge-m3",
                "prompt": text
            }, timeout=30)
            response.raise_for_status()
            embedding = response.json().get("embedding")
            if embedding:
                return embedding
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1}/{retries} failed: {e}")
            time.sleep(delay)
    print("❌ Skipping chunk after repeated failures.")
    return None


# --------------------------
# 📂 Setup JSON Folder
# --------------------------
json_folder = "jsons"
json_files = [f for f in os.listdir(json_folder) if f.endswith(".json")]

def extract_number(filename):
    match = re.search(r"\d+", filename)
    return int(match.group(0)) if match else float('inf')

json_files = sorted(json_files, key=extract_number)

all_chunks = []
chunk_id = 0

print(f"📁 Found {len(json_files)} JSON files. Starting embedding creation...\n")

# --------------------------
# 🔁 Process All JSON Files
# --------------------------
for json_file in json_files:
    file_path = os.path.join(json_folder, json_file)
    with open(file_path, "r", encoding="utf-8") as f:
        content = json.load(f)

    raw_number = content.get("video_number", os.path.splitext(json_file)[0])
    match = re.search(r"\d+", str(raw_number))
    video_number = match.group(0).zfill(3) if match else "unknown"

    print(f"🎬 Processing {json_file} (Video {video_number})...")

    for i, chunk in enumerate(content.get("chunks", [])):
        text = chunk.get("text", "").strip()
        if not text:
            continue

        embedding = create_embedding(text)
        if embedding is None:
            continue  # Skip if embedding failed

        chunk["chunk_id"] = chunk_id
        chunk["embedding"] = embedding
        chunk["number"] = video_number

        all_chunks.append(chunk)
        chunk_id += 1

    print(f"✅ Finished {json_file} — Total chunks so far: {len(all_chunks)}")

print(f"\n🎯 Completed Embedding Creation for {len(all_chunks)} chunks!\n")

# --------------------------
# 📊 Create & Save DataFrame
# --------------------------
df = pd.DataFrame(all_chunks)
joblib.dump(df, "embeddings.joblib")

print("💾 embeddings.joblib saved successfully!")
