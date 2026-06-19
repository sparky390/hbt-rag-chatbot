import subprocess
import shutil
import os

print("=" * 60)
print("HBT RAG Knowledge Base Builder")
print("=" * 60)

# Clean old data
if os.path.exists("chroma_db"):
    print("Removing old ChromaDB...")
    shutil.rmtree("chroma_db")

if os.path.exists("data/chunks.json"):
    print("Removing old chunks...")
    os.remove("data/chunks.json")

steps = [
    ("Crawler", ["python", "scraper/crawler.py"]),
    ("Scraper", ["python", "scraper/scraper.py"]),
    ("Cleaner", ["python", "scraper/cleaner.py"]),
    ("Chunker", ["python", "embeddings/chunker.py"]),
    ("Embedder", ["python", "embeddings/embedder.py"])
]

for step_name, command in steps:

    print(f"\nRunning {step_name}...")

    result = subprocess.run(command)

    if result.returncode != 0:
        print(f"\nERROR: {step_name} failed.")
        exit(1)

    print(f"{step_name} completed successfully.")

print("\nKnowledge base built successfully!")
print("You can now run:")
print("streamlit run app.py")
print("=" * 60)