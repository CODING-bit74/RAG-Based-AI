import requests
import os
import json
import re
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# --------------------------
# 🧩 Function: Create Embedding
# --------------------------
def create_embedding(text):
    response = requests.post("http://localhost:11434/api/embeddings", json={
        "model": "bge-m3",
        "prompt": text
    })
    embedding = response.json()["embedding"]
    return embedding


# --------------------------
# 📂 Setup JSON Folder
# --------------------------
json_folder = "jsons"
json_files = [f for f in os.listdir(json_folder) if f.endswith(".json")]

# Sort files numerically (e.g., video1, video2, video10)
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
            continue  # skip empty chunks

        embedding = create_embedding(text)

        chunk["chunk_id"] = chunk_id
        chunk["embedding"] = embedding
        chunk["number"] = video_number

        all_chunks.append(chunk)
        chunk_id += 1

print(f"\n✅ Completed Embedding Creation for {len(all_chunks)} chunks!\n")

# --------------------------
# 📊 Create DataFrame
# --------------------------
df = pd.DataFrame(all_chunks)
print(df.head())
print("\n✅ DataFrame created successfully!\n")

# --------------------------
# 🔍 Query Input
# --------------------------
incoming_query = input("Enter your query: ")
query_embedding = create_embedding(incoming_query)
print("\n✅ Query Embedding Created!\n")

# --------------------------
# 🧮 Cosine Similarity
# --------------------------
similarity = cosine_similarity(np.vstack(df['embedding']), [query_embedding]).flatten()
top_result = 3
max_indices = similarity.argsort()[::-1][:top_result]
new_df = df.iloc[max_indices]

print("🎯 Top Matches:")
print(new_df[["title", "number", "text"]])
