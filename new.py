import requests
import os
import json
import re
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import joblib



def create_embedding(text):
    response = requests.post("http://localhost:11434/api/embeddings", json={
        "model": "bge-m3",
        "prompt": text
    })
    embedding = response.json()["embedding"]
    return embedding

json_folder = "jsons"

# ✅ List only JSON files
json_files = [f for f in os.listdir(json_folder) if f.endswith(".json")]

# ✅ Sort files by numeric part safely
def extract_number(filename):
    match = re.search(r"\d+", filename)
    return int(match.group(0)) if match else float('inf')  # files without numbers go last

json_files = sorted(json_files, key=extract_number)

all_chunks = []
chunk_id = 0

# Process only the first JSON file
json_file = json_files[0]
with open(os.path.join(json_folder, json_file), "r", encoding="utf-8") as f:
    content = json.load(f)

raw_number = content.get("video_number", os.path.splitext(json_file)[0])
match = re.search(r"\d+", str(raw_number))
video_number = match.group(0).zfill(3) if match else "unknown"

print(f"🎬 Creating Embeddings for {json_file} (Video {video_number})...")

# Process only the first 5 chunks
for i, chunk in enumerate(content["chunks"]):

    text = chunk["text"]
    embedding = create_embedding(text)

    chunk["chunk_id"] = chunk_id
    chunk["embedding"] = embedding
    chunk["number"] = video_number
    all_chunks.append(chunk)
    chunk_id += 1



df = pd.DataFrame(all_chunks)
# save this data frame
joblib.dump(df, "embeddings.joblib")
# print("\n✅ Embeddings created in proper numeric sequence!\n")


# incoming_query = input("Enter your query: ")
# query_embedding = create_embedding(incoming_query)
# print("\n✅ Query Embedding Created!\n")


# # find cosine similarity between query and all embeddings
# similarity = cosine_similarity(np.vstack(df['embedding']),[query_embedding]).flatten()
# print(similarity)
# top_result =3
# max_indices=similarity.argsort()[::-1][0:top_result]
# print(max_indices)
# new_df=df.iloc[max_indices]
# print(new_df[["title", "number", "text",]])




