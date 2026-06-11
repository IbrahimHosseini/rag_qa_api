# RAG QA API

FastAPI service for document ingestion, semantic search, and conversational QA using Retrieval-Augmented Generation (RAG). Upload PDF documents, auto-chunk and embed them via OpenAI, store vectors in pgvector, and query with natural language — including multi-turn chat with conversation history.

## Architecture

```mermaid
flowchart TD
    subgraph Ingestion
        A[PDF Upload] --> B[Parse\npdfplumber]
        B --> C[Split\nLangChain]
        C --> D[Embed\nOpenAI]
        D --> E[(pgvector\nPostgreSQL)]
    end

    subgraph Retrieval
        F[Natural Language Query] --> G{Has session\nhistory?}
        G -- Yes --> H[Rephrase\nGPT-4o-mini]
        G -- No --> I[Original Query]
        H --> J[Embed\nOpenAI]
        I --> J
        J --> K[Hybrid Search\nVector + Trigram + RRF]
        E --> K
        K --> L[Rerank\nCrossEncoder]
        L --> M[Top-K Chunks]
    end

    subgraph Persistence
        F --> N[(ConversationHistory\nPostgreSQL)]
        N --> G
    end
```

**Stack:**

- FastAPI + SQLAlchemy (async) + asyncpg
- PostgreSQL 16 + pgvector + pg_trgm extensions
- OpenAI `text-embedding-3-small` (1536 dimensions)
- OpenAI `gpt-4o-mini` for query rephrasing
- `cross-encoder/ms-marco-MiniLM-L-6-v2` (HuggingFace) for reranking
- Alembic for migrations

## Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| `POST` | `/documents/` | Upload PDF, index chunks |
| `GET` | `/documents/` | List all documents |
| `POST` | `/documents/search` | Hybrid semantic search over chunks |
| `POST` | `/documents/chat` | Conversational QA with session history |

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

Uses hybrid search (vector similarity + trigram full-text) with Reciprocal Rank Fusion (RRF), then reranks results with a CrossEncoder model. Returns top 3 chunks.

### Chat

```bash
curl -X POST http://localhost:8000/documents/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid", "query": "your follow-up question"}'
```

Response:

```json
{
  "session_id": "uuid",
  "query": "original question",
  "rephrased_query": "standalone rephrased question",
  "results": [
    { "id": "chunk-uuid", "content": "relevant text chunk..." }
  ]
}
```

Conversation history is persisted per `session_id`. Follow-up questions are rephrased into standalone queries using GPT-4o-mini before retrieval.

## Setup

### Prerequisites

- Python 3.13+
- Docker (for PostgreSQL + pgvector)
- OpenAI API key
- HuggingFace token (for reranker model)

### 1. Start database

```bash
docker compose up -d
```

Runs PostgreSQL 16 with pgvector on port `5433`.

### 2. Environment

Create `.env.local`:

```env
OPENAI_API_KEY=sk-...
HF_TOKEN=hf-...
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

**ConversationHistory** — stores chat turns with:

- `session_id` — groups messages into a conversation
- `role` — `user` or `assistant`
- `content` — message text
- `created_at` — timestamp

## Configuration

| Setting | Default | Description |
| ------- | ------- | ----------- |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `EMBEDDING_DIMENSION` | `1536` | Vector dimensions |
| `OPENAI_API_KEY` | required | OpenAI API key |
| `HF_TOKEN` | required | HuggingFace token for reranker |
| `DATABASE_URL` | required | Async PostgreSQL URL |
| `DEBUG` | `true` | Debug mode |
