from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """A document chunk retrieved from the vector store."""

    chunk_id: str
    document_id: str
    content: str
    score: float


class RAGContext(BaseModel):
    """Context assembled from retrieved document chunks."""

    query: str
    context: str
    chunks: list[RetrievedChunk] = Field(default_factory=list)


class RAGResponse(BaseModel):
    """Response returned by the RAG pipeline."""

    answer: str
    sources: list[RetrievedChunk] = Field(default_factory=list)
