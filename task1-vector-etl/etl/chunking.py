from __future__ import annotations

import re


def semantic_chunks(text: str, max_chars: int = 1800, overlap: int = 250) -> list[str]:
    """Sentence-aware chunking: prefer sentence boundaries, with bounded overlap."""
    if max_chars < 100:
        raise ValueError("max_chars must be >= 100")
    if overlap < 0 or overlap >= max_chars:
        raise ValueError("overlap must be >= 0 and less than max_chars")
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", normalized)
    chunks, current = [], ""
    for sentence in sentences:
        if len(sentence) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            start = 0
            while start < len(sentence):
                end = min(len(sentence), start + max_chars)
                chunks.append(sentence[start:end])
                if end == len(sentence):
                    break
                start = end - overlap
            continue
        candidate = f"{current} {sentence}".strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            prefix = current[-overlap:] if overlap and current else ""
            current = f"{prefix} {sentence}".strip()
    if current:
        chunks.append(current)
    return list(dict.fromkeys(c for c in chunks if c))
