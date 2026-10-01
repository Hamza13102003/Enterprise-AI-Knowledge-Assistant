# app/repositories/document_repository.py
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.document import Document
class DocumentRepository:
    """
    Repository for document persistence.
    """
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    async def create(
        self,
        *,
        filename: str,
        content_type: str,
        file_size: int,
        status: str = "processing",
        uploaded_by: UUID | None = None,
    ) -> Document:
        document = Document(
            filename=filename,
            content_type=content_type,
            file_size=file_size,
            status=status,
            chunks_count=0,
            uploaded_by=uploaded_by,
        )
        self.session.add(document)
        await self.session.flush()
        return document
    async def mark_completed(
        self,
        document: Document,
        *,
        chunks_count: int,
    ) -> Document:
        document.status = "completed"
        document.chunks_count = chunks_count
        await self.session.flush()
        return document
    async def mark_failed(
        self,
        document: Document,
    ) -> Document:
        document.status = "failed"
        await self.session.flush()
        return document
    async def delete(
        self,
        document: Document,
    ) -> None:
        """
        Delete a document from the database.
        """
        await self.session.delete(document)
        await self.session.flush()
    async def list_documents(
        self,
        *,
        uploaded_by: UUID,
    ) -> list[Document]:
        """
        Return documents belonging to a specific user,
        ordered by newest first.
        """
        result = await self.session.execute(
            select(Document)
            .where(Document.uploaded_by == uploaded_by)
            .order_by(Document.created_at.desc()),
        )
        return list(result.scalars().all())
    async def get_by_id(
        self,
        document_id: UUID,
        *,
        uploaded_by: UUID | None = None,
    ) -> Document | None:
        """
        Return a document by ID.
        When uploaded_by is provided, the document must belong
        to that user.
        """
        statement = select(Document).where(
            Document.id == document_id,
        )
        if uploaded_by is not None:
            statement = statement.where(
                Document.uploaded_by == uploaded_by,
            )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
