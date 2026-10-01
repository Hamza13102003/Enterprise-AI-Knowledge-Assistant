from uuid import uuid4

from app.rag.context import RAGContextBuilder
from app.schemas.rag import RetrievedChunk


def test_context_builder_combines_chunks() -> None:
    document_id = str(uuid4())
    chunk_id = str(uuid4())

    chunks = [
        RetrievedChunk(
            chunk_id=chunk_id,
            document_id=document_id,
            content="Enterprise AI knowledge content.",
            score=0.91,
        )
    ]

    result = RAGContextBuilder().build(
        "What is the enterprise knowledge system?",
        chunks,
    )

    assert result.query == "What is the enterprise knowledge system?"
    assert len(result.chunks) == 1
    assert "Enterprise AI knowledge content." in result.context
    assert "[Source 1]" in result.context
