from __future__ import annotations
from functools import lru_cache
from uuid import uuid5, NAMESPACE_URL
import chromadb
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from etl.config import settings

@lru_cache(maxsize=1)
def embedder():
    return SentenceTransformer(settings.embedding_model)

def stable_id(meta: dict, chunk: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"{meta['tenant_id']}|{meta['document_id']}|{meta.get('page_number','')}|{meta.get('row_number','')}|{chunk}"))

def _embed(texts: list[str]) -> list[list[float]]:
    return embedder().encode(texts, batch_size=settings.batch_size, normalize_embeddings=True).tolist()

def index_chroma(records: list[dict]) -> int:
    client = chromadb.PersistentClient(path=settings.chroma_path)
    collection = client.get_or_create_collection(
        name=settings.chroma_collection, metadata={"hnsw:space": "cosine"})
    count = 0
    for start in range(0, len(records), settings.batch_size):
        batch = records[start:start + settings.batch_size]
        collection.upsert(
            ids=[r["id"] for r in batch],
            documents=[r["text"] for r in batch],
            metadatas=[r["metadata"] for r in batch],
            embeddings=_embed([r["text"] for r in batch]))
        count += len(batch)
    return count

def index_qdrant(records: list[dict]) -> int:
    if settings.qdrant_url:
        client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)
    else:
        client = QdrantClient(path="./data/qdrant")
    vectors = _embed([r["text"] for r in records]) if records else []
    if not records:
        return 0
    dim = len(vectors[0])
    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE))
    count = 0
    for start in range(0, len(records), settings.batch_size):
        batch, vec_batch = records[start:start + settings.batch_size], vectors[start:start + settings.batch_size]
        points = [models.PointStruct(id=r["id"], vector=v, payload={"text": r["text"], **r["metadata"]})
                  for r, v in zip(batch, vec_batch)]
        client.upsert(collection_name=settings.qdrant_collection, points=points, wait=True)
        count += len(points)
    return count
