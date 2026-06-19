from typing import List


def retrieve_relevant_docs(query: str, top_k: int = 5):
    """Retrieve the most relevant documents for a query."""
    return [f"Document {i+1}" for i in range(top_k)]
