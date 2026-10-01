from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.rag.context import RAGContextBuilder
from app.rag.prompt import RAGPromptBuilder
from app.rag.retriever import RetrievedChunk
from app.rag.service import RAGService


@pytest.mark.asyncio
async def test_rag_service_generates_answer() -> None:
    retriever = MagicMock()
    retriever.retrieve = AsyncMock()
    retriever.calculate_retrieval_confidence = MagicMock()

    llm_service = AsyncMock()

    user_id = uuid4()
    document_id = str(uuid4())
    chunk_id = str(uuid4())

    retriever.retrieve.return_value = [
        RetrievedChunk(
            chunk_id=chunk_id,
            document_id=document_id,
            content=(
                "The company uses Kubernetes for "
                "container orchestration."
            ),
            score=0.95,
        )
    ]

    retriever.calculate_retrieval_confidence.return_value = 0.95

    llm_service.generate.return_value = (
        "The company uses Kubernetes for "
        "container orchestration."
    )

    service = RAGService(
        retriever=retriever,
        context_builder=RAGContextBuilder(),
        prompt_builder=RAGPromptBuilder(),
        llm_service=llm_service,
    )

    result = await service.answer(
        "What does the company use for container orchestration?",
        user_id=user_id,
    )

    assert result.answer == (
        "The company uses Kubernetes for "
        "container orchestration."
    )

    assert len(result.sources) == 1