import json
import os
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import chromadb

BASE_DIR = r"C:\Users\Shreya\PycharmProjects\movie_query_rag"

#HARD-LOCKED PATHS
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")
JSON_PATH = os.path.join(BASE_DIR, "scripts", "movies.json")

print("Using JSON from:", JSON_PATH)
print("Using Chroma DB at:", CHROMA_PATH)

#load JSON
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# convert records to text
texts = []
ids = []

for row in data:
    text = f"""
Title: {row['title']}
Director: {row['director']}
Release Date: {row['release_date']}
Money Made (USD): {int(row['money_made'])}
"""
    texts.append(text.strip())
    ids.append(str(row["id"]))

# load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=CHROMA_PATH)

#create or load collection safely
collection = client.get_or_create_collection(name="movies")

#embed and store
for i in tqdm(range(len(texts))):
    emb = model.encode(texts[i]).tolist()
    collection.add(
        ids=[ids[i]],
        documents=[texts[i]],
        embeddings=[emb]
    )

print("All movies embedded and stored in Chroma DB successfully!")
