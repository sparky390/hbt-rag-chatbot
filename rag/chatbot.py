from rag.retriever import retrieve_context
from llm.ollama_client import generate_response

def ask_question(question):

    results = retrieve_context(
        question,
        top_k=2
    )

    if not results["documents"][0]:
        return "I could not find relevant information in the knowledge base."

    context = "\n\n".join(
        results["documents"][0]
    )

    prompt = f"""
You are an AI Knowledge Assistant for HBT.

Use ONLY the provided context.

When answering:
- Summarize clearly.
- Use bullet points when listing services.
- Ignore navigation menus and website boilerplate.
- Do not use outside knowledge.

If the answer is not present in the context, reply exactly:

I could not find relevant information in the knowledge base.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

    answer = generate_response(prompt)

    return answer