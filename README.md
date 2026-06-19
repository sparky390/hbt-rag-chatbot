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

1. **Crawl** — discover all service sub-pages under the HBT Technology Services URL
2. **Scrape** — download raw HTML and extract structured text with heading hierarchy preserved
3. **Clean** — strip boilerplate, cookie banners, nav noise, and duplicate lines
4. **Chunk** — split content into structure-aware chunks with breadcrumb heading paths
5. **Embed** — generate dense vector embeddings using `all-MiniLM-L6-v2`
6. **Store** — persist embeddings in a local ChromaDB collection
7. **Retrieve** — at query time, embed the question and fetch top-k similar chunks
8. **Generate** — feed retrieved context into Ollama (`gemma3:4b`) with a strict grounding prompt
9. **Display** — render the answer with collapsible source citations in Streamlit

---

## ⚡ Features

- 🏠 Fully local — no OpenAI key, no paid APIs, runs entirely on your machine via Ollama
- 🌐 Multi-page scraping — crawls the main page and all 6 linked service sub-pages (7 pages total)
- 🎯 Grounded answers — explicitly returns *"I could not find relevant information in the knowledge base."* instead of hallucinating
- 📄 Source citations — every answer shows document title, heading path, source file, and similarity score
- 💬 Chat history — full conversation memory within a session
- 🧭 Sample questions sidebar — pre-loaded prompts to explore HBT services instantly
- 🔍 Smart retrieval — enumeration queries (e.g. "list all services") get boosted `service_index` chunks for complete answers
- 🧩 Modular architecture — crawler, scraper, cleaner, chunker, embedder, retriever, LLM, and UI all in separate modules

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Frontend / UI | [Streamlit](https://streamlit.io) |
| LLM | [Ollama](https://ollama.com) + `gemma3:4b` (local) |
| Embeddings | `all-MiniLM-L6-v2` via [sentence-transformers](https://www.sbert.net) |
| Vector Database | [ChromaDB](https://www.trychroma.com) (cosine similarity, persistent) |
| Web Scraping | [BeautifulSoup4](https://beautiful-soup-4.readthedocs.io) + requests |
| Language | Python 3.9+ |
| Version Control | GitHub |

---

## 📁 Project Structure

```
hbt-rag-chatbot/
├── app.py                      # Streamlit entry point
├── run_pipeline.py             # One-command pipeline runner (scrape → embed)
├── requirements.txt
│
├── scraper/
│   ├── crawler.py              # Discovers all service page URLs
│   ├── scraper.py              # Downloads HTML, extracts + saves text & metadata
│   └── cleaner.py              # Post-processes text (removes boilerplate, dedup)
│
├── embeddings/
│   ├── chunker.py              # Structure-aware chunking with heading breadcrumbs
│   └── embedder.py             # Generates embeddings and stores in ChromaDB
│
├── rag/
│   ├── retriever.py            # Vector search with similarity filtering & source diversity
│   ├── prompt_builder.py       # Builds grounding prompt; defines NOT_FOUND_MESSAGE
│   └── chatbot.py              # ask_question_detailed() — main RAG entry point
│
├── llm/
│   └── ollama_client.py        # Calls Ollama chat API (model: gemma3:4b)
│
├── vectordb/
│   └── chroma_manager.py       # ChromaDB client helpers
│
├── data/
│   ├── raw/                    # Raw HTML per page
│   ├── processed/              # Cleaned plain text per page
│   ├── metadata/               # JSON metadata per page (URL, word count, etc.)
│   └── chunks.json             # All chunks before embedding
│
├── chroma_db/                  # Persisted ChromaDB vector store (auto-generated)
└── ui/
    └── components.py           # Streamlit header/footer helpers
```

---

## 🚀 Usage

**Prerequisites:** Python 3.9+, [Ollama](https://ollama.com/download) installed and running

```bash
# Pull the model used by this project
ollama pull gemma3:4b

# Clone and install
git clone https://github.com/sparky390/hbt-rag-chatbot.git
cd hbt-rag-chatbot
pip install -r requirements.txt
```

**Option A — Run the full pipeline in one command**
```bash
python run_pipeline.py
```
This runs crawler → scraper → cleaner → chunker → embedder in sequence, then prints a reminder to launch the app.

**Option B — Run each step individually**

```bash
# Step 1: Discover and scrape all pages
python scraper/crawler.py     # see discovered URLs
python scraper/scraper.py     # download + extract text → data/

# Step 2: Clean extracted text
python scraper/cleaner.py

# Step 3: Chunk into knowledge base
python embeddings/chunker.py

# Step 4: Generate embeddings and store in ChromaDB
python embeddings/embedder.py
```

**Step 5 — Launch the chatbot**
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
Website (hbt-group.com/aftermarket-services/technology-services/)
        ↓
    crawler.py          — discovers 7 service page URLs
        ↓
    scraper.py          — downloads HTML, extracts structured text
        ↓
    cleaner.py          — removes boilerplate, deduplicates lines
        ↓
    chunker.py          — splits into heading-aware chunks with breadcrumbs
        ↓
    embedder.py         — generates embeddings (all-MiniLM-L6-v2) → ChromaDB
        ↓
    retriever.py        — cosine similarity search, source diversity filtering
        ↓
    ollama_client.py    — grounding prompt → Ollama (gemma3:4b)
        ↓
    app.py (Streamlit)  — chat UI with source citations
```

---

## 🌟 Bonus Features Implemented

- ✅ **Multi-page scraping** — crawls main page + 6 service sub-pages (7 pages total)
- ✅ **Citation support** — shows source document, heading breadcrumb, and similarity score per answer
- ✅ **Conversation memory** — chat history retained within a session
- ✅ **Handle unknown questions** — returns exact "I could not find relevant information in the knowledge base." message

---

## 📝 Assumptions & Challenges

**Assumptions:**
- Only publicly accessible pages under `hbt-group.com/aftermarket-services/technology-services/` are scraped
- Ollama and ChromaDB run fully locally — no internet needed after initial model pull and scrape
- The `chroma_db/` folder persists between sessions; re-running `run_pipeline.py` will rebuild it from scratch
- The `gemma3:4b` model must be pulled before launching (`ollama pull gemma3:4b`)

**Challenges faced:**
- The HBT site uses Elementor for layout, meaning content is wrapped in deeply nested `div` structures rather than semantic HTML — required content-zone detection via CSS selectors and density scoring fallback
- Boilerplate (cookie banners, GDPR notices, nav links) is embedded inline in the page body and required a dedicated `cleaner.py` step to strip without removing real content
- Tuning chunk size (`MAX_CHUNK_CHARS = 1400`) and similarity threshold (`MIN_SIMILARITY = 0.25`) to balance recall vs. precision for the local LLM context window
- Enumeration queries ("list all services") needed special handling — a `service_index` chunk type and similarity boosting to avoid partial answers

---

## 📝 Notes

- Re-scraping is only needed if HBT updates their website; otherwise `chroma_db/` can be reused as-is
- `langchain` and `langchain-text-splitters` are listed in `requirements.txt` as dependencies but the RAG pipeline is implemented directly without them
- The `ui/` folder contains stub helpers; all active UI logic lives in `app.py`

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
