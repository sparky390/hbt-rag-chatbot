import uuid
import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "hbt_knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def extract_pdf_text(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages).strip()


def ingest_pdf(uploaded_file, filename: str) -> int:
    """
    Extract, chunk, embed and store PDF into existing ChromaDB collection.
    Returns number of chunks added.
    """
    text = extract_pdf_text(uploaded_file)
    if not text:
        return 0

    chunks = splitter.split_text(text)
    chunks = [c.strip() for c in chunks if len(c.split()) >= 10]

    if not chunks:
        return 0

    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(chunks, show_progress_bar=False).tolist()

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(COLLECTION_NAME)

    collection.add(
        ids=[str(uuid.uuid4()) for _ in chunks],
        documents=chunks,
        embeddings=embeddings,
        metadatas=[
            {
                "source": filename,
                "doc_title": filename.replace(".pdf", "").replace("_", " "),
                "heading_path": "",
                "chunk_id": i,
            }
            for i in range(len(chunks))
        ],
    )

    return len(chunks)