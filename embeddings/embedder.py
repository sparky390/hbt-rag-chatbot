import json
import chromadb
from sentence_transformers import SentenceTransformer

with open("data/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks")

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="chroma_db")

try:
    client.delete_collection("hbt_knowledge")
    print("Dropped existing collection")
except Exception:
    pass

collection = client.create_collection(
    name="hbt_knowledge",
    metadata={"hnsw:space": "cosine"},
)

texts = [c["content"] for c in chunks]
print("Generating embeddings...")
embeddings = model.encode(texts, show_progress_bar=True).tolist()

collection.add(
    ids=[str(i) for i in range(len(chunks))],
    documents=texts,
    embeddings=embeddings,
    metadatas=[
        {"source": c["source"], "chunk_id": c["chunk_id"]}
        for c in chunks
    ],
)

print(f"\n✓ Stored {len(chunks)} chunks in ChromaDB → chroma_db/")