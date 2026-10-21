from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterator

from pypdf import PdfReader

SUPPORTED = {".pdf", ".csv", ".md", ".markdown", ".txt"}


def load_sidecar(path: Path) -> dict:
    sidecar = path.with_name(path.name + ".meta.json")
    if not sidecar.exists():
        return {}
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Metadata sidecar must be an object: {sidecar}")
    return data


def extract_file(path: Path) -> Iterator[tuple[str, dict]]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path), strict=True)
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported")
        for page_no, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                yield text, {"page_number": page_no}
    elif suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return
            for row_no, row in enumerate(reader, start=2):
                cleaned = {str(k): (v or "").strip() for k, v in row.items() if k}
                text = "\n".join(f"{k}: {v}" for k, v in cleaned.items() if v)
                if text:
                    yield text, {"row_number": row_no}
    elif suffix in {".md", ".markdown", ".txt"}:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if text:
            yield text, {}
    else:
        return
