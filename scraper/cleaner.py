import os
import re
from typing import Set, List

INPUT_FOLDER = "data/processed"

# Exact unwanted lines (lowercased for case-insensitive exact matches)
UNWANTED_EXACT: Set[str] = {
    "home",
    "company",
    "facts & figures",
    "management",
    "sustainability",
    "history",
    "news",
    "career",
    "jobs",
    "contact",
    "privacy policy",
    "cookie policy",
    "general terms and conditions",
    "opt-out preferences",
    "accept",
    "deny",
    "view preferences",
    "save preferences",
    "manage consent",
    "manage cookie consent",
    "skip to content",
}

# Short-line substrings that indicate navigation/consent lines.
# These are applied only for relatively short lines to avoid removing
# legitimate longer paragraphs that mention these words.
UNWANTED_SUBSTRINGS: List[str] = [
    "cookie",
    "consent",
    "privacy",
    "terms",
    "opt-out",
    "preferences",
    "accept",
    "deny",
    "manage",
    "save",
]


def should_drop_line(line: str) -> bool:
    """Decide whether to drop a line.

    - Exact (case-insensitive) matches are dropped.
    - Short lines (<= 60 chars) containing any unwanted substring are dropped.
    """
    low = line.lower().strip()
    if not low:
        return False

    if low in UNWANTED_EXACT:
        return True

    if low.startswith("products"):
        return True

    # Only apply substring matching to short lines
    if len(low) <= 120:
        for sub in UNWANTED_SUBSTRINGS:
            if sub in low:
                return True

    return False


def clean_file(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.splitlines()

    cleaned_lines: List[str] = []
    prev_blank = False

    for line in lines:
        stripped = line.strip()

        # Preserve a single blank line between paragraphs
        if not stripped:
            if not prev_blank:
                cleaned_lines.append("")
                prev_blank = True
            continue

        if should_drop_line(stripped):
            continue

        cleaned_lines.append(stripped)
        prev_blank = False

    text = "\n".join(cleaned_lines).strip()

    # Normalize multiple blank lines to a single blank line
    text = re.sub(r"\n{2,}", "\n\n", text)

    # Normalize multiple spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text + "\n")


def main() -> None:
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Input folder not found: {INPUT_FOLDER}")
        return

    for filename in os.listdir(INPUT_FOLDER):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(INPUT_FOLDER, filename)

        try:
            clean_file(path)
            print(f"Cleaned: {filename}")
        except Exception as e:
            print(f"Failed to clean {filename}: {e}")

    print("\nCleaning completed successfully!")


if __name__ == "__main__":
    main()