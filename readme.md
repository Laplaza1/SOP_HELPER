
# SOP_HELPER

**RAG-powered Standard Operating Procedure (SOP) assistant**

SOP_HELPER is a Django-based web application that helps users create, store, search, and interact with Standard Operating Procedures using Retrieval-Augmented Generation (RAG). It combines vector embeddings, a Qdrant vector database, and AI models to provide context-aware answers and step-by-step guidance grounded in your SOPs.

> **Project status**: Early development / Beta  
> **Author**: Laplaza1  
> **Repository**: [https://github.com/Laplaza1/SOP_HELPER](https://github.com/Laplaza1/SOP_HELPER)

---

## Overview

Standard Operating Procedures are critical for consistency, training, compliance, and knowledge transfer. SOP_HELPER turns static SOP documents into an interactive, searchable knowledge base.

**Core idea**:  
Upload or manually create SOPs → embed the steps → store them in a vector database → query them semantically → have an LLM elaborate on the retrieved context without inventing information.

### Key Features

- **SOP Creation & Storage**  
  Manually add SOPs with service level, title, and individual steps. Each step is embedded and stored in Qdrant.

- **Semantic Search**  
  Query SOPs using natural language. Results are filtered by SOP name when provided and ranked by cosine similarity.

- **RAG Chat Interface**  
  Retrieved SOP context is passed to Grok (via the xAI API). The model is instructed to answer *only* from the provided context.

- **Document Upload (In Progress)**  
  Support for uploading PDF (and planned TXT) documents, with text extraction using `pypdfium2`, `pdfplumber`, and related libraries.

- **Embedding Options**  
  - Primary: `fastembed` (lightweight, 384-dimensional)  
  - Alternative: `sentence-transformers` (`all-MiniLM-L6-v2`)

- **Django Backend**  
  Clean project structure with a dedicated `SOP_Chat` app, models for documents, forms, admin, and logging.

---

## Tech Stack

| Layer              | Technology                          |
|--------------------|-------------------------------------|
| Framework          | Django ≥ 6.0                        |
| Vector Database    | Qdrant                              |
| Embeddings         | fastembed / sentence-transformers   |
| LLM                | xAI Grok (via OpenAI-compatible API)|
| Document Parsing   | pypdfium2, pdfplumber, pymupdf      |
| Orchestration      | LangChain / LangGraph (planned)     |
| Package Management | `uv` + `pyproject.toml`             |
| Database           | SQLite (default)                    |

---

## Project Structure

```
SOP_HELPER/
├── SOP_Chat/                 # Main Django app
│   ├── templates/            # base.html, chat.html, upload forms
│   ├── agent.py              # LLM interaction logic
│   ├── embeder.py            # Embedding utilities
│   ├── qdrant.py             # Qdrant client & collection management
│   ├── models.py             # Document model
│   ├── views.py              # create_sop, semantic_search, upload, etc.
│   ├── forms.py
│   └── ...
├── SOP_Site/                 # Project settings & URLs
├── manage.py
├── pyproject.toml
├── uv.lock
└── db.sqlite3
```

---

## Getting Started

###current  Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Running Qdrant instance (local or remote)
- xAI API key (`XAI_API_KEY`)

### 1. Clone the repository

```bash
git clone https://github.com/Laplaza1/SOP_HELPER.git
cd SOP_HELPER
```

### 2. Install dependencies

Using `uv` (recommended):

```bash
uv sync
```

Or with pip:

```bash
pip install -e .
```

### 3. Environment variables

Create a `.env` file in the project root:

```env
XAI_API_KEY=your_xai_api_key_here
QDRANT_HOST=http://localhost:6333   # or your Qdrant URL
QDRANT_COLLECTION =collection_name
SECRET_KEY =django_secret_key
```



### 4. Set up Qdrant collection

The application will attempt to create a collection named `sop` with 384-dimensional vectors and cosine distance if it does not exist.

### 5. Run migrations & start the server

```bash
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the interface.

---

## Usage

### Creating an SOP

Send a POST request (or use the form) with:

- `serviceLevel`
- `sop` (name/title of the procedure)
- `step` (individual step text)

Each step is embedded with `fastembed` and upserted into Qdrant with the corresponding payload.

>>>Soon will be able to upload a whole `.txt` or `.pdf` .

### Semantic Search + RAG

1. Provide a natural-language query (`q`)
2. Optionally filter by SOP name (`sop`)
3. The system:
   - Embeds the query
   - Retrieves the top matching steps from Qdrant
   - Passes the results as context to Grok
   - Returns a clear, structured answer grounded only in the retrieved SOP content

### Document Upload

PDF upload support is under active development. Uploaded files are stored via the `Document` model. Text extraction examples using `pypdfium2` are available in `SOP_Chat/example_PDF_conversion.py`.

---

## Configuration Notes

- **Embeddings**: Default is 384-dimensional (`fastembed`). Ensure your Qdrant collection matches this dimension.
- **LLM**: Currently uses `grok-4.3` (or similar) via the xAI OpenAI-compatible endpoint. Temperature is set to 0.8 with a 1024 token limit.
- **System Prompt**: Explicitly instructs the model to use *only* the provided context and negative prompting for excess info.
- **Logging**: file logging to `app.log` soon will be from `.env` .

---

## Current Limitations & Roadmap

- Document ingestion pipeline (PDF → text → chunking → embedding).
- authentication / multi-user support.
- LangGraph / more advanced agent orchestration
- Frontend built out.

**Planned improvements**:
- Full PDF/TXT ingestion with intelligent chunking
- Better UI/UX for uploading,managing and inquiring about SOPs
- Service-level filtering and more advanced metadata
- Persistent conversation history
- Export / import of SOP collections
- SOP lookup



---

## Contributing

This is currently a personal/experimental project. Feel free to open issues or pull requests if you’d like to collaborate.

---



## Acknowledgments

- Built with Django, Qdrant, fastembed, and xAI Grok, Soon to be configurable
- Inspired by the need for practical, AI-assisted SOP management and knowledge retrieval

---

**Questions or feedback?**  
Reach out via the GitHub repository or Discord.

