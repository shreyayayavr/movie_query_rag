import os
from chromadb import Settings
import chromadb

BASE_DIR = r"C:\Users\Shreya\PycharmProjects\movie_query_rag"
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

print("BASE_DIR exists:", os.path.exists(BASE_DIR))
print("CHROMA_PATH:", CHROMA_PATH)

# Create client
client = chromadb.Client(
    Settings(persist_directory=CHROMA_PATH)
)

# Force create collection
collection = client.get_or_create_collection(name="test_debug")

# Force add one record
collection.add(
    documents=["debug document"],
    ids=["1"]
)

print("After write, CHROMA_PATH exists:", os.path.exists(CHROMA_PATH))

# List directory contents
if os.path.exists(BASE_DIR):
    print("\nFiles inside BASE_DIR:")
    print(os.listdir(BASE_DIR))

if os.path.exists(CHROMA_PATH):
    print("\nFiles inside CHROMA_PATH:")
    print(os.listdir(CHROMA_PATH))
