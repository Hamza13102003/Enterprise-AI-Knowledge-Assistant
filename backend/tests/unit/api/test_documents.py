from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.main import app

client = TestClient(app)


def create_mock_user():
    """Create a mock authenticated user."""
    user_id = uuid4()

    return type(
        "MockUser",
        (),
        {
            "id": user_id,
            "is_active": True,
        },
    )()


def create_mock_document(
    *,
    user_id,
    document_id=None,
    filename="company_policy.txt",
    content_type="text/plain",
    file_size=1024,
    status="completed",
    chunks_count=3,
):
    """Create a mock document matching the Document model."""
    now = datetime.now(UTC)

    return type(
        "MockDocument",
        (),
        {
            "id": document_id or uuid4(),
            "filename": filename,
            "content_type": content_type,
            "file_size": file_size,
            "status": status,
            "chunks_count": chunks_count,
            "uploaded_by": user_id,
            "created_at": now,
            "updated_at": now,
        },
    )()


def test_list_documents() -> None:
    user = create_mock_user()

    mock_document = create_mock_document(
        user_id=user.id,
        filename="company_policy.txt",
        content_type="text/plain",
        file_size=1024,
        status="completed",
        chunks_count=3,
    )

    mock_repository = AsyncMock()
    mock_repository.list_documents.return_value = [
        mock_document,
    ]

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        with patch(
            "app.api.v1.documents.router.DocumentRepository",
            return_value=mock_repository,
        ):
            response = client.get("/api/v1/documents")

        assert response.status_code == 200

        body = response.json()

        assert body["documents"][0]["filename"] == "company_policy.txt"
        assert body["documents"][0]["content_type"] == "text/plain"
        assert body["documents"][0]["file_size"] == 1024
        assert body["documents"][0]["status"] == "completed"
        assert body["documents"][0]["chunks_count"] == 3
        assert body["documents"][0]["uploaded_by"] == str(user.id)
        assert "created_at" in body["documents"][0]
        assert "updated_at" in body["documents"][0]

        mock_repository.list_documents.assert_awaited_once_with(
            uploaded_by=user.id,
        )

    finally:
        app.dependency_overrides.clear()


def test_get_document() -> None:
    user = create_mock_user()
    document_id = uuid4()

    mock_document = create_mock_document(
        user_id=user.id,
        document_id=document_id,
        filename="employee_handbook.txt",
        content_type="text/plain",
        file_size=2048,
        status="completed",
        chunks_count=5,
    )

    mock_repository = AsyncMock()
    mock_repository.get_by_id.return_value = mock_document

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        with patch(
            "app.api.v1.documents.router.DocumentRepository",
            return_value=mock_repository,
        ):
            response = client.get(
                f"/api/v1/documents/{document_id}",
            )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == str(document_id)
        assert body["filename"] == "employee_handbook.txt"
        assert body["content_type"] == "text/plain"
        assert body["file_size"] == 2048
        assert body["status"] == "completed"
        assert body["chunks_count"] == 5
        assert body["uploaded_by"] == str(user.id)
        assert "created_at" in body
        assert "updated_at" in body

        mock_repository.get_by_id.assert_awaited_once_with(
            document_id,
            uploaded_by=user.id,
        )

    finally:
        app.dependency_overrides.clear()


def test_get_document_not_found() -> None:
    user = create_mock_user()
    document_id = uuid4()

    mock_repository = AsyncMock()
    mock_repository.get_by_id.return_value = None

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        with patch(
            "app.api.v1.documents.router.DocumentRepository",
            return_value=mock_repository,
        ):
            response = client.get(
                f"/api/v1/documents/{document_id}",
            )

        assert response.status_code == 404

        body = response.json()

        assert body["detail"] == "Document not found."

        mock_repository.get_by_id.assert_awaited_once_with(
            document_id,
            uploaded_by=user.id,
        )

    finally:
        app.dependency_overrides.clear()


def test_delete_document_not_found() -> None:
    user = create_mock_user()
    document_id = uuid4()

    mock_repository = AsyncMock()
    mock_repository.get_by_id.return_value = None

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        with patch(
            "app.api.v1.documents.router.DocumentRepository",
            return_value=mock_repository,
        ):
            response = client.delete(
                f"/api/v1/documents/{document_id}",
            )

        assert response.status_code == 404

        body = response.json()

        assert body["detail"] == "Document not found."

        mock_repository.get_by_id.assert_awaited_once_with(
            document_id,
            uploaded_by=user.id,
        )

    finally:
        app.dependency_overrides.clear()


def test_upload_rejects_unsupported_file_type() -> None:
    user = create_mock_user()

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = client.post(
            "/api/v1/documents/upload",
            files={
                "file": (
                    "malicious.exe",
                    b"fake executable content",
                    "application/octet-stream",
                ),
            },
        )

        assert response.status_code == 415

        body = response.json()

        assert (
            body["detail"]
            == "Unsupported document type. Allowed types: PDF, DOCX, TXT."
        )

    finally:
        app.dependency_overrides.clear()


def test_upload_rejects_empty_file() -> None:
    user = create_mock_user()

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = client.post(
            "/api/v1/documents/upload",
            files={
                "file": (
                    "empty.txt",
                    b"",
                    "text/plain",
                ),
            },
        )

        assert response.status_code == 400

        body = response.json()

        assert body["detail"] == "The uploaded file is empty."

    finally:
        app.dependency_overrides.clear()