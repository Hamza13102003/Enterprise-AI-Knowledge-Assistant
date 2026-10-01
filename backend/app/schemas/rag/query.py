from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    """Request schema for querying the RAG system."""

    query: str = Field(min_length=1, max_length=5000)
    top_k: int = Field(default=5, ge=1, le=20)
