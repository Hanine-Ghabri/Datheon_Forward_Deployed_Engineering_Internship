# Task 1 — Vector ETL Pipeline

This project ingests documents from a directory, extracts text, chunks it, enriches the metadata, and indexes the embeddings in a vector database for downstream retrieval.

## Purpose

The ETL pipeline is designed for client-legacy document collections. It accepts a root folder, scans supported file types, extracts content into chunk-sized units, and preserves provenance such as tenant, department, access tier, source document, and page or row numbers.

## Architecture

- `etl/extract.py`: reads supported file types and yields text plus provenance metadata.
- `etl/chunking.py`: creates sentence-aware chunks with bounded overlap.
- `etl/metadata.py`: validates tenant and access metadata and adds document provenance.
- `etl/index.py`: embeds and writes records to ChromaDB or Qdrant.
- `etl/pipeline.py`: orchestrates the end-to-end ETL flow.
- `etl/cli.py`: CLI entry point for local ingestion.

## Prerequisites

- Python 3.11+
- A virtual environment is recommended.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Environment variables

The project reads `.env` using `pydantic-settings`.

```dotenv
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
BATCH_SIZE=64
CHUNK_SIZE_CHARS=1800
CHUNK_OVERLAP_CHARS=250
CHROMA_PATH=./data/chroma
CHROMA_COLLECTION=client_legacy_documents
QDRANT_URL=
QDRANT_API_KEY=
QDRANT_COLLECTION=client_legacy_documents
DEFAULT_TENANT_ID=
DEFAULT_DEPARTMENT=unknown
DEFAULT_ACCESS_TIER=
```

`DEFAULT_TENANT_ID` and `DEFAULT_ACCESS_TIER` are intentionally required for files that lack metadata. The pipeline fails closed instead of silently making sensitive data public or cross-tenant.

## Running the ETL pipeline

```bash
python -m etl.cli ingest ./sample-documents --backend chroma --dry-run
python -m etl.cli ingest ./sample-documents --backend chroma
python -m etl.cli ingest ./sample-documents --backend qdrant
```

CLI options:
- `input_dir`: folder containing source documents
- `--backend {chroma,qdrant}`
- `--dry-run`: extract and chunk without indexing
- `--output-manifest`: optional JSONL chunk manifest path

## Running tests

```bash
pytest tests -q
```

## Supported input types

- PDF
- CSV
- Markdown (`.md`, `.markdown`)
- Plain text (`.txt`)

## Limitations and security considerations

- Large PDFs and CSV files are processed in memory during extraction.
- There is no built-in malicious file scanning or content policy enforcement before indexing.
- Embedding models may require network access on the first run.
- The pipeline intentionally fails closed if tenant or sensitivity metadata is missing.

## Example output

```bash
python -m etl.cli ingest ./documents --backend chroma
```

returns a summary with file counts, chunk counts, indexing counts, elapsed time, and any extraction errors.
