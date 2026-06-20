from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from rag.retriever import retrieve_context, is_enumeration_query, warmup
from rag.prompt_builder import build_context_block, build_prompt, NOT_FOUND_MESSAGE, resolve_reference
from llm.ollama_client import generate_response

DEFAULT_TOP_K = 5


@dataclass
class Source:
    source_file: str
    doc_title: str
    heading_path: str
    similarity: float


@dataclass
class AnswerResult:
    answer: str
    sources: List[Source] = field(default_factory=list)
    grounded: bool = True
    resolved_topic: Optional[str] = None      # topic resolved this turn (for pronoun chaining)
    reference_list: Optional[List[str]] = None # the bullet list to resolve ordinals against


def _humanize_filename(filename: str) -> str:
    name = filename.replace(".txt", "").replace("_", " ").strip()
    return name[:1].upper() + name[1:] if name else filename


def _build_sources(metadatas: List[dict], similarities: List[float]) -> List[Source]:
    sources: List[Source] = []
    seen = set()
    for meta, sim in zip(metadatas, similarities):
        source_file = meta.get("source", "")
        heading_path = meta.get("heading_path", "")
        key = (source_file, heading_path)
        if key in seen:
            continue
        seen.add(key)
        sources.append(Source(
            source_file=source_file,
            doc_title=meta.get("doc_title") or _humanize_filename(source_file),
            heading_path=heading_path,
            similarity=sim,
        ))
    return sources


def _assemble_context(documents: List[str], metadatas: List[dict]) -> str:
    return build_context_block(documents, metadatas)


def _looks_like_refusal(answer: str) -> bool:
    return NOT_FOUND_MESSAGE.lower() in answer.lower()


def _extract_topic(resolved_question: str, original_question: str) -> Optional[str]:
    """Return the resolved topic string, or None if nothing changed."""
    if resolved_question == original_question:
        return None
    return resolved_question


def ask_question(question: str, top_k: int = DEFAULT_TOP_K) -> str:
    result = ask_question_detailed(question, top_k=top_k)
    return result.answer


def ask_question_detailed(
    question: str,
    top_k: int = DEFAULT_TOP_K,
    history: Optional[List[Tuple[str, str]]] = None,
    last_resolved_topic: Optional[str] = None,
    reference_list: Optional[List[str]] = None,  # NEW: persisted list from enumeration answers
) -> AnswerResult:
    enumeration = is_enumeration_query(question)
    effective_top_k = top_k + 3 if enumeration else top_k

    # Resolve vague references BEFORE retrieval.
    # KEY FIX: if we have a persisted reference_list (from a previous enumeration
    # answer), prefer it over the last answer text — because the last answer may
    # be a single-topic answer that contains no list to parse.
    resolved_question = question
    if history:
        resolved_question = resolve_reference(
            question,
            history[-1][1],
            last_resolved_topic=last_resolved_topic,
            reference_list=reference_list,   # pass the persisted list
        )

    results = retrieve_context(resolved_question, top_k=effective_top_k)

    if not results["documents"]:
        return AnswerResult(
            answer=NOT_FOUND_MESSAGE,
            sources=[],
            grounded=True,
            resolved_topic=last_resolved_topic,
            reference_list=reference_list,   # carry forward unchanged
        )

    context = _assemble_context(results["documents"], results["metadatas"])
    prompt = build_prompt(
        question=question,
        resolved_question=resolved_question,
        context=context,
        enumeration=enumeration,
        history=history,
    )

    answer = generate_response(prompt).strip()

    if _looks_like_refusal(answer):
        return AnswerResult(
            answer=NOT_FOUND_MESSAGE,
            sources=[],
            grounded=True,
            resolved_topic=last_resolved_topic,
            reference_list=reference_list,
        )

    sources = _build_sources(results["metadatas"], results["similarities"])
    new_topic = _extract_topic(resolved_question, question) or last_resolved_topic

    # If this turn was an enumeration answer, extract and persist the list
    # so future ordinal follow-ups can resolve against it correctly.
    new_reference_list = reference_list
    if enumeration:
        from rag.prompt_builder import _extract_list_items
        extracted = _extract_list_items(answer)
        if extracted:
            new_reference_list = extracted

    return AnswerResult(
        answer=answer,
        sources=sources,
        grounded=True,
        resolved_topic=new_topic,
        reference_list=new_reference_list,
    )