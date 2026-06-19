from llm.ollama_client import query_model
from rag.prompt_builder import build_prompt
from rag.retriever import retrieve_relevant_docs


def chat(query: str):
    context = retrieve_relevant_docs(query)
    prompt = build_prompt(query, context)
    return query_model(prompt)
