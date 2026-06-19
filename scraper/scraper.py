import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime

URL = "https://hbt-group.com/aftermarket-services/technology-services/"

response = requests.get(URL)

# Create folders
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("data/metadata", exist_ok=True)

# 1. Save Raw HTML
with open(
    "data/raw/technology_services.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(response.text)

# Parse HTML
soup = BeautifulSoup(response.text, "html.parser")

# 2. Extract Clean Text
text = soup.get_text(
    separator="\n",
    strip=True
)

with open(
    "data/processed/technology_services.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write(text)

# 3. Save Metadata
metadata = {
    "url": URL,
    "title": soup.title.text if soup.title else "No Title",
    "scraped_at": str(datetime.now()),
    "content_length": len(text)
}

with open(
    "data/metadata/technology_services.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(metadata, f, indent=4)

print("Scraping completed successfully!")