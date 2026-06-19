# 🤖 HBT AI Knowledge Assistant (RAG Chatbot | ChromaDB / Ollama / Streamlit)
An AI-powered chatbot that answers questions about HBT Technology Services using Retrieval-Augmented Generation (RAG).  
Answers are grounded strictly in scraped website content — no hallucinations, no guessing.

## 🔗 Quick Navigation
- [How It Works](#%EF%B8%8F-how-it-works)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Usage](#-usage)
- [Example Questions](#-example-questions)
- [Architecture](#-architecture)
- [Bonus Features Implemented](#-bonus-features-implemented)
- [Assumptions & Challenges](#-assumptions--challenges)
- [Notes](#-notes)

---

## ⚙️ How It Works

1. Scrape the HBT Technology Services website (multiple pages)
2. Clean HTML and extract structured text with heading paths preserved
3. Chunk content and generate sentence embeddings
4. Store vectors in a local ChromaDB database
5. At query time, embed the question and retrieve top-k similar chunks
6. Feed retrieved context into a local Ollama LLM
7. Display the grounded answer with collapsible source citations in Streamlit

---

## ⚡ Features

- 🏠 Fully local — no OpenAI key, no paid APIs, runs entirely on your machine via Ollama
- 🌐 Multi-page scraping — crawls the main page and all linked product/service sub-pages
- 🎯 Grounded answers — explicitly says "I could not find relevant information" instead of hallucinating
- 📄 Source citations — every answer shows document title, heading path, source file, and similarity score
- 💬 Chat history — full conversation memory within a session
- 🧭 Sample questions sidebar — pre-loaded prompts to explore HBT services instantly
- 🧩 Modular architecture — scraper, embeddings, vectordb, RAG, LLM, and UI fully separated

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Frontend / UI | [Streamlit](https://streamlit.io) |
| LLM | [Ollama](https://ollama.com) + Llama 3 (local) |
| Embeddings | [sentence-transformers](https://www.sbert.net) |
| Vector Database | [ChromaDB](https://www.trychroma.com) |
| RAG Orchestration | [LangChain](https://langchain.com) |
| Web Scraping | [BeautifulSoup4](https://beautiful-soup-4.readthedocs.io) + requests |
| Language | Python |
| Version Control | GitHub |

---

## 📁 Project Structure

```
hbt-rag-chatbot/
├── app.py                  # Streamlit entry point
├── requirements.txt
├── scraper/                # Website crawling and HTML cleaning
├── data/                   # Raw scraped content (HTML + clean text + metadata)
├── embeddings/             # Sentence embedding model wrapper
├── vectordb/               # ChromaDB ingestion and vector querying
├── chroma_db/              # Persisted vector store (auto-generated, do not delete)
├── rag/
│   └── chatbot.py          # Core RAG pipeline: ask_question_detailed()
├── llm/                    # Ollama LLM interface
└── ui/                     # Streamlit UI helper components
```

---

## 🚀 Usage

**Prerequisites:** Python 3.9+, [Ollama](https://ollama.com/download) installed and running

```bash
# Pull a local model first
ollama pull llama3

# Clone and install
git clone https://github.com/sparky390/hbt-rag-chatbot.git
cd hbt-rag-chatbot
pip install -r requirements.txt
```

**Step 1 — Scrape the HBT website**
```bash
python -m scraper.scrape
```
Crawls https://hbt-group.com/aftermarket-services/technology-services/ and all linked service pages. Saves raw HTML, clean text, and metadata to `data/`.

**Step 2 — Build the vector store**
```bash
python -m vectordb.ingest
```
Chunks the scraped content, generates embeddings, and persists them to `chroma_db/`.

**Step 3 — Launch the chatbot**
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 💬 Example Questions

- What services does HBT Technology Services offer?
- What industries does HBT serve?
- What analytics capabilities are available?
- What sourcing solutions are offered?
- What digital transformation services are available?
- What is Data as a Service at HBT?
- What automation solutions does HBT provide?
- What consulting services are available?

---

## 🏗️ Architecture

```
Website (hbt-group.com)
        ↓
    Scraper
  (BeautifulSoup4)
        ↓
  Text Processing
  (chunking + cleaning)
        ↓
  Vector Database
    (ChromaDB)
        ↓
    Retriever
(sentence-transformers)
        ↓
       LLM
  (Ollama / Llama 3)
        ↓
  Chat Interface
   (Streamlit)
```

---

## 🌟 Bonus Features Implemented

- ✅ **Multi-page scraping** — crawls the main page and all product/service sub-pages
- ✅ **Citation support** — answers show source document, heading path, and similarity score
- ✅ **Conversation memory** — chat history is retained within a session
- ✅ **Handle unknown questions** — returns "I could not find relevant information in the knowledge base" instead of hallucinating

---

## 📝 Assumptions & Challenges

**Assumptions:**
- Only publicly accessible pages within the HBT website are scraped
- The Ollama LLM and ChromaDB run fully locally — no internet connection needed after setup
- The `chroma_db/` folder persists between sessions and should not be deleted

**Challenges faced:**
- Extracting structured content with heading hierarchy from dynamically nested HTML required careful BeautifulSoup parsing
- Tuning chunk size and overlap to balance retrieval accuracy vs. context length for the local LLM
- Ensuring the RAG pipeline correctly distinguishes between "no relevant content found" vs. low-confidence answers

---

## 🌟 Support & Contribution

If you found this project useful:
- ⭐ Star the repository
- 🍴 Fork and improve it
- 🐛 Report issues or suggest features

Contributions are always welcome!

---

## 🔗 Connect With Me

<p align="center">
  <a href="https://github.com/sparky390">GitHub</a> •
  <a href="https://instagram.com/sparky.fpv">Instagram</a>
</p>

---

## 💬 Feedback

Have ideas or improvements?  
Feel free to open an issue or reach out — would love to see what you build with this! 🤖

---

<p align="center">
  Made with ❤️ by <b>Surya.S</b><br>
  ⚡ Turning scraped pages into smart answers
</p>
