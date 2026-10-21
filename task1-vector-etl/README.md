# Datheon Forward Deployed Engineering Internship

A portfolio repository for two applied engineering projects: a secure client data ingestion and vector ETL pipeline, and a multi-tenant enterprise RAG system with role-based access control.

## Overview

This repository demonstrates two complementary systems that are relevant to real-world enterprise AI deployments:

- Task 1 focuses on ingesting heterogeneous business documents, preserving provenance and access metadata, chunking safely, and building vector indexes for semantic retrieval.
- Task 2 focuses on secure retrieval-augmented generation in a multi-tenant setting with RBAC, access clearance gates, evidence-grounded answering, and auditable citations.

Both projects are intentionally designed for portfolio use and local validation. They are not production-certified security systems and should be hardened before use with sensitive client data.

## Project highlights

### Task 1 — Client Legacy Data Ingestion & Vector ETL Pipeline

Location: [task1-vector-etl/](task1-vector-etl/)

Features:
- Ingests PDF, CSV, Markdown, and plain text content.
- Applies sentence-aware chunking with configurable overlap.
- Preserves tenant, department, access tier, modified date, source, page number, and row number where applicable.
- Uses batched Sentence Transformers embeddings.
- Supports ChromaDB and Qdrant vector indexing with cosine similarity.
- Offers dry-run mode, JSONL manifest export, and basic throughput reporting.
- Fails closed when security metadata is missing or invalid.

### Task 2 — Enterprise Multi-Tenant RAG with RBAC

Location: [task2-enterprise-rag/](task2-enterprise-rag/)

Features:
- FastAPI service for PDF document ingestion and question answering.
- JWT-based local authentication and server-side authorization.
- Strict tenant isolation and clearance-based retrieval enforcement.
- Query rewriting and cross-encoder reranking.
- Evidence-grounded answer generation with page-level PDF citations.
- Abstention when evidence is insufficient or authorization fails.
- Test coverage for unauthorized access and citation validation.

## Repository tree

```text
Datheon_Forward_Deployed_Engineering_Internship/
├── README.md
├── task1-vector-etl/
│   ├── .env.example
│   ├── .gitignore
│   ├── Dockerfile
│   ├── README.md
│   ├── requirements.txt
│   ├── etl/
│   └── tests/
├── task2-enterprise-rag/
│   ├── .env.example
│   ├── Dockerfile
│   ├── README.md
│   ├── requirements.txt
│   ├── docker-compose.yml
│   ├── app/
│   ├── scripts/
│   └── tests/
└── legacy compatibility files remain only for reference
```

## Installation and usage

### Task 1

```bash
cd task1-vector-etl
python -m venv .venv
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1
# Windows cmd
# .\.venv\Scripts\activate.bat
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m etl.cli ingest ./data/input --backend chroma --output-manifest ./data/manifest.jsonl
```

Dry-run:

```bash
python -m etl.cli ingest ./data/input --backend chroma --dry-run
```

Tests:

```bash
pytest -q
```

### Task 2

```bash
cd task2-enterprise-rag
python -m venv .venv
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1
# Windows cmd
# .\.venv\Scripts\activate.bat
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/make_demo_token.py
uvicorn app.main:app --reload
```

Open the Swagger UI at http://127.0.0.1:8000/docs and use a bearer token from the demo script.

Tests:

```bash
pytest -q
```

## Security considerations and known limitations

- These projects are portfolio implementations and should not be treated as production-ready security certifications.
- Tenant IDs, access clearance, and role membership must be validated server-side and never trusted from the client.
- Missing or malformed access metadata is treated as a fail-closed condition.
- Local JWT/demo auth is for development only and should be replaced with an enterprise identity provider or centralized policy service.
- Document parsing and ingestion should be hardened with malware scanning, rate limiting, storage isolation, and audit logging before production use.
- OCR support for scanned PDFs is not included unless explicitly added later.

## Author

- GitHub: [@your-github-handle](https://github.com/your-github-handle)
- LinkedIn: [Your Name](https://www.linkedin.com/in/your-linkedin-profile)
- Email: your.email@example.com

## Project-specific documentation

- [Task 1 README](task1-vector-etl/README.md)
- [Task 2 README](task2-enterprise-rag/README.md)

