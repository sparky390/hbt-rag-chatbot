from rag.retriever import retrieve_context
from llm.ollama_client import generate_response


def ask_question(question: str) -> str:
    results = retrieve_context(question, top_k=5)

    if not results["documents"][0]:
        return "I could not find relevant information in the knowledge base."

    context_parts = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        source = meta.get("source", "").replace(".txt", "").replace("_", " ")
        context_parts.append(f"[Source: {source}]\n{doc}")

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""You are an AI Knowledge Assistant for HBT Technology Services.

Answer ONLY using the provided context below.
- List services as bullet points when the question asks "what services".
- Be concise and professional.
- Ignore any navigation text, "Click here", or counter numbers in the context.
- Do NOT use outside knowledge.
- If the answer is not in the context, reply: "I could not find relevant information in the knowledge base."

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""

    return generate_response(prompt)