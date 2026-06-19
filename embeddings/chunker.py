import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

INPUT_FOLDER = "data/raw"
OUTPUT_FILE = "data/chunks.json"

all_chunks = []

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

for filename in os.listdir(INPUT_FOLDER):

    if filename.endswith(".txt"):

        file_path = os.path.join(
            INPUT_FOLDER,
            filename
        )

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            text = f.read()

        chunks = splitter.split_text(text)

        for chunk in chunks:

            all_chunks.append({
                "source": filename,
                "content": chunk
            })

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_chunks,
        f,
        indent=2
    )

print(
    f"Created {len(all_chunks)} chunks"
)