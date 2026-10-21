# Client Legacy Data Ingestion & Vector ETL Pipeline

An extensible Python ETL pipeline for extracting legacy business documents (PDF, CSV, Markdown), normalizing records, semantically chunking text, preserving metadata, embedding in batches, and indexing in ChromaDB or Qdrant.

## Features
- PDF / CSV / Markdown ingestion
- Metadata preservation: tenant, department, access tier, source, modified date, page number
- Semantic chunking with a configurable sentence-aware splitter and overlap
- Batched embeddings and upserts
- Cosine similarity index configuration
- Metadata filters for retrieval
- Dry-run mode and JSONL manifest output
- Basic benchmarking for throughput and chunk counts
- Optional Qdrant backend; ChromaDB default

## Setup

Python 3.11+:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Ingest a directory

Place source files under `./data/input` and run:

```bash
python -m etl.cli ingest ./data/input --backend chroma --output-manifest ./data/manifest.jsonl
```

Preview without indexing:

```bash
python -m etl.cli ingest ./data/input --dry-run
```

Qdrant local mode:

```bash
python -m etl.cli ingest ./data/input --backend qdrant
```

Optional Qdrant server mode: set `QDRANT_URL` and `QDRANT_API_KEY` in `.env`.

## Input metadata

A sidecar JSON file named `<filename>.meta.json` can override defaults:

```json
{
  "tenant_id": "client-acme",
  "department": "finance",
  "access_tier": "confidential",
  "modified_date": "2026-10-20",
  "source": "legacy-share"
}
```

Missing security metadata fails closed by default; configure a safe default only if your governance policy explicitly allows it. Do not infer access tier from document contents.

CSV rows are converted to text with column names preserved. Each row receives its own chunk by default, and large rows are split if necessary.

## Security and production notes
- ETL preserves metadata; it does not itself grant access. Validate tenant, department, and access tier against an authoritative policy source.
- Use least-privilege credentials and encrypted storage; keep secrets out of source control.
- Scan uploads, limit file size and page count, and isolate parsers in a worker/container.
- Use stable document IDs, content hashes, idempotent upserts, dead-letter handling, retries, and audit logs for a production deployment.
- Test tenant/department/access-tier filters at the database boundary.
- For scanned PDFs, add OCR (e.g., Tesseract or a managed OCR service) and preserve page provenance.
- Benchmark with representative documents and hardware; performance numbers depend on environment and model downloads.

This is a starter implementation. Threat-model, load-test, and validate access controls before production.
