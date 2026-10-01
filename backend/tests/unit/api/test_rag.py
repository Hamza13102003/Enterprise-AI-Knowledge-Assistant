from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.main import app

client = TestClient(app)


def test_rag_query() -> None:
    user_id = uuid4()

    mock_user = type(
        "MockUser",
        (),
        {
            "id": user_id,
        },
    )()

    mock_result = {
        "answer": "The company provides 20 days of annual leave.",
        "sources": [],
    }

    app.dependency_overrides[get_current_user] = lambda: mock_user

    try:
        with patch(
            "app.api.v1.rag.router.RAGService.answer",
            new_callable=AsyncMock,
            return_value=mock_result,
        ) as mock_answer:
            response = client.post(
                "/api/v1/rag/query",
                json={
                    "query": "What is the annual leave policy?",
                    "top_k": 5,
                },
            )

        assert response.status_code == 200

        body = response.json()

        assert body["success"] is True
        assert body["message"] == "RAG query completed successfully."
        assert body["data"]["answer"] == (
            "The company provides 20 days of annual leave."
        )

        mock_answer.assert_awaited_once_with(
            "What is the annual leave policy?",
            user_id=user_id,
            top_k=5,
        )

    finally:
        app.dependency_overrides.clear()