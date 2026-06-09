# RAG QA API

FastAPI service for document ingestion and semantic search using Retrieval-Augmented Generation (RAG). Upload PDF documents, auto-chunk and embed them via OpenAI, store vectors in pgvector, and query with natural language.

## Architecture

```text
PDF Upload → Parse (pdfplumber) → Split (LangChain) → Embed (OpenAI) → Store (pgvector)
                                                                              ↓
Natural Language Query → Embed → Vector Similarity Search → Ranked Chunks
```

**Stack:**

- FastAPI + SQLAlchemy (async) + asyncpg
- PostgreSQL 16 + pgvector extension
- OpenAI `text-embedding-3-small` (1536 dimensions)
- Alembic for migrations

## Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| `POST` | `/documents/` | Upload PDF, index chunks |
| `GET` | `/documents/` | List all documents |
| `POST` | `/documents/search` | Semantic search over chunks |

### Upload document

```bash
curl -X POST http://localhost:8000/documents/ \
  -F "file=@document.pdf"
```

Response:

```json
{
  "id": "uuid",
  "file_name": "uuid.pdf",
  "file_path": "uploads/uuid.pdf",
  "status": "completed"
}
```

Document status lifecycle: `pending` → `processing` → `completed` | `failed`

### Search

```bash
curl -X POST http://localhost:8000/documents/search \
  -H "Content-Type: application/json" \
  -d '{"text": "your question here"}'
```

Response:

```json
[
  { "id": "chunk-uuid", "content": "relevant text chunk..." }
]
```

## Setup

### Prerequisites

- Python 3.13+
- Docker (for PostgreSQL + pgvector)
- OpenAI API key

### 1. Start database

```bash
docker compose up -d
```

Runs PostgreSQL 16 with pgvector on port `5433`.

### 2. Environment

Create `.env.local`:

```env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/rag_qa_db
DEBUG=true
```

### 3. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Start server

```bash
uvicorn app.main:app --reload
```

API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

## Data Model

**Document** — tracks uploaded file and indexing status

**DocumentChunk** — stores parsed text segments with:

- `content` — raw text
- `chunk_index` — position within document
- `page_number` — source page
- `embedding` — 1536-dim vector (pgvector)

## Configuration

| Setting | Default | Description |
| ------- | ------- | ----------- |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `EMBEDDING_DIMENSION` | `1536` | Vector dimensions |
| `OPENAI_API_KEY` | required | OpenAI API key |
| `DATABASE_URL` | required | Async PostgreSQL URL |
| `DEBUG` | `true` | Debug mode |
