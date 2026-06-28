# Clinical Intelligence Copilot

A production-grade medical AI platform that transforms unstructured clinical PDFs into a structured, searchable patient knowledge base. It separates **knowledge construction** (one-time async extraction) from **knowledge reasoning** (per-query AI analysis), so the AI never re-reads raw documents — it reasons over a pre-built patient profile.

---

## What It Does

1. **Upload** medical PDFs (lab reports, discharge summaries, prescriptions)
2. **Extraction pipeline** parses text, extracts structured clinical entities, and generates semantic embeddings — all asynchronously
3. **Patient profile** is built: conditions, medications, lab results, and a chronological timeline
4. **AI Copilot** answers natural language questions about the patient's history using a hybrid SQL + vector RAG pipeline with grounded, verifiable citations

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend | FastAPI 0.111, Python 3.11, Pydantic v2 |
| Database | Supabase PostgreSQL + pgvector |
| Auth & Storage | Supabase Auth (JWT) + Supabase Storage |
| AI / LLM | Groq API — LLaMA 3.3-70B Versatile |
| Embeddings | `all-MiniLM-L6-v2` via Sentence Transformers (384-dim) |
| PDF Parsing | PyMuPDF |
| Deployment | Render (backend), Vercel (frontend) |
| Monorepo | Turborepo |

---

## Repository Structure

```
.
├── backend/               # FastAPI application
│   └── app/
│       ├── agents/        # Planner, Router, Verifier (agent orchestration)
│       ├── ai/            # Groq client, embeddings, extraction, prompts
│       ├── api/v1/        # Route handlers (auth, upload, chat, docs, timeline, search)
│       ├── core/          # Config, security (JWT validation)
│       ├── db/            # SQLAlchemy models, CRUD, session, migrations
│       ├── schemas/       # Pydantic request/response schemas
│       ├── services/      # Business logic (chat, extraction, search, storage, timeline)
│       └── main.py        # App entry point, lifespan, CORS, route registration
├── frontend/              # Next.js application
│   ├── app/               # App Router pages (dashboard, upload, auth)
│   ├── components/        # UI components (ChatPanel, Timeline, Reports, etc.)
│   ├── hooks/             # useChat, useDocumentStatus
│   ├── services/          # ApiService (fetch wrapper with auth)
│   └── lib/               # TypeScript types, helpers
├── scripts/               # Seeding, vector building, benchmarking utilities
├── tests/                 # pytest test suite
└── docs/                  # Architecture, API, deployment docs
```

---

## Architecture

### Data Hierarchy

Every piece of data follows a strict FK chain for multi-tenant isolation:

```
User (Supabase Auth)
  └─ Patient (1:1)
       ├─ Document
       │    ├─ ClinicalEntity  (Condition / Medication / LabResult)
       │    ├─ TimelineEvent
       │    └─ VectorChunk     (384-dim embedding)
       └─ ChatMessage
```

All query-time SQL filters are scoped by `patient_id`, derived from the authenticated user's JWT.

### Database Schema

The database uses **Supabase PostgreSQL** with the `pgvector` extension — no separate vector database needed.

- `users` — mirrors Supabase Auth, keyed by Supabase user UUID
- `patients` — 1:1 with user, the root of all clinical data
- `documents` — tracks upload status through 6 states: `QUEUED → PROCESSING → EXTRACTING → INDEXING → READY / FAILED`
- `vector_chunks` — text chunks with `embedding vector(384)` column, queried via cosine distance
- `clinical_entities` — structured facts (category, normalized_name, value, metadata JSONB)
- `timeline_events` — date-ordered clinical events linked to source documents
- `chat_messages` — full conversation history with `citations_json` per AI message

---

## Core Flows

### 1. Document Ingestion Pipeline

```
Upload PDF
  → Store in Supabase Storage (user_id/filename path)
  → Create Document record (status=QUEUED)
  → Background thread starts:
       ├─ Download PDF bytes → PyMuPDF text extraction
       ├─ Chunk text (300-word windows, 50-word overlap)
       ├─ Groq JSON-mode extraction → ClinicalEntities + TimelineEvents → PostgreSQL
       ├─ Sentence Transformer embeddings → VectorChunks → pgvector
       └─ Document.status = READY
  → Frontend polls /documents/{id}/status every 3s until READY
```

The extraction step calls Groq with a structured system prompt, returning typed entities (Condition, Medication, LabResult) with metadata like dosage, unit, and `is_abnormal`. On server restart, any document stuck in an intermediate state is automatically recovered and re-queued.

### 2. Agent-Orchestrated Chat (RAG Pipeline)

```
User message
  → Planner: classify intent
       └─ Strategy: SQL_ONLY | HYBRID | VECTOR_ONLY
       └─ entities_to_search: ["metformin", "HbA1c"]
  → Router: assemble context
       ├─ SQL path: query clinical_entities (filtered by Planner entities, limit 50)
       └─ Vector path: cosine similarity search in pgvector (top-k=6)
  → Format evidence block with numbered citations [1], [2]...
  → Groq LLM (temp=0.0): generate response using evidence only
  → Verifier: regex-check citation indices, strip hallucinated refs
  → Save user + AI messages to chat_messages
  → Return { role, content, citations[] }
```

The **Planner** prevents context explosion by narrowing SQL queries to relevant entity names before fetching. The **Verifier** enforces algorithmic honesty — if the LLM cites `[5]` but only `[1]-[3]` exist in context, the citation is removed before the response reaches the user.

### 3. Authentication Flow

1. User submits credentials on `/login` or `/signup`
2. Backend calls Supabase Auth SDK (`sign_in_with_password` / `sign_up`)
3. JWT is returned and stored in `localStorage`
4. Every API call includes `Authorization: Bearer <token>`
5. FastAPI dependency `get_current_user()` validates the token via Supabase, returns `user_id`
6. On 401, the frontend clears the token and redirects to `/login`

---

## API Overview

All routes are prefixed at `/api/v1/`.

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/signup` | Create account, auto-provision patient profile |
| `POST` | `/auth/login` | Login, returns JWT |
| `POST` | `/upload` | Upload PDF (202 Accepted, async processing) |
| `GET` | `/documents` | List all documents for the user |
| `GET` | `/documents/{id}/status` | Poll processing status |
| `GET` | `/documents/{id}/entities` | Get extracted clinical entities |
| `DELETE` | `/documents/{id}` | Delete document + cascade |
| `GET` | `/patients/profile` | Get structured patient profile |
| `GET` | `/patients/search?q=` | Hybrid SQL + vector search |
| `POST` | `/chat` | Send message, runs full agent pipeline |
| `GET` | `/chat/history` | Retrieve conversation history |
| `DELETE` | `/chat` | Clear chat history |
| `GET` | `/timeline` | Get chronological timeline events |

---

## Frontend Pages

| Route | Description |
|---|---|
| `/login` | Email/password login |
| `/signup` | Registration |
| `/upload` | PDF upload with status polling |
| `/dashboard` | Patient summary + embedded chat |
| `/dashboard/chat` | Full-screen chat interface |
| `/dashboard/reports` | Document list with entity viewer |
| `/dashboard/timeline` | Visual chronological timeline |
| `/dashboard/settings` | Session management |

Key components: `ChatPanel` (conversation UI with clickable citation badges), `CitationDrawer` (source details panel), `ClinicalSummaryCard` (conditions/medications/labs grid), `TimelinePanel`, `ReportViewer` (PDF iframe + extracted entities side-by-side).

---

## Setup & Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Supabase project with the `pgvector` extension enabled

### Environment Variables

Copy `.env.example` and fill in your values. The backend expects:
- `DATABASE_URL` — Supabase PostgreSQL connection string
- `SUPABASE_SERVICE_KEY` — service role key for Storage and Auth admin
- `GROQ_API_KEY` — from [console.groq.com](https://console.groq.com)
- `JWT_SECRET` — your Supabase project's JWT secret

The frontend expects:
- `NEXT_PUBLIC_BACKEND_URL` — backend base URL
- `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_KEY` — for client-side auth

### Database Migrations

Run `backend/app/db/migrations.sql` in your Supabase SQL Editor to create all tables and enable the `vector` and `uuid-ossp` extensions.

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker (Backend)

```bash
docker build -t clinical-copilot-backend ./backend
docker run -p 8000:8000 --env-file backend/.env clinical-copilot-backend
```

The Dockerfile pre-downloads the `all-MiniLM-L6-v2` model at build time so the first request has no cold start.

---

## Testing

```bash
cd tests
pytest
```

Test coverage includes: auth flows, chat pipeline, citation grounding, entity extraction, RAG retrieval, search, timeline, upload, and multi-step integration scenarios.

---

## Design Principles

- **PostgreSQL-first** — deterministic SQL for structured queries, vectors for semantic search. No separate vector DB.
- **Stateless AI** — Groq stores zero patient data. All state lives in PostgreSQL.
- **Algorithmic honesty** — the Verifier strips any citation the LLM invented that isn't backed by actual retrieved evidence.
- **Recovery resilience** — on startup, the app scans for documents stuck mid-pipeline and restarts their workflows.
- **Multi-tenant isolation** — every table is scoped by `patient_id` derived from a validated JWT, making cross-user data leakage structurally impossible.
