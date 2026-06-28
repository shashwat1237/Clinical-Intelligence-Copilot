# Clinical Intelligence Copilot

A production-grade clinical intelligence system that transforms unstructured medical PDFs into a structured, searchable, and explainable patient knowledge base.

## Architecture
The application separates knowledge construction from knowledge reasoning.
- **Frontend:** Next.js, React, TypeScript, Tailwind CSS (Deployed on Vercel).
- **Backend:** FastAPI, Python (Deployed on Render).
- **Database/Auth/Storage:** Supabase PostgreSQL, Supabase Auth, Supabase Storage.
- **AI/Vector:** Groq API, FAISS/pgvector, Sentence Transformers.

## Quick Start
1. Install dependencies at the root: `npm install`
2. Set up environments: Copy `.env.example` to `.env` in respective directories.
3. Start the dev servers using Turborepo: `npm run dev`

