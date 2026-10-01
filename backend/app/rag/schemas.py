from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """
    A document chunk retrieved from the vector database.
    """

    chunk_id: str
    document_id: str
    content: str
    score: float


class RetrievalResponse(BaseModel):
    """
    Collection of chunks retrieved for a query.
    """

    query: str
    results: list[RetrievedChunk] = Field(default_factory=list)
