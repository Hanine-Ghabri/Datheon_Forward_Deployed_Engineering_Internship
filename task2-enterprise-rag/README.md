# Task 2 — Enterprise Multi-Tenant RAG with RBAC

This project provides a FastAPI-based retrieval-augmented generation service for enterprise document repositories. It applies tenant restrictions, user role checks, and clearance gating before retrieving or answering questions.

## Purpose

The application is built for secure document answering in multi-tenant environments. It ingests PDFs, stores chunk metadata, embeds the content, and answers questions using only evidence that is authorized for the current identity.

## Architecture

- `app/main.py`: FastAPI app and request handlers.
- `app/config.py`: settings and environment variables.
- `app/security.py`: JWT verification and principal validation.
- `app/retrieval.py`: embedding, filtering, reranking, and authorization checks.
- `app/answer.py`: evidence-grounded answer generation and citation validation.
- `scripts/make_demo_token.py`: helper for generating a local development JWT.

## Prerequisites

- Python 3.11+
- Docker and Docker Compose for local containerized runs
- Access to a local ChromaDB-backed data directory

## Installation

Run these commands from `task2-enterprise-rag/`.

```bash
python -m venv .venv
```

Activate the environment and install dependencies:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

```bash
# macOS / Linux
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Set a strong local `JWT_SECRET` in `.env`, then create a demo token:

```bash
python scripts/make_demo_token.py
```

## Environment variables

```dotenv
APP_ENV=development
JWT_SECRET=replace-with-a-long-random-secret-before-use
JWT_ISSUER=enterprise-rag-local
JWT_AUDIENCE=enterprise-rag-api
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
CHROMA_PATH=./data/chroma
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
TOP_K=20
FINAL_K=5
MAX_UPLOAD_MB=20
```

`JWT_SECRET` must be replaced before any non-local use. Leave `OPENAI_API_KEY` blank to keep the API in abstention mode instead of calling a model.

## Running the API

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the Swagger UI.

For Docker Compose, create `.env` from `.env.example` and set a strong `JWT_SECRET`, then run:

```bash
docker compose up --build
```

## Example end-to-end flow

Use the generated token as a Bearer token in Swagger UI. In the curl examples, replace TOKEN with that token.

```bash
python scripts/make_demo_token.py
```

Use the generated token as a Bearer token in Swagger UI or in the curl `Authorization` header.

```bash
curl -X POST http://127.0.0.1:8000/documents \
  -H "Authorization: Bearer <token>" \
  -F "document_id=doc-001" \
  -F "allowed_roles=employee" \
  -F "required_clearance=confidential" \
  -F "file=@/path/to/document.pdf"

curl -X POST http://127.0.0.1:8000/query \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"question":"What does the document say about risk exposure?"}'
```

## Running tests

```bash
python -m pytest tests -q
```

Run the test command from `task2-enterprise-rag/`.

## Security model

- Requests require a valid JWT bearer token.
- The principal is validated for tenant, roles, and clearance.
- Retrieval enforces tenant and clearance constraints in the vector query.
- `chunk_is_authorized()` fails closed if ACL metadata is missing or malformed.
- The answer layer only uses evidence that passes authorization checks and abstains when evidence is insufficient or citations are invalid.

## Limitations and operational considerations

- This is a local development-friendly implementation and not a production IdP integration.
- The app uses a demo JWT issuer for local use only; production should use OIDC/JWKS or a trusted external identity provider.
- Model downloads can require network access the first time they run.
- PDF ingestion is intentionally limited to the text content and does not perform surveillance or office-document sanitization.
