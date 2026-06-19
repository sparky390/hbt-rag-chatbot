import re

INPUT_FILE = "data/raw/technology_services.txt"
OUTPUT_FILE = "data/processed/clean_text.txt"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    text = f.read()

# Remove excessive blank lines
text = re.sub(r"\n{2,}", "\n", text)

# Remove common unwanted phrases
unwanted = [
    "Manage Cookie Consent",
    "Cookie Policy",
    "Accept",
    "Deny",
    "View preferences",
    "Manage consent",
    "Skip to content",
]

for item in unwanted:
    text = text.replace(item, "")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(text)

print("Cleaned text saved.")