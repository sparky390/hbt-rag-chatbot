# 🤖 HBT AI Knowledge Assistant (RAG Chatbot)

> An AI-powered chatbot that answers questions about HBT Technology Services using Retrieval-Augmented Generation (RAG). Answers are grounded strictly in scraped website content — no hallucinations, no guessing. Fully local, no paid APIs required.

---

## 🔗 Quick Navigation

- [How It Works](#%EF%B8%8F-how-it-works)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
  - [Option A — Docker (Recommended)](#option-a--docker-recommended)
  - [Option B — Local Python](#option-b--local-python)
- [Architecture](#%EF%B8%8F-architecture)
- [Features](#-features)
- [Example Questions](#-example-questions)
- [Bonus Features Implemented](#-bonus-features-implemented)
- [Assumptions](#-assumptions)
- [Challenges Faced](#-challenges-faced)
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

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Frontend / UI | [Streamlit](https://streamlit.io) |
| LLM | [Ollama](https://ollama.com) + `gemma3:4b` (local) |
| Embeddings | `all-MiniLM-L6-v2` via [sentence-transformers](https://www.sbert.net) |
| Vector Database | [ChromaDB](https://www.trychroma.com) (cosine similarity, persistent) |
| Web Scraping | [BeautifulSoup4](https://beautiful-soup-4.readthedocs.io) + requests |
| Containerisation | Docker + Docker Compose |
| Language | Python 3.12 |

---

## 📁 Project Structure

```
hbt-rag-chatbot/
├── app.py                      # Streamlit entry point
├── run_pipeline.py             # One-command pipeline runner (scrape → embed)
├── requirements.txt
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml          # Orchestrates app + Ollama services
├── .env.example                # Environment variable template
│
├── scraper/
│   ├── crawler.py              # Discovers all service page URLs
│   ├── scraper.py              # Downloads HTML, extracts + saves text & metadata
│   └── cleaner.py              # Post-processes text (removes boilerplate, dedup)
│
├── embeddings/
│   ├── chunker.py              # Structure-aware chunking with heading breadcrumbs
│   ├── embedder.py             # Generates embeddings and stores in ChromaDB
│   └── pdf_ingestor.py         # Ingests uploaded PDF documents into ChromaDB
│
├── rag/
│   ├── retriever.py            # Vector search with similarity filtering & source diversity
│   ├── prompt_builder.py       # Builds grounding prompt; defines NOT_FOUND_MESSAGE
│   └── chatbot.py              # ask_question_detailed() — main RAG entry point
│
├── llm/
│   └── ollama_client.py        # Calls Ollama chat API (model: gemma3:4b)
│
├── data/
│   ├── raw/                    # Raw HTML per page
│   ├── processed/              # Cleaned plain text per page
│   ├── metadata/               # JSON metadata per page (URL, word count, etc.)
│   ├── chunks.json             # All chunks before embedding
│   └── feedback.json           # Saved user feedback (thumbs up/down)
│
└── chroma_db/                  # Persisted ChromaDB vector store (auto-generated)
```

---

## 🚀 Setup & Installation

### Prerequisites

| Requirement | Notes |
|---|---|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Required for Option A |
| [Ollama](https://ollama.com/download) | Required for Option B only |
| Python 3.9+ | Required for Option B only |
| ~6 GB disk space | For model weights + Docker layers |

---

### Option A — Docker (Recommended)

This is the easiest path. Docker Compose spins up the Ollama model server and the Streamlit app together. The embedding model is baked into the image at build time — no cold-start downloads.

**1. Clone the repository**

```bash
git clone https://github.com/sparky390/hbt-rag-chatbot.git
cd hbt-rag-chatbot
```

**2. Copy the environment file**

```bash
cp .env.example .env
```

Default values in `.env.example` work out of the box:

```env
APP_PORT=8501
OLLAMA_PORT=11434
OLLAMA_MODEL=gemma3:4b
```

**3. Build and start all services**

```bash
docker compose up --build
```

This will:
- Pull the `ollama/ollama` image
- Build the app image (installs Python deps, bakes in the `all-MiniLM-L6-v2` embedding model)
- Start the Ollama service and automatically pull `gemma3:4b`
- Start the Streamlit app once Ollama is healthy

> ⏳ First build takes 5–10 minutes depending on your connection. Subsequent starts are fast.

**4. Open the chatbot**

```
http://localhost:8501
```

**5. (Optional) Re-run the scraping pipeline**

The repo ships with a pre-built `chroma_db/` vector store. If you want to re-scrape from the live HBT website:

```bash
docker compose exec app python run_pipeline.py
```

**Stopping the services**

```bash
docker compose down
```

To also remove stored model weights and vector data:

```bash
docker compose down -v
```

---

### Option B — Local Python

Use this if you prefer not to use Docker.

**1. Install and start Ollama**

Download from [ollama.com/download](https://ollama.com/download), then:

```bash
ollama pull gemma3:4b
```

**2. Clone and install dependencies**

```bash
git clone https://github.com/sparky390/hbt-rag-chatbot.git
cd hbt-rag-chatbot
pip install -r requirements.txt
```

**3. Run the data pipeline**

**Option 3A — One command:**
```bash
python run_pipeline.py
```

**Option 3B — Step by step:**
```bash
# Step 1: Discover and scrape all pages
python scraper/crawler.py
python scraper/scraper.py

# Step 2: Clean extracted text
python scraper/cleaner.py

# Step 3: Chunk into knowledge base
python embeddings/chunker.py

# Step 4: Generate embeddings → ChromaDB
python embeddings/embedder.py
```

> ⚠️ Skip steps 1–4 if you want to use the pre-built `chroma_db/` that ships with the repo.

**4. Launch the chatbot**

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🏗️ Architecture

### High-Level Data Flow

```
Website (hbt-group.com/aftermarket-services/technology-services/)
        │
        ▼
   crawler.py          — discovers 7 service page URLs
        │
        ▼
   scraper.py          — downloads HTML, extracts structured text
        │
        ▼
   cleaner.py          — removes boilerplate, deduplicates lines
        │
        ▼
   chunker.py          — splits into heading-aware chunks with breadcrumbs
        │
        ▼
   embedder.py         — generates embeddings (all-MiniLM-L6-v2) → ChromaDB
        │
   ┌────┴────────────────────────────────────────┐
   │              Query Path (runtime)            │
   └────┬────────────────────────────────────────┘
        │
   User Question
        │
        ▼
   retriever.py        — cosine similarity search, source diversity filtering
        │
        ▼
   prompt_builder.py   — grounding prompt construction + reference resolution
        │
        ▼
   ollama_client.py    — grounding prompt → Ollama (gemma3:4b) → answer text
        │
        ▼
   app.py (Streamlit)  — chat UI with collapsible source citations + feedback
```

### Docker Service Architecture

```
docker-compose.yml
├── ollama          (port 11434)  — model server, volume: ollama_data
├── ollama-pull     (one-shot)    — pulls gemma3:4b on first start
└── app             (port 8501)   — Streamlit chatbot, volume: chroma_data
         ↕
    OLLAMA_HOST=http://ollama:11434  (internal Docker network)
```

### Dockerfile — Multi-Stage Build

```
Stage 1 (builder)
  python:3.12-slim + build-essential
  → installs CPU-only PyTorch (avoids multi-GB CUDA download)
  → installs requirements.txt
  → bakes all-MiniLM-L6-v2 into /opt/hf-cache

Stage 2 (runtime)
  python:3.12-slim (no compilers)
  → copies /opt/venv and /opt/hf-cache from builder
  → copies app source
  → runs as non-root user (appuser, uid 1000)
  → healthcheck: curl http://localhost:8501/_stcore/health
```

### RAG Retrieval Detail

```
Question
  │
  ├─ is_enumeration_query()? → boost service_index chunks (+0.15 similarity)
  │
  ▼
embed question → cosine similarity search (fetch_k=20 candidates)
  │
  ├─ filter: similarity ≥ MIN_SIMILARITY (0.15)
  ├─ sort: descending similarity
  └─ diversity cap: max 3 chunks per source document
  │
  ▼
top-k chunks → build_context_block() → prompt → Ollama
```

---

## ⚡ Features

- 🏠 **Fully local** — no OpenAI key, no paid APIs; runs entirely on your machine via Ollama
- 🌐 **Multi-page scraping** — crawls the main page and all 6 linked service sub-pages (7 pages total)
- 🎯 **Grounded answers** — explicitly returns `"I could not find relevant information in the knowledge base."` instead of hallucinating
- 📄 **Source citations** — every answer shows document title, heading path, source file, and similarity score
- 💬 **Chat history** — full conversation memory within a session (last 3 turns passed to LLM)
- 🧭 **Sample questions sidebar** — pre-loaded prompts to explore HBT services instantly
- 🔍 **Smart retrieval** — enumeration queries (e.g. "list all services") get boosted `service_index` chunks for complete answers
- 🔗 **Pronoun chaining** — resolves "tell me more about that" / "what about the second one?" across turns
- 📎 **PDF ingestion** — upload company brochures directly in the chat bar; chunks are added to ChromaDB live
- 👍👎 **Feedback** — thumbs-up/down saved to `data/feedback.json`
- 🐳 **Docker deployment** — single `docker compose up --build` starts the full stack
- 🧩 **Modular architecture** — crawler, scraper, cleaner, chunker, embedder, retriever, LLM, and UI all in separate modules

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
- What does HBT do for technical documentation?
- What is strategic sourcing at HBT?

---

## 🌟 Bonus Features Implemented

| Feature | Status | Details |
|---|---|---|
| Multi-page scraping | ✅ | Crawls main page + 6 service sub-pages (7 pages total) |
| PDF ingestion | ✅ | Upload PDFs directly in the Streamlit chat bar; chunks added live |
| Conversation memory | ✅ | Last 3 turns passed to LLM; pronoun/ordinal reference resolution |
| Feedback mechanism | ✅ | 👍 / 👎 buttons; responses saved to `data/feedback.json` |
| Docker deployment | ✅ | Full multi-service Docker Compose stack with health checks |
| Citation support | ✅ | Collapsible source panel: doc title, heading path, similarity score |

---

## 📝 Assumptions

- **Scope limited to public HBT pages** — only pages publicly accessible under `hbt-group.com/aftermarket-services/technology-services/` are scraped. No authentication or internal pages are targeted.
- **Ollama runs locally** — the LLM (`gemma3:4b`) and ChromaDB both run on the host machine (or within Docker). No internet connection is needed after the initial model pull and scrape.
- **Pre-built vector store included** — the repo ships with a populated `chroma_db/` so the chatbot works immediately without re-running the pipeline. Re-run `run_pipeline.py` only if the HBT website is updated.
- **CPU inference is acceptable** — the Dockerfile installs CPU-only PyTorch. Inference with `gemma3:4b` via Ollama is adequate for a PoC; GPU acceleration would require a separate Ollama GPU image and is not configured here.
- **Single-user session** — Streamlit session state handles conversation memory in-memory per browser tab. There is no multi-user persistence layer.
- **English-only content** — the HBT website content and the embedding model (`all-MiniLM-L6-v2`) are both English-focused; multilingual queries are not supported.
- **`gemma3:4b` must be pulled before first use** — Docker Compose handles this automatically via the `ollama-pull` service. For local (non-Docker) usage, `ollama pull gemma3:4b` must be run manually.

---

## 🧗 Challenges Faced

### 1. Deeply nested Elementor HTML structure
The HBT website is built with the Elementor page builder. Content is wrapped in many layers of `<div class="elementor-*">` containers rather than semantic HTML (`<article>`, `<section>`, `<p>`). Standard `soup.get_text()` produced a flat, unstructured dump. **Solution:** implemented content-zone detection via CSS class heuristics and a density-scoring fallback to identify the main content region before extracting text.

### 2. Inline boilerplate mixed with real content
Cookie consent banners, GDPR notices, "How can we help?" CTAs, and navigation links are injected directly into the page body rather than in clearly separated DOM zones. They appeared after text extraction and polluted chunks. **Solution:** added a dedicated `cleaner.py` step with pattern-based filtering (`BOILERPLATE_PATTERNS`) and a `is_boilerplate()` check in the chunker to strip these without removing genuine content.

### 3. Tuning chunk size vs. similarity threshold
Initial chunks of 800 characters caused the LLM context window to fill with many partial snippets. Increasing to `MAX_CHUNK_CHARS = 1400` improved coherence. The similarity threshold required careful tuning: `MIN_SIMILARITY = 0.25` dropped short but relevant service-name matches (e.g. "Engineering Services") which score 0.18–0.22. **Solution:** lowered to `MIN_SIMILARITY = 0.15` after observing false negatives in testing.

### 4. Enumeration queries returning incomplete lists
"List all services" queries retrieved chunks about individual services rather than the overview index. **Solution:** introduced a `service_index` chunk type — a synthetic chunk built from the heading tree — and applied a `+0.15` similarity boost to `service_index` chunks for enumeration queries (detected by regex `ENUMERATION_RE`).

### 5. Pronoun and ordinal resolution across turns
Follow-up questions like "tell me more about that" or "what about the second one?" failed because the retriever had no context about what "that" referred to. **Solution:** implemented `resolve_reference()` in `prompt_builder.py`, and introduced `last_resolved_topic` and `reference_list` fields persisted in Streamlit `session_state`. The reference list is captured after enumeration answers so ordinal follow-ups (e.g. "the third one") always resolve against the original list, even if the most recent answer was a single-topic response.

### 6. Docker cold-start download delay
The first container run downloaded the `all-MiniLM-L6-v2` model (~90 MB) from Hugging Face at startup, causing a 30–60 second delay before the first query. **Solution:** baked the model download into the Docker builder stage (`RUN python -c "SentenceTransformer('all-MiniLM-L6-v2')"`) so it is cached in the image layer and the runtime container starts instantly.

### 7. CPU-only PyTorch image size
`sentence-transformers` pulls the full CUDA PyTorch build by default (~2.5 GB). **Solution:** explicitly installed the CPU-only wheel first (`--index-url https://download.pytorch.org/whl/cpu`) before `requirements.txt`, reducing the final image size significantly.

---

## 📝 Notes

- Re-scraping is only needed if HBT updates their website; otherwise `chroma_db/` can be reused as-is.
- `langchain` and `langchain-text-splitters` are listed in `requirements.txt` as transitive dependencies but the RAG pipeline is implemented directly without them — no `LangChain` abstractions are used.
- The `ui/` folder contains stub helpers referenced in the project structure; all active UI logic lives in `app.py`.
- Docker volumes (`ollama_data`, `chroma_data`) persist between restarts. Run `docker compose down -v` to wipe them completely.


## 🔗 Connect With Me

<p align="center">
  <a href="https://github.com/sparky390">GitHub</a> •
  <a href="https://www.linkedin.com/in/surya-sundars/">Linkedin</a>
</p>

---

<p align="center">
  Made with ❤️ by <b>Surya.S</b><br>
  ⚡ Turning scraped pages into smart answers
</p>
