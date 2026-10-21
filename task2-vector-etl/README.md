# Task 1 — Client Legacy Data Ingestion & Vector ETL Pipeline

This project ingests legacy business documents, preserves access and provenance metadata, chunks content safely, and builds vector indexes for semantic retrieval.

## What it does

- Accepts PDF, CSV, Markdown, and plain text input.
- Extracts text while preserving document provenance such as page numbers and row numbers.
- Enforces required metadata such as tenant and access tier.
- Splits long text into sentence-aware chunks with configurable overlap.
- Embeds chunks using Sentence Transformers.
- Indexes vectors in ChromaDB or Qdrant with cosine similarity.
- Supports dry-run execution and JSONL manifest exports.

## Folder layout

```text
task1-vector-etl/
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
├── requirements.txt
├── etl/
│   ├── __init__.py
│   ├── chunking.py
│   ├── cli.py
│   ├── config.py
│   ├── extract.py
│   ├── index.py
│   ├── metadata.py
│   └── pipeline.py
└── tests/
    ├── test_chunking.py
    ├── test_metadata.py
    └── test_pipeline.py
```

## Setup

Python 3.11+ recommended.

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
```

## Example run

```bash
python -m etl.cli ingest ./data/input --backend chroma --output-manifest ./data/manifest.jsonl
```

Dry-run without indexing:

```bash
python -m etl.cli ingest ./data/input --backend chroma --dry-run
```

Qdrant local mode:

```bash
python -m etl.cli ingest ./data/input --backend qdrant
```

## Metadata contract

A sidecar JSON file named `<filename>.meta.json` may define metadata fields such as:

```json
{
  "tenant_id": "client-acme",
  "department": "finance",
  "access_tier": "confidential",
  "modified_date": "2026-10-20",
  "source": "legacy-share"
}
```

Missing or invalid tenant/access metadata fails closed. The ETL layer preserves metadata but does not authorize access by itself.

## Running tests

```bash
pytest -q
```

## Security notes

- The ETL pipeline does not infer access privileges from content.
- Sensitive metadata must come from a trusted source and be validated before indexing.
- Keep `.env`, credentials, and generated vector databases out of Git.

