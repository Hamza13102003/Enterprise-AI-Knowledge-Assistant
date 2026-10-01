from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.api.v1.documents.dependencies import (
    get_document_ingestion_service,
)
from app.database.models.user import User
from app.database.session import get_db_session
from app.ingestion.service import DocumentIngestionService
from app.repositories.document_repository import DocumentRepository
from app.schemas.documents.upload import DocumentUploadResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    ingestion_service: DocumentIngestionService = Depends(
        get_document_ingestion_service,
    ),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> DocumentUploadResponse:
    """
    Upload, persist, process, and index a document.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A filename is required.",
        )

    filename = Path(file.filename).name
    suffix = Path(filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                "Unsupported document type. "
                "Allowed types: PDF, DOCX, TXT."
            ),
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty.",
        )

    repository = DocumentRepository(db)

    document = await repository.create(
        filename=filename,
        content_type=file.content_type or "application/octet-stream",
        file_size=len(contents),
        uploaded_by=current_user.id,
    )

    await db.commit()

    try:
        with TemporaryDirectory() as temporary_directory:
            temporary_path = Path(
                temporary_directory,
            ) / filename

            temporary_path.write_bytes(contents)

            chunks_indexed = await ingestion_service.ingest(
                temporary_path,
                document_id=document.id,
                uploaded_by=current_user.id,
            )

        await repository.mark_completed(
            document,
            chunks_count=chunks_indexed,
        )

        await db.commit()

    except ValueError as exc:
        await repository.mark_failed(document)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        await repository.mark_failed(document)
        await db.commit()

        print(
            "DOCUMENT PROCESSING ERROR: "
            f"{type(exc).__name__}: {exc}",
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document processing failed.",
        ) from exc

    return DocumentUploadResponse(
        document_id=document.id,
        filename=filename,
        chunks_indexed=chunks_indexed,
        message="Document uploaded and indexed successfully.",
    )