NOT_FOUND_MESSAGE = "I could not find relevant information in the knowledge base."


def build_context_block(documents, metadatas) -> str:
    parts = []
    for doc, meta in zip(documents, metadatas):
        label = meta.get("doc_title") or meta.get("source", "Unknown source")
        heading = meta.get("heading_path", "")
        header = f"[Source: {label}" + (f" | Section: {heading}]" if heading else "]")
        parts.append(f"{header}\n{doc}")
    return "\n\n---\n\n".join(parts)


def build_prompt(question: str, context: str, enumeration: bool = False) -> str:
    completeness_hint = (
        "\n- This question asks for a full list/category enumeration. "
        "Check EVERY [Source: ...] block above and include every distinct "
        "item mentioned across ALL of them — do not stop after the first "
        "block or summarize down to a partial subset."
        if enumeration else ""
    )
    return f"""You are an AI Knowledge Assistant for HBT Technology Services.

Answer the question using ONLY the information in CONTEXT below.

Rules:
- Do NOT use any outside knowledge. Do NOT invent, infer, or assume facts that are not explicitly present in CONTEXT.
- If the question asks "what services" or for a list/category of things, enumerate every distinct item found across the ENTIRE context as bullet points, not just the first one mentioned.
- Treat each [Source: ...] block as a distinct piece of evidence; merge overlapping or duplicate items, but never drop an item that only appears in one block.{completeness_hint}
- Ignore navigation text, "Click here", stray numbers/counters, or other non-substantive fragments if they appear in the context.
- Be concise, factual, and professional. Do not pad the answer with generic marketing language that isn't in the context.
- If CONTEXT does not contain the answer, respond with EXACTLY this sentence and nothing else: "{NOT_FOUND_MESSAGE}"

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""