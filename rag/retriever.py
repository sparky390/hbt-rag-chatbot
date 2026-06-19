import chromadb

from sentence_transformers import (
    SentenceTransformer
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_collection(
    "hbt_knowledge"
)

def retrieve_context(
    question,
    top_k=5
):

    question_embedding = model.encode(
        question
    ).tolist()

    results = collection.query(
        query_embeddings=[
            question_embedding
        ],
        n_results=top_k
    )

    return results