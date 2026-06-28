# REST API Documentation

The FastAPI layer relies entirely on JWT validation via Supabase.

### Core Endpoints
- `POST /api/v1/auth/signup`: Registers user and syncs to Supabase.
- `POST /api/v1/upload/`: Asynchronous document upload. Returns 202 Accepted.
- `GET /api/v1/documents/`: Retrieves documents scoped to the JWT owner.
- `POST /api/v1/chat/`: Invokes the Planner->Router->LLM->Verifier chain.
- `GET /api/v1/patients/profile`: Returns deterministic structured clinical data.

