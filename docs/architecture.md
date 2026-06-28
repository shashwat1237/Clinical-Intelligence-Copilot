# Clinical Intelligence Copilot: Architectural Philosophy

This system is a **Clinical Intelligence Engine**, not a document chatbot.
It separates **knowledge construction** from **knowledge reasoning**.

## 1. Knowledge Construction (Ingestion)
Instead of re-reading PDFs, the system parses reports once during ingestion to build a structured PostgreSQL patient profile.
- **Text Extraction**: Uses PyMuPDF to convert PDFs to text.
- **Clinical Entities**: Uses Groq (JSON mode) to extract structured facts (Medications, Labs, Conditions).
- **Semantic Indexing**: Chunks are embedded using `all-MiniLM-L6-v2` and indexed natively in **pgvector** inside Supabase (eliminating the need for separate vector databases like FAISS).

## 2. Knowledge Reasoning (Agent Layer)
The system uses a deterministic Agent Orchestration layer to answer user questions.
- **Planner**: Classifies intent (e.g., "Is this a SQL lookup or does it require reasoning?").
- **Router**: Assembles the minimal necessary context (SQL facts + Vector retrieval).
- **Verifier**: Enforces "Algorithmic Honesty" by scrubbing hallucinated citations before the response reaches the user.

## 3. Data Flow Hierarchy
Every piece of data follows a strict hierarchy to ensure multi-tenant isolation:
`User` → `Patient` → `Documents` → `Clinical Entities` → `Timeline Events` → `Chat History`

## 4. Engineering Decisions
- **PostgreSQL-First**: We use SQL for deterministic queries (e.g., "What are my medications?") to minimize token usage and LLM costs. Vector similarity search is integrated directly via pgvector.
- **Stateless AI**: The Groq API is strictly used for reasoning and extraction. It stores no patient data.
- **75-File Constraint**: To maintain clarity, domain-specific modules (e.g., `search_and_patients.py`) are consolidated to keep the repository architecture lean and readable.
