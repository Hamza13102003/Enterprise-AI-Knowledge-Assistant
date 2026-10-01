from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from qdrant_client.models import ScoredPoint

from app.rag.retriever import RAGRetriever


@pytest.mark.asyncio
async def test_retrieve_returns_relevant_chunks() -> None:
    embedding_service = AsyncMock()
    vector_store = AsyncMock()

    query_embedding = [0.1, 0.2, 0.3]

    embedding_service.embed.return_value = query_embedding

    user_id = uuid4()
    chunk_id = uuid4()
    document_id = uuid4()

    vector_store.search.return_value = [
        ScoredPoint(
            id=str(chunk_id),
            version=1,
            score=0.92,
            payload={
                "chunk_id": str(chunk_id),
                "document_id": str(document_id),
                "uploaded_by": str(user_id),
                "content": "Enterprise knowledge assistant content.",
            },
        )
    ]

    retriever = RAGRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    results = await retriever.retrieve(
        "What is the enterprise knowledge assistant?",
        user_id=user_id,
    )

    assert len(results) == 1
    assert results[0].chunk_id == str(chunk_id)
    assert results[0].document_id == str(document_id)
    assert results[0].content == "Enterprise knowledge assistant content."
    assert results[0].score == 0.92

    embedding_service.embed.assert_awaited_once_with(
        "What is the enterprise knowledge assistant?"
    )

    vector_store.search.assert_awaited_once_with(
        query_embedding,
        user_id=user_id,
        limit=5,
    )


@pytest.mark.asyncio
async def test_empty_query_returns_no_results() -> None:
    embedding_service = AsyncMock()
    vector_store = AsyncMock()

    retriever = RAGRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    results = await retriever.retrieve(
        "   ",
        user_id=uuid4(),
    )

    assert results == []

    embedding_service.embed.assert_not_awaited()
    vector_store.search.assert_not_awaited()