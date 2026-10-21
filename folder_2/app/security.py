from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.config import settings

CLEARANCE = {"public": 0, "confidential": 1, "secret": 2, "top_secret": 3}
bearer = HTTPBearer(auto_error=False)

@dataclass(frozen=True)
class Principal:
    subject: str
    tenant_id: str
    roles: frozenset[str]
    clearance: str
    permissions: frozenset[str]

    @property
    def clearance_rank(self) -> int:
        return CLEARANCE[self.clearance]

def encode_demo_token(subject="alice", tenant_id="acme", roles=None,
                      clearance="confidential", permissions=None) -> str:
    """Local-development helper only. Never expose as a production token issuer."""
    now = datetime.now(timezone.utc)
    claims = {
        "sub": subject, "tenant_id": tenant_id,
        "roles": roles or ["employee"], "clearance": clearance,
        "permissions": permissions or ["document:read", "document:write"],
        "iss": settings.jwt_issuer, "aud": settings.jwt_audience,
        "iat": now, "exp": now + timedelta(hours=1),
    }
    return jwt.encode(claims, settings.jwt_secret, algorithm="HS256")

def principal_from_claims(claims: dict[str, Any]) -> Principal:
    clearance, tenant_id, subject = claims.get("clearance"), claims.get("tenant_id"), claims.get("sub")
    roles, permissions = claims.get("roles"), claims.get("permissions", [])
    if (not isinstance(tenant_id, str) or not tenant_id or not isinstance(subject, str) or not subject
        or clearance not in CLEARANCE or not isinstance(roles, list)
        or not all(isinstance(x, str) for x in roles) or not isinstance(permissions, list)
        or not all(isinstance(x, str) for x in permissions)):
        raise HTTPException(status_code=401, detail="Invalid identity claims")
    return Principal(subject, tenant_id, frozenset(roles), clearance, frozenset(permissions))

def get_principal(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> Principal:
    if creds is None:
        raise HTTPException(status_code=401, detail="Bearer token required")
    try:
        claims = jwt.decode(
            creds.credentials, settings.jwt_secret, algorithms=["HS256"],
            issuer=settings.jwt_issuer, audience=settings.jwt_audience,
            options={"require": ["exp", "iat", "sub", "tenant_id", "clearance", "roles"]},
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return principal_from_claims(claims)

def require_permission(permission: str):
    def dependency(principal: Principal = Depends(get_principal)) -> Principal:
        if permission not in principal.permissions:
            raise HTTPException(status_code=403, detail="Insufficient permission")
        return principal
    return dependency
