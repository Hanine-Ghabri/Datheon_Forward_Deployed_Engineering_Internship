# Datheon Forward Deployed Engineering Internship

A portfolio repository containing two engineering projects built around secure document ingestion, vector indexing, and enterprise retrieval-augmented generation (RAG).

## Project overview

This repository contains two related internship tasks:

- Task 1: Client legacy document ingestion and vector ETL pipeline
- Task 2: Multi-tenant enterprise RAG application with role-based access control and evidence-grounded answer generation

## Repository layout

```text
Datheon_Forward_Deployed_Engineering_Internship/
├── README.md
├── .gitignore
├── task1-vector-etl/
│   ├── README.md
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── extract.py
│   │   ├── chunking.py
│   │   ├── metadata.py
│   │   ├── index.py
│   │   └── cli.py
│   └── tests/
├── task2-enterprise-rag/
│   ├── README.md
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── retrieval.py
│   │   ├── answer.py
│   │   └── citations.py
│   ├── scripts/
│   └── tests/
```

## Task 1 — Client Legacy Data Ingestion & Vector ETL Pipeline

Location: `task1-vector-etl/`

- Extracts PDF, CSV, Markdown, and text documents
- Preserves metadata such as tenant, department, access tier, modified date, and source provenance
- Uses sentence-aware chunking with configurable overlap
- Generates embeddings in batches and indexes them in ChromaDB or Qdrant
- Supports dry-run mode and manifest export
- Provides content and metadata for downstream retrieval pipelines

See `task1-vector-etl/README.md` for implementation details, setup, and usage.

## Task 2 — Enterprise Multi-Tenant RAG with RBAC

Location: `task2-enterprise-rag/`

- FastAPI API for secure PDF ingestion
- JWT-based demo authentication and principal validation
- Tenant-scoped retrieval and role/clearance-aware filtering
- Evidence-grounded answer generation with citations
- Graceful abstention when evidence is insufficient or unauthorized

See `task2-enterprise-rag/README.md` for implementation details, setup, and usage.

## Installation and validation

Each project has its own dependency list and environment file.

### Task 1
```bash
cd task1-vector-etl
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
pytest tests -q
```

### Task 2
```bash
cd task2-enterprise-rag
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
pytest tests -q
```

## Security considerations

This repository is a portfolio implementation, not a production-certified system.

- Replace demo JWT authentication with a real identity provider before production use
- Validate authorization metadata against a trusted policy source
- Fail closed when tenant or access metadata is missing or malformed
- Keep secrets and API keys out of version control
- Add scanning, logging, and audit controls before deploying real data

## Portfolio links

- GitHub: [Add your GitHub profile URL here]
- LinkedIn: [Add your LinkedIn profile URL here]

## Author

Add your name, LinkedIn, and contact details here before publishing.
