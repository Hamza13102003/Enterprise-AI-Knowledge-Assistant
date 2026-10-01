from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.api.v1.documents.upload import router as upload_router
from app.database.models.user import User
from app.database.session import get_db_session
from app.repositories.document_repository import DocumentRepository
from app.schemas.documents.list import (
    DocumentListItem,
    DocumentListResponse,
)
from app.vector_store.qdrant import QdrantService

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get(
    "",
    response_model=DocumentListResponse,
)
async def list_documents(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> DocumentListResponse:
    """
    Return documents belonging to the authenticated user.
    """
    repository = DocumentRepository(db)

    documents = await repository.list_documents(
        uploaded_by=current_user.id,
    )

    return DocumentListResponse(
        documents=[DocumentListItem.model_validate(doc) for doc in documents],
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a document owned by the authenticated user
    and its indexed vector chunks.
    """
    repository = DocumentRepository(db)
    vector_store = QdrantService()

    document = await repository.get_by_id(
        document_id,
        uploaded_by=current_user.id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    try:
        await vector_store.delete_by_document_id(document_id)

        await repository.delete(document)

        await db.commit()

    except Exception as exc:
        await db.rollback()

        print(
            "DOCUMENT DELETE ERROR: "
            f"{type(exc).__name__}: {exc}",
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document deletion failed.",
        ) from exc

    finally:
        await vector_store.close()


@router.get(
    "/{document_id}",
    response_model=DocumentListItem,
)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> DocumentListItem:
    """
    Return a single document owned by the authenticated user.
    """
    repository = DocumentRepository(db)

    document = await repository.get_by_id(
        document_id,
        uploaded_by=current_user.id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return DocumentListItem.model_validate(document)


router.include_router(upload_router)