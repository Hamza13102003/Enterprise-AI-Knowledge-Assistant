from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentListItem(BaseModel):
    """Document information returned by the document listing API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    content_type: str
    file_size: int
    status: str
    chunks_count: int
    uploaded_by: UUID | None
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    """Response containing uploaded documents."""

    documents: list[DocumentListItem]
