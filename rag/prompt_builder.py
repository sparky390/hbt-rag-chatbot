import re
from typing import List, Optional, Tuple

NOT_FOUND_MESSAGE = "I could not find relevant information in the knowledge base."

# ── Ordinal words to numeric index (0-based) ────────────────────────────────
_ORDINALS = {
    "first": 0, "1st": 0,
    "second": 1, "2nd": 1,
    "third": 2, "3rd": 2,
    "fourth": 3, "4th": 3,
    "fifth": 4, "5th": 4,
    "sixth": 5, "6th": 5,
    "seventh": 6, "7th": 6,
    "eighth": 7, "8th": 7,
    "ninth": 8, "9th": 8,
    "tenth": 9, "10th": 9,
}

_ORDINAL_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in _ORDINALS) + r")\b",
    re.IGNORECASE,
)

_REFERENCE_TRIGGERS = re.compile(
    r"\b(it|that|this|the\s+(first|second|third|fourth|fifth|sixth|seventh|"
    r"eighth|ninth|tenth|\d+(?:st|nd|rd|th))\s+one|tell\s+me\s+more|"
    r"expand|elaborate|explain\s+more|more\s+about|more\s+details|"
    r"what\s+about\s+(?:the\s+)?(?:first|second|third|fourth|fifth|sixth|"
    r"seventh|eighth|ninth|tenth))\b",
    re.IGNORECASE,
)

_PRONOUN_ONLY_RE = re.compile(r"\b(it|that|this)\b", re.IGNORECASE)


def _extract_list_items(text: str) -> List[str]:
    """Pull bullet/numbered items out of an assistant answer."""
    items = []
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"^[*\-•]\s+(.+)", line)
        if m:
            items.append(m.group(1).strip())
            continue
        m = re.match(r"^\d+[.)]\s+(.+)", line)
        if m:
            items.append(m.group(1).strip())
    return items


def resolve_reference(
    question: str,
    last_answer: str,
    last_resolved_topic: Optional[str] = None,
    reference_list: Optional[List[str]] = None,  # NEW: persisted list from enumeration
) -> str:
    """
    Resolve vague references in `question` to a concrete topic.

    Priority order:
    1. Explicit ordinal + reference_list  → use the PERSISTED list (e.g. from Q1)
    2. Explicit ordinal + last_answer     → extract list from the last answer
    3. Pronoun + last_resolved_topic      → reuse the previously resolved topic
    4. No match                           → return question unchanged

    The key insight: after Q1 returns a list and Q2 narrows to one topic,
    Q3's "second one" must resolve against Q1's list — not Q2's single-topic
    answer. `reference_list` holds Q1's list persistently across turns.
    """
    if not _REFERENCE_TRIGGERS.search(question) and not _PRONOUN_ONLY_RE.search(question):
        return question

    # ── Case 1 & 2: explicit ordinal ─────────────────────────────────────────
    m = _ORDINAL_RE.search(question)
    if m:
        idx = _ORDINALS.get(m.group(1).lower())
        if idx is not None:
            # Prefer the persisted list; fall back to parsing the last answer
            items = reference_list if reference_list else _extract_list_items(last_answer)
            if items and idx < len(items):
                target = items[idx]
                resolved = _ORDINAL_RE.sub(target, question, count=1)
                resolved = re.sub(
                    r"\b(the\s+)" + re.escape(target) + r"\s+one\b",
                    r"\g<1>" + target, resolved, flags=re.IGNORECASE,
                )
                return resolved.strip()

    # ── Case 3: pronoun + known topic ────────────────────────────────────────
    if last_resolved_topic and _PRONOUN_ONLY_RE.search(question):
        resolved = _PRONOUN_ONLY_RE.sub(last_resolved_topic, question, count=1)
        return resolved.strip()

    # ── Case 4: trigger phrase, no list, but topic known ─────────────────────
    if last_resolved_topic and _REFERENCE_TRIGGERS.search(question):
        items = reference_list if reference_list else _extract_list_items(last_answer)
        if not items:
            return f"{question} about {last_resolved_topic}"

    return question


def build_context_block(documents, metadatas) -> str:
    parts = []
    for doc, meta in zip(documents, metadatas):
        label = meta.get("doc_title") or meta.get("source", "Unknown source")
        heading = meta.get("heading_path", "")
        header = f"[Source: {label}" + (f" | Section: {heading}]" if heading else "]")
        parts.append(f"{header}\n{doc}")
    return "\n\n---\n\n".join(parts)


def build_prompt(
    question: str,
    context: str,
    enumeration: bool = False,
    history: Optional[List[Tuple[str, str]]] = None,
    resolved_question: Optional[str] = None,
) -> str:
    completeness_hint = (
        "\n- This question asks for a full list/category enumeration. "
        "Check EVERY [Source: ...] block above and include every distinct "
        "item mentioned across ALL of them — do not stop after the first "
        "block or summarize down to a partial subset."
        if enumeration else ""
    )

    history_block = ""
    if history:
        last_q, last_a = history[-1]
        history_block = (
            f"\nPREVIOUS EXCHANGE (use ONLY to resolve references like "
            f"\"it\", \"that\", \"the first one\" — never as a source of facts):\n"
            f"User: {last_q}\nAssistant: {last_a}\n"
        )

    topic_hint = ""
    if resolved_question and resolved_question != question:
        topic_hint = (
            f"\nNOTE: The user's question refers to \"{resolved_question.strip()}\" "
            f"based on the previous exchange. Answer about that specific topic.\n"
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
{history_block}{topic_hint}
CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""