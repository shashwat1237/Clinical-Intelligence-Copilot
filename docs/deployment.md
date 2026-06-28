# Clinical Intelligence Copilot: Production Deployment Strategy

This project follows a production-inspired deployment strategy, distributing responsibilities across specialized, low-cost cloud services.

## 1. Deployment Philosophy
Every service owns exactly one responsibility:
- **Frontend**: Vercel (Next.js hosting, Edge CDN)
- **Backend**: Render (FastAPI API, Dockerized for dependency isolation)
- **Database**: Supabase PostgreSQL (Structured data & pgvector semantic index)
- **Storage**: Supabase Storage (PDF reports)
- **Auth**: Supabase Auth (JWT handling)
- **Reasoning**: Groq (Stateless LLM)
- **Embeddings**: Local (Sentence Transformers running inside the Render container)

## 2. Infrastructure Overview
- **Vercel**: Handles static assets and client-side routing.
- **Render**: Hosts the FastAPI backend using Docker. Environment variables for `DATABASE_URL`, `GROQ_API_KEY`, and `JWT_SECRET` are injected at runtime here. A startup script manages resuming jobs killed by sleep states.
- **Supabase**: Serves as the primary persistence layer. We use the `pgvector` extension for all semantic retrieval, keeping relational and semantic data in a unified database architecture.

## 3. Security Model
- **HTTPS Only**: All communication is encrypted via TLS.
- **JWT Validation**: The FastAPI backend validates Supabase-issued tokens for every protected route.
- **CORS Configuration**: CORS is explicitly restricted to the production frontend URL.
- **Secrets Management**: Sensitive keys are never hardcoded; they are managed through platform-native environment variable injection.

## 4. Scalability
The monolithic architecture is designed for vertical scaling. Should load increase, the background extraction tasks (currently running on FastAPI background threads and auto-resuming on boot) can easily be offloaded to a dedicated Celery worker service without modifying the API routing logic.
