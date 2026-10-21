# Datheon Forward Deployed Engineering Internship

A portfolio repository containing two engineering projects built around secure document ingestion and enterprise retrieval-augmented generation (RAG).

## Projects

### Task 1 — Client Legacy Data Ingestion & Vector ETL Pipeline
Location: [`task1-vector-etl/`](task1-vector-etl/)

- Extracts PDF, CSV, Markdown, and text documents.
- Chunks content with overlap while preserving source metadata.
- Preserves tenant, department, access tier, modified date, and source page/row.
- Generates sentence-transformer embeddings in batches.
- Indexes vectors in ChromaDB or Qdrant using cosine similarity.
- Supports dry runs, JSONL manifests, and basic throughput reporting.

Start with the task-specific [README](task1-vector-etl/README.md).

### Task 2 — Enterprise Multi-Tenant RAG with RBAC
Location: [`task2-enterprise-rag/`](task2-enterprise-rag/)

- FastAPI endpoints for PDF ingestion and question answering.
- JWT-based development authentication and role/clearance checks.
- Tenant and clearance filters in vector retrieval, with application-level validation.
- Query rewriting and cross-encoder reranking.
- Evidence-grounded answers with PDF page citations and abstention when evidence is insufficient.
- Security tests, Dockerfile, and configuration template.

Start with the task-specific [README](task2-enterprise-rag/README.md).

## Repository layout

```text
Datheon_Forward_Deployed_Engineering_Internship/
├── README.md
├── task1-vector-etl/
│   ├── etl/
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
└── task2-enterprise-rag/
    ├── app/
    ├── scripts/
    ├── tests/
    ├── requirements.txt
    └── README.md
```

## Quick start

Each project has its own dependencies and instructions. Open its folder and follow its README. Keep each `.env` file local; never commit API keys, access tokens, private documents, or secrets.

## Security and limitations

This repository is a portfolio implementation, not a certified production system. Before using real client data, replace development authentication with your organization's identity provider, centralize authorization policy, restrict who can assign document access metadata, secure vector storage, add ingestion scanning and audit logs, and run security and load tests. OCR is not included for scanned PDFs.

## Suggested validation

- Run the unit tests in each project environment.
- Test cross-tenant and clearance-denied retrieval.
- Confirm page citations match the original PDF pages.
- Benchmark ETL throughput on a representative document set.
- Verify that missing or invalid access metadata fails closed.

## Author

Add your name, LinkedIn, and contact details here before publishing.
