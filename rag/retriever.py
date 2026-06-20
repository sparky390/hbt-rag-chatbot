import re
from typing import Dict, List, Optional

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "hbt_knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

MIN_SIMILARITY = 0.15          # FIX 1: lowered from 0.25 → catches short generic terms
                               # like "Engineering Services" that score 0.18–0.22
DEFAULT_TOP_K = 5
DEFAULT_FETCH_K = 20
MAX_PER_SOURCE = 3

ENUMERATION_RE = re.compile(
    r"\b(what services|list|all (the )?services|categories|"
    r"what (do|does) .* offer|what (can|do) you (offer|provide|do)|"
    r"overview|everything (you|hbt) (do|offer))\b",
    re.IGNORECASE,
)

_model: Optional[SentenceTransformer] = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def warmup():
    """Preload embedding and vector store resources at startup."""
    _get_model()
    _get_collection()


def _distance_to_similarity(distance: float) -> float:
    similarity = 1.0 - distance
    return max(0.0, min(1.0, similarity))


def is_enumeration_query(question: str) -> bool:
    return bool(ENUMERATION_RE.search(question))


def retrieve_context(
    question: str,
    top_k: int = DEFAULT_TOP_K,
    fetch_k: int = DEFAULT_FETCH_K,
    max_per_source: int = MAX_PER_SOURCE,
    min_similarity: float = MIN_SIMILARITY,
) -> Dict:
    collection = _get_collection()
    model = _get_model()

    embedding = model.encode(question).tolist()

    raw = collection.query(
        query_embeddings=[embedding],
        n_results=fetch_k,
        include=["documents", "metadatas", "distances"],
    )

    docs = raw["documents"][0] if raw["documents"] else []
    metas = raw["metadatas"][0] if raw["metadatas"] else []
    dists = raw["distances"][0] if raw["distances"] else []

    candidates = []
    for doc, meta, dist in zip(docs, metas, dists):
        similarity = _distance_to_similarity(dist)
        if similarity < min_similarity:
            continue
        candidates.append({
            "document": doc,
            "metadata": meta,
            "similarity": similarity,
        })

    if is_enumeration_query(question):
        for c in candidates:
            if c["metadata"].get("section_type") == "service_index":
                c["similarity"] = min(1.0, c["similarity"] + 0.15)

    candidates.sort(key=lambda c: c["similarity"], reverse=True)

    selected: List[Dict] = []
    per_source_count: Dict[str, int] = {}

    for c in candidates:
        if len(selected) >= top_k:
            break
        source = c["metadata"].get("source", "")
        if per_source_count.get(source, 0) >= max_per_source:
            continue
        selected.append(c)
        per_source_count[source] = per_source_count.get(source, 0) + 1

    return {
        "documents": [c["document"] for c in selected],
        "metadatas": [c["metadata"] for c in selected],
        "similarities": [c["similarity"] for c in selected],
    }