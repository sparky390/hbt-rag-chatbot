from dataclasses import dataclass, field
from typing import Dict, List

from rag.retriever import retrieve_context, is_enumeration_query
from rag.prompt_builder import build_context_block, build_prompt, NOT_FOUND_MESSAGE
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


def ask_question(question: str, top_k: int = DEFAULT_TOP_K) -> str:
    result = ask_question_detailed(question, top_k=top_k)
    return result.answer


def ask_question_detailed(question: str, top_k: int = DEFAULT_TOP_K) -> AnswerResult:
    enumeration = is_enumeration_query(question)
    effective_top_k = top_k + 3 if enumeration else top_k

    results = retrieve_context(question, top_k=effective_top_k)

    if not results["documents"]:
        return AnswerResult(answer=NOT_FOUND_MESSAGE, sources=[], grounded=True)

    context = _assemble_context(results["documents"], results["metadatas"])
    prompt = build_prompt(question, context, enumeration)

    answer = generate_response(prompt).strip()

    if _looks_like_refusal(answer):
        return AnswerResult(answer=NOT_FOUND_MESSAGE, sources=[], grounded=True)

    sources = _build_sources(results["metadatas"], results["similarities"])
    return AnswerResult(answer=answer, sources=sources, grounded=True)