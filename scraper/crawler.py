import requests
from bs4 import BeautifulSoup


def crawl_site(base_url, max_pages=50):
    """Crawl HBT pages and collect URLs to scrape."""
    urls = {base_url}
    visited = set()

    while urls and len(visited) < max_pages:
        url = urls.pop()
        visited.add(url)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith("http") and "hbt" in href:
                if href not in visited:
                    urls.add(href)

    return list(visited)
