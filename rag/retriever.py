import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("hbt_knowledge")


def retrieve_context(question: str, top_k: int = 5):
    embedding = model.encode(question).tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    if not results["distances"] or not results["distances"][0]:
        return None

    if results["distances"][0][0] > 1.0:
        return None

    return results