UNWANTED_EXACT = {
    "home", "company", "facts & figures", "management",
    "sustainability", "history", "news", "career", "jobs",
    "contact", "privacy policy", "cookie policy",
    "general terms and conditions", "opt-out preferences",
    "accept", "deny", "view preferences", "save preferences",
    "manage consent", "manage cookie consent", "skip to content",
    "click here", "read more", "learn more", "view all",
}

ALWAYS_NOISE_RE = re.compile(
    r"^(click here|read more|learn more|>+|»|←|→|·)$"
    r"|^(copyright|©)\s*\d{4}"
    r"|^https?://"
    r"|^\d+\s*[+%]?$"
    r"|^•\s*$",
    re.IGNORECASE,
)

SHORT_LINE_NOISE = [
    "cookie", "consent", "opt-out", "manage cookie",
    "save preferences", "gdpr",
]


def should_drop(line: str) -> bool:
    low = line.lower().strip()
    if not low:
        return False
    if low in UNWANTED_EXACT:
        return True
    if ALWAYS_NOISE_RE.search(low):
        return True
    if len(low) <= 120:
        for sub in SHORT_LINE_NOISE:
            if sub in low:
                return True
    return False