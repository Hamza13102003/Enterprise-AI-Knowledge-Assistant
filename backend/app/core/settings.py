from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str
    app_env: str
    debug: bool

    host: str
    port: int

    secret_key: str
    access_token_expire_minutes: int

    database_url: str

    qdrant_host: str
    qdrant_port: int

    embedding_model: str = "nomic-embed-text"
    embedding_dimension: int = 768

    ollama_host: str
    ollama_model: str

    ollama_temperature: float = 0.0
    ollama_top_p: float = 0.9
    ollama_num_predict: int = 256
    ollama_timeout: float = 120.0

    rag_retrieval_threshold: float = 0.70
    rag_relevance_threshold: float = 0.72

    log_level: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance loaded from the environment."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
