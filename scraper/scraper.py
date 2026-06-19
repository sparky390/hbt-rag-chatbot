import requests
from bs4 import BeautifulSoup
import os

URL = "https://hbt-group.com/aftermarket-services/technology-services/"

response = requests.get(URL)

soup = BeautifulSoup(response.text, "html.parser")

text = soup.get_text(separator="\n", strip=True)

os.makedirs("data/raw", exist_ok=True)

with open("data/raw/technology_services.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Website scraped successfully!")