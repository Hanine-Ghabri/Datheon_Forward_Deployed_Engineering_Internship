from __future__ import annotations
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from etl.config import settings

ALLOWED_TIERS = {"public", "internal", "confidential", "secret", "top_secret"}

def build_metadata(path: Path, extra: dict, source_root: Path, provenance: dict) -> dict:
    # Missing tenant/access tier is intentionally a hard error: do not silently make
    # sensitive data public or cross-tenant.
    tenant = extra.get("tenant_id") or settings.default_tenant_id
    tier = extra.get("access_tier") or settings.default_access_tier
    if not tenant:
        raise ValueError(f"Missing tenant_id in metadata for {path}")
    if tier not in ALLOWED_TIERS:
        raise ValueError(f"Missing/invalid access_tier in metadata for {path}")
    try:
        relative = path.resolve().relative_to(source_root.resolve()).as_posix()
    except ValueError:
        relative = path.name
    raw_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    modified = extra.get("modified_date") or datetime.fromtimestamp(
        path.stat().st_mtime, tz=timezone.utc).date().isoformat()
    return {
        "tenant_id": str(tenant),
        "department": str(extra.get("department") or settings.default_department),
        "access_tier": str(tier),
        "modified_date": str(modified),
        "source": str(extra.get("source") or relative),
        "document_id": str(extra.get("document_id") or raw_hash[:24]),
        "content_sha256": raw_hash,
        **provenance,
    }
