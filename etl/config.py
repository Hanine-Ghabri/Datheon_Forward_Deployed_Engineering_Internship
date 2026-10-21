from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    batch_size: int = 64
    chunk_size_chars: int = 1800
    chunk_overlap_chars: int = 250
    chroma_path: str = "./data/chroma"
    chroma_collection: str = "client_legacy_documents"
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection: str = "client_legacy_documents"
    default_tenant_id: str = ""
    default_department: str = "unknown"
    default_access_tier: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
