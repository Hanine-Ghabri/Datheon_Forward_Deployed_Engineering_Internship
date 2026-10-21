from functools import lru_cache
from typing import Any
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
from app.config import settings
from app.security import Principal, CLEARANCE

@lru_cache(maxsize=1)
def embedder():
    return SentenceTransformer(settings.embedding_model)

@lru_cache(maxsize=1)
def reranker():
    return CrossEncoder(settings.reranker_model)

@lru_cache(maxsize=1)
def collection():
    client = chromadb.PersistentClient(path=settings.chroma_path)
    return client.get_or_create_collection(name="enterprise_chunks", metadata={"hnsw:space": "cosine"})

def rewrite_queries(question: str) -> list[str]:
    """Deterministic query variants; replace with a controlled LLM rewriter if desired."""
    q = " ".join(question.strip().split())
    variants = [q]
    if len(q.split()) >= 4:
        variants.append("key facts and evidence about " + q)
    return list(dict.fromkeys(variants))[:3]

def chunk_is_authorized(meta: dict[str, Any], principal: Principal) -> bool:
    # Fail closed on missing/malformed ACL metadata.
    if meta.get("tenant_id") != principal.tenant_id:
        return False
    required = meta.get("required_clearance")
    if required not in CLEARANCE or CLEARANCE[required] > principal.clearance_rank:
        return False
    allowed_roles = meta.get("allowed_roles")
    if not isinstance(allowed_roles, list) or not set(allowed_roles).intersection(principal.roles):
        return False
    return True

def retrieve(question: str, principal: Principal) -> list[dict[str, Any]]:
    col, candidates = collection(), {}
    for query in rewrite_queries(question):
        where = {"$and": [
            {"tenant_id": {"$eq": principal.tenant_id}},
            {"required_clearance_rank": {"$lte": principal.clearance_rank}},
        ]}
        result = col.query(query_embeddings=[embedder().encode(query).tolist()],
            n_results=settings.top_k, where=where,
            include=["documents", "metadatas", "distances"])
        ids, docs = result.get("ids", [[]])[0], result.get("documents", [[]])[0]
        metas, distances = result.get("metadatas", [[]])[0], result.get("distances", [[]])[0]
        for cid, doc, meta, distance in zip(ids, docs, metas, distances):
            if not chunk_is_authorized(meta or {}, principal):
                continue
            if cid not in candidates or distance < candidates[cid]["distance"]:
                candidates[cid] = {"id": cid, "text": doc, "metadata": meta, "distance": distance}
    docs = list(candidates.values())
    if not docs:
        return []
    scores = reranker().predict([(question, d["text"]) for d in docs])
    for item, score in zip(docs, scores):
        item["rerank_score"] = float(score)
    docs.sort(key=lambda x: x["rerank_score"], reverse=True)
    return [d for d in docs if chunk_is_authorized(d["metadata"], principal)][:settings.final_k]

def index_chunks(chunks: list[dict[str, Any]]) -> None:
    if chunks:
        collection().upsert(
            ids=[c["id"] for c in chunks],
            documents=[c["text"] for c in chunks],
            metadatas=[c["metadata"] for c in chunks],
            embeddings=embedder().encode([c["text"] for c in chunks]).tolist())
