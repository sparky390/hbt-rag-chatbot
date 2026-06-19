"""
Structure-aware chunker for the HBT knowledge base.
"""

import os
import json
import re
from typing import List, Dict, Optional

INPUT_FOLDER = "data/processed"
OUTPUT_FILE = "data/chunks.json"

MAX_CHUNK_CHARS = 1400
MIN_CHUNK_WORDS = 8

HEADING_RE = re.compile(r"^(#{2,4})\s+(.*)$")

KNOWN_TYPO_FIXES = {
    "Strategic Product Suport": "Strategic Product Support",
}


def fix_known_typos(text: str) -> str:
    for wrong, right in KNOWN_TYPO_FIXES.items():
        text = text.replace(wrong, right)
    return text


BOILERPLATE_PATTERNS = [
    re.compile(r"^how can we help you\??$", re.IGNORECASE),
    re.compile(r"^do you have questions about our services", re.IGNORECASE),
    re.compile(r"^please feel free to contact us\.?$", re.IGNORECASE),
    re.compile(r"^do you need an individual offer", re.IGNORECASE),
]

CATEGORY_INTRO_RE = re.compile(
    r"(our services|services? (we|will) (offer|be)|service categories|"
    r"our (capabilities|offerings)|what we offer)",
    re.IGNORECASE,
)


class Section:
    __slots__ = ("level", "title", "lines", "parent_path")

    def __init__(self, level: int, title: str, parent_path: List[str]):
        self.level = level
        self.title = title
        self.lines: List[str] = []
        self.parent_path = parent_path

    @property
    def path(self) -> str:
        return " > ".join(self.parent_path + [self.title]) if self.title else " > ".join(self.parent_path)

    @property
    def text(self) -> str:
        return "\n".join(self.lines).strip()


def is_boilerplate(line: str) -> bool:
    stripped = line.strip()
    return any(p.search(stripped) for p in BOILERPLATE_PATTERNS)


def parse_sections(text: str) -> List[Section]:
    sections: List[Section] = []
    stack: List[str] = []
    level_stack: List[int] = []

    current = Section(level=1, title="", parent_path=[])
    sections.append(current)

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if is_boilerplate(line):
            continue

        m = HEADING_RE.match(line.strip())
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()

            while level_stack and level_stack[-1] >= level:
                level_stack.pop()
                stack.pop()

            parent_path = list(stack)
            current = Section(level=level, title=title, parent_path=parent_path)
            sections.append(current)

            stack.append(title)
            level_stack.append(level)
        else:
            line_text = re.sub(r"^[•\-]\s*", "• ", line.strip())
            current.lines.append(line_text)

    return [s for s in sections if s.text or s.title]


def chunk_section(section: Section) -> List[str]:
    body = section.text
    if len(body) <= MAX_CHUNK_CHARS:
        return [body] if body else []

    paragraphs = re.split(r"\n(?=•\s)|\n\n", body)
    pieces, current_piece = [], ""
    for para in paragraphs:
        if len(current_piece) + len(para) + 1 <= MAX_CHUNK_CHARS:
            current_piece = f"{current_piece}\n{para}".strip()
        else:
            if current_piece:
                pieces.append(current_piece)
            current_piece = para
    if current_piece:
        pieces.append(current_piece)
    return pieces


def build_service_index(sections: List[Section], doc_title: str) -> Optional[Dict]:
    for i, section in enumerate(sections):
        if not section.title or not CATEGORY_INTRO_RE.search(section.title):
            continue

        this_path = section.parent_path + [section.title]
        children = []
        for other in sections[i + 1:]:
            if other.parent_path == this_path:
                if other.text:
                    children.append(other.title)
            elif len(other.parent_path) < len(this_path):
                break

        if len(children) >= 2:
            bullet_list = "\n".join(f"• {c}" for c in children)
            content = (
                f"{doc_title} — {section.title}\n"
                f"The complete list of service categories is:\n{bullet_list}"
            )
            return {
                "content": content,
                "heading_path": " > ".join(this_path),
                "section_type": "service_index",
            }
    return None


def get_doc_title(sections: List[Section]) -> str:
    for s in sections:
        if s.level <= 3 and s.title:
            return s.title
    return ""


def process_file(filename: str) -> List[Dict]:
    path = os.path.join(INPUT_FOLDER, filename)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    text = fix_known_typos(text)

    if len(text.split()) < 20:
        print(f"  ⚠ Skipping (too short): {filename}")
        return []

    sections = parse_sections(text)
    doc_title = get_doc_title(sections)
    chunks: List[Dict] = []

    index_chunk = build_service_index(sections, doc_title)
    if index_chunk:
        chunks.append({**index_chunk, "doc_title": doc_title})

    for section in sections:
        pieces = chunk_section(section)
        for piece in pieces:
            if len(piece.split()) < MIN_CHUNK_WORDS:
                continue
            breadcrumb = section.path
            prefixed = f"{breadcrumb}\n{piece}" if breadcrumb else piece
            chunks.append({
                "content": prefixed,
                "heading_path": breadcrumb,
                "section_type": "content",
                "doc_title": doc_title,
            })

    for idx, c in enumerate(chunks):
        c["source"] = filename
        c["chunk_id"] = idx

    return chunks


def main():
    all_chunks: List[Dict] = []

    if not os.path.isdir(INPUT_FOLDER):
        print(f"Folder not found: {INPUT_FOLDER}")
        return

    for filename in sorted(os.listdir(INPUT_FOLDER)):
        if not filename.endswith(".txt"):
            continue
        file_chunks = process_file(filename)
        all_chunks.extend(file_chunks)
        n_index = sum(1 for c in file_chunks if c["section_type"] == "service_index")
        tag = " (+1 service index)" if n_index else ""
        print(f"  ✓ {len(file_chunks):>3} chunks ← {filename}{tag}")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=4, ensure_ascii=False)

    print(f"\nTotal chunks: {len(all_chunks)} → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()