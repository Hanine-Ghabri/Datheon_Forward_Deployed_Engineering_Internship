from app.security import Principal, CLEARANCE
from app.retrieval import chunk_is_authorized

def principal(tenant="acme", roles=("employee",), clearance="confidential"):
    return Principal("u1", tenant, frozenset(roles), clearance, frozenset({"document:read"}))

def metadata(tenant="acme", roles=None, clearance="public"):
    return {"tenant_id": tenant, "allowed_roles": roles or ["employee"],
            "required_clearance": clearance, "required_clearance_rank": CLEARANCE[clearance],
            "document_id": "doc1", "page_number": 1}

def test_allowed_document():
    assert chunk_is_authorized(metadata(), principal())

def test_cross_tenant_denied():
    assert not chunk_is_authorized(metadata(tenant="other"), principal())

def test_role_mismatch_denied():
    assert not chunk_is_authorized(metadata(roles=["finance"]), principal())

def test_higher_clearance_denied():
    assert not chunk_is_authorized(metadata(clearance="secret"), principal())

def test_missing_acl_fails_closed():
    assert not chunk_is_authorized({"tenant_id": "acme"}, principal())
