# Enterprise Multi-Tenant RAG with RBAC

Security-first FastAPI reference implementation: tenant/clearance-filtered retrieval, query rewriting, cross-encoder reranking, PDF page provenance, and evidence-grounded answers.

## Quick start
Python 3.11+ recommended.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
python scripts/make_demo_token.py
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs. Set a strong `JWT_SECRET` and `OPENAI_API_KEY` in `.env`. Without an LLM key, the API abstains instead of inventing an answer. Embedding and reranker weights download on first use.

The demo token issuer is for local development only. Production must use OIDC/JWKS and verify issuer, audience, expiry, rotation, and trusted identity attributes.

## Endpoints
- `POST /documents`: upload PDF with `document_id`, comma-separated `allowed_roles`, and `required_clearance`.
- `POST /query`: answer using only authorized evidence.
- `GET /health`: liveness endpoint.

## Security properties
- Tenant and clearance filters applied at vector-store retrieval.
- Application-level role, tenant, and clearance validation fails closed.
- Authorization rechecked before evidence reaches the answer model.
- Page numbers come from PDF ingestion metadata, never from the LLM.
- The answer model must cite evidence IDs; missing evidence results in abstention.
- Uploaded content is treated as untrusted data.

## Production hardening checklist
1. Replace demo JWT authentication with your IdP and centralized policy service.
2. Restrict document ingestion and ACL assignment to a trusted ingestion/admin service.
3. Use secured managed vector storage, TLS, encryption, tenant isolation, backups, rate limits, and audit logs.
4. Make ACL changes invalidate stale chunks, caches, and derived indexes.
5. Add malware scanning, PDF resource limits, a durable ingestion worker, and observability.
6. Test cross-tenant leakage, clearance boundaries, prompt injection, citation accuracy, and abstention.
7. For high-assurance use, add independent claim verification and human review.

This is a production-oriented starter, not a security certification. Review and threat-model it before deployment.
