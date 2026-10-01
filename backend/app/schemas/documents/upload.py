from uuid import UUID

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    """Response returned after successfully indexing a document."""

    document_id: UUID
    filename: str
    chunks_indexed: int
    message: str
