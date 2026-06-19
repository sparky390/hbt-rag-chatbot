import os
import re
from typing import Set, List

INPUT_FOLDER = "data/processed"

UNWANTED_EXACT: Set[str] = {
    "home", "company", "facts & figures", "management",
    "sustainability", "history", "news", "career", "jobs",
    "contact", "privacy policy", "cookie policy",
    "general terms and conditions", "opt-out preferences",
    "accept", "deny", "view preferences", "save preferences",
    "manage consent", "manage cookie consent", "skip to content",
    "click here", "read more", "learn more", "view all",
    "technology", "services",
}

ALWAYS_NOISE_RE = re.compile(
    r"^(click here|read more|learn more|>+|»|←|→|·)$"
    r"|^(copyright|©)\s*\d{4}"
    r"|^https?://"
    r"|^\d+\s*[+%]?$"
    r"|^•\s*$",
    re.IGNORECASE,
)

SHORT_LINE_NOISE: List[str] = [
    "cookie", "consent", "opt-out", "manage cookie",
    "save preferences", "gdpr",
]


def should_drop(line: str) -> bool:
    low = line.lower().strip()
    if not low:
        return False
    if low in UNWANTED_EXACT:
        return True
    if low.startswith("products"):
        return True
    if ALWAYS_NOISE_RE.search(low):
        return True
    if len(low) <= 120:
        for sub in SHORT_LINE_NOISE:
            if sub in low:
                return True
    return False


def clean_file(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.splitlines()
    cleaned: List[str] = []
    prev_blank = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if not prev_blank:
                cleaned.append("")
                prev_blank = True
            continue
        if should_drop(stripped):
            prev_blank = False
            continue
        cleaned.append(stripped)
        prev_blank = False

    result = "\n".join(cleaned).strip()
    result = re.sub(r"\n{3,}", "\n\n", result)
    result = re.sub(r"[ \t]+", " ", result)

    with open(path, "w", encoding="utf-8") as f:
        f.write(result + "\n")

    return len(result.split())


def main():
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Folder not found: {INPUT_FOLDER}")
        return

    for filename in sorted(os.listdir(INPUT_FOLDER)):
        if not filename.endswith(".txt"):
            continue
        path = os.path.join(INPUT_FOLDER, filename)
        try:
            words = clean_file(path)
            print(f"  ✓ {words:>5} words → {filename}")
        except Exception as e:
            print(f"  ✗ Failed {filename}: {e}")

    print("\nCleaning complete!")


if __name__ == "__main__":
    main()