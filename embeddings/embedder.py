import json
import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = "data/chunks.json"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "hbt_knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def main():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks")

    model = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        client.delete_collection(COLLECTION_NAME)
        print("Dropped existing collection")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [c["content"] for c in chunks]
    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    metadatas = []
    for c in chunks:
        metadatas.append({
            "source": c.get("source", ""),
            "chunk_id": c.get("chunk_id", 0),
            "heading_path": c.get("heading_path", "") or "",
            "section_type": c.get("section_type", "content") or "content",
            "doc_title": c.get("doc_title", "") or "",
        })

    collection.add(
        ids=[str(i) for i in range(len(chunks))],
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"\n✓ Stored {len(chunks)} chunks in ChromaDB → {CHROMA_PATH}/")


if __name__ == "__main__":
    main()