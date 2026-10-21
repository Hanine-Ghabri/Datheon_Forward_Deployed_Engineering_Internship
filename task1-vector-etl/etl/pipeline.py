from __future__ import annotations

import json
import time
from pathlib import Path

from etl.chunking import semantic_chunks
from etl.config import settings
from etl.extract import SUPPORTED, extract_file, load_sidecar
from etl.index import index_chroma, index_qdrant, stable_id
from etl.metadata import build_metadata


def run_pipeline(input_dir: str, backend: str = "chroma", dry_run: bool = False,
                 output_manifest: str | None = None) -> dict:
    root = Path(input_dir).resolve()
    if not root.is_dir():
        raise ValueError(f"Input directory does not exist: {root}")
    started = time.perf_counter()
    records, errors, files_seen = [], [], 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED:
            continue
        files_seen += 1
        try:
            sidecar = load_sidecar(path)
            for extracted_text, provenance in extract_file(path):
                metadata = build_metadata(path, sidecar, root, provenance)
                for chunk_no, chunk in enumerate(semantic_chunks(
                    extracted_text, settings.chunk_size_chars, settings.chunk_overlap_chars)):
                    meta = {**metadata, "chunk_number": chunk_no}
                    records.append({"id": stable_id(meta, chunk), "text": chunk, "metadata": meta})
        except Exception as exc:
            errors.append({"file": str(path.relative_to(root)), "error": type(exc).__name__,
                           "message": str(exc)})
    if output_manifest:
        manifest = Path(output_manifest)
        manifest.parent.mkdir(parents=True, exist_ok=True)
        with manifest.open("w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
    indexed = 0
    if not dry_run:
        if backend == "chroma":
            indexed = index_chroma(records)
        elif backend == "qdrant":
            indexed = index_qdrant(records)
        else:
            raise ValueError("backend must be 'chroma' or 'qdrant'")
    elapsed = time.perf_counter() - started
    return {"files_seen": files_seen, "chunks_created": len(records), "chunks_indexed": indexed,
            "errors": errors, "elapsed_seconds": round(elapsed, 3),
            "chunks_per_second": round(len(records) / elapsed, 2) if elapsed else 0,
            "dry_run": dry_run, "backend": backend}
