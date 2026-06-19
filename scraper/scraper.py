import requests
import os
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime
from crawler import get_service_links

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("data/metadata", exist_ok=True)

# Only remove by tag name — class-based removal was too aggressive
# and was deleting Elementor content wrappers along with noise
NOISE_TAGS = [
    "script", "style", "noscript", "iframe",
    "nav", "header", "footer", "aside", "form",
    "button", "svg", "canvas",
]

TEXT_NOISE_PATTERNS = re.compile(
    r"^(click here|read more|learn more|>|»|←|→|\d+\s*[+%]?)$",
    re.IGNORECASE,
)

# Elementor page content — HBT site uses this
CONTENT_SELECTORS = [
    "[data-elementor-type='wp-page']",
    "main#content",
    "main",
    "article",
    "[class*='entry-content']",
    "[class*='post-content']",
    "[class*='elementor-section-wrap']",
    "div#content",
    "div#primary",
    "div.content",
]


def remove_noise(soup):
    """Remove noise tags only — collect first to avoid iterator crash."""
    to_remove = []
    for tag in soup.find_all(NOISE_TAGS):
        to_remove.append(tag)
    for tag in to_remove:
        try:
            tag.decompose()
        except Exception:
            pass


def find_content_zone(soup):
    """Try semantic selectors, then density scoring."""
    for selector in CONTENT_SELECTORS:
        try:
            zone = soup.select_one(selector)
            if zone and len(zone.get_text(strip=True).split()) > 30:
                return zone, selector
        except Exception:
            continue

    # Density scoring: most content words per HTML byte, penalise link-heavy blocks
    best, best_score = None, 0.0
    for tag in soup.find_all(["div", "section"]):
        html_len = len(str(tag))
        if html_len < 300:
            continue
        words = len(tag.get_text().split())
        if words < 30:
            continue
        links = len(tag.find_all("a"))
        score = (words / html_len) - max(0, links - 5) * 0.05
        if score > best_score:
            best_score, best = score, tag

    return (best, "density-scored") if best else (soup.find("body"), "body-fallback")


def extract_clean_text(zone):
    """Extract structured plain text from content zone."""
    if not zone:
        return ""

    lines = []
    seen = set()

    for elem in zone.find_all(
        ["h1", "h2", "h3", "h4", "p", "li", "td", "th"], recursive=True
    ):
        text = re.sub(r"\s+", " ", elem.get_text(separator=" ", strip=True))

        if not text or len(text) < 8:
            continue

        if TEXT_NOISE_PATTERNS.match(text):
            continue

        key = text.lower()
        if key in seen:
            continue
        seen.add(key)

        tag = elem.name
        if tag == "h1":
            lines.append(f"\n## {text}")
        elif tag == "h2":
            lines.append(f"\n### {text}")
        elif tag in ("h3", "h4"):
            lines.append(f"\n#### {text}")
        elif tag == "li":
            lines.append(f"• {text}")
        else:
            lines.append(text)

    return "\n".join(lines).strip()


urls = get_service_links()
print(f"Found {len(urls)} URLs\n")

for index, url in enumerate(urls):
    try:
        print(f"Scraping: {url}")

        response = requests.get(
            url, timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.text.strip() if soup.title else f"page_{index}"
        file_name = re.sub(r"[^a-z0-9_]", "_", title.lower())
        file_name = re.sub(r"_+", "_", file_name).strip("_")[:80]

        # Save raw HTML before any modification
        with open(f"data/raw/{file_name}.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        # Remove only tag-based noise, then extract
        remove_noise(soup)
        zone, method = find_content_zone(soup)
        text = extract_clean_text(zone)

        if len(text.split()) < 20:
            print(f"  Warning: very little content extracted via '{method}'")
        else:
            print(f"  ✓ {len(text.split())} words via '{method}' → {file_name}")

        with open(f"data/processed/{file_name}.txt", "w", encoding="utf-8") as f:
            f.write(text)

        metadata = {
            "url": url,
            "title": title,
            "scraped_at": str(datetime.now()),
            "content_length": len(text),
            "word_count": len(text.split()),
            "extraction_method": method,
        }
        with open(f"data/metadata/{file_name}.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"  ✗ Failed: {url} — {e}")

print("\nScraping complete!")