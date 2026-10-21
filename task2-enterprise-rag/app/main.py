import hashlib
import io
from typing import Literal

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from pypdf import PdfReader

from app.answer import generate_answer
from app.config import settings
from app.retrieval import index_chunks, retrieve
from app.security import CLEARANCE, Principal, require_permission

app = FastAPI(title="Enterprise Multi-Tenant RAG", version="1.0.0")


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    document_id: str = Form(..., min_length=1, max_length=128),
    allowed_roles: str = Form(...),
    required_clearance: Literal["public", "confidential", "secret", "top_secret"] = Form(...),
    principal: Principal = Depends(require_permission("document:write")),
):
    if file.content_type != "application/pdf":
        raise HTTPException(415, "Only PDF documents are supported")
    raw = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(raw) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, "File exceeds upload size limit")
    try:
        reader = PdfReader(io.BytesIO(raw), strict=True)
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are unsupported")
        roles = sorted(set(x.strip() for x in allowed_roles.split(",") if x.strip()))
        if not roles:
            raise ValueError("At least one allowed role is required")
        chunks, digest = [], hashlib.sha256(raw).hexdigest()
        for page_index, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()
            words, chunk_size, overlap = text.split(), 220, 35
            for start in range(0, len(words), chunk_size - overlap):
                part = " ".join(words[start:start + chunk_size])
                if not part:
                    continue
                chunk_id = f"{principal.tenant_id}:{document_id}:{digest[:16]}:p{page_index + 1}:c{len(chunks)}"
                chunks.append({
                    "id": chunk_id,
                    "text": part,
                    "metadata": {
                        "tenant_id": principal.tenant_id,
                        "document_id": document_id,
                        "page_number": page_index + 1,
                        "required_clearance": required_clearance,
                        "required_clearance_rank": CLEARANCE[required_clearance],
                        "allowed_roles": roles,
                        "uploaded_by": principal.subject,
                        "content_sha256": digest,
                    },
                })
        if not chunks:
            raise ValueError("No extractable text found in PDF")
        index_chunks(chunks)
        return {"document_id": document_id, "pages": len(reader.pages), "chunks_indexed": len(chunks)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(400, f"Could not ingest PDF: {type(exc).__name__}")


@app.post("/query")
def query(request: QueryRequest, principal: Principal = Depends(require_permission("document:read"))):
    return generate_answer(request.question, retrieve(request.question, principal), principal)
