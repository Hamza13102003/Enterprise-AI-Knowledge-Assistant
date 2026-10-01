from pathlib import Path
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.ingestion.chunking.text_chunker import TextChunker
from app.ingestion.models.document import DocumentPage, ExtractedDocument
from app.ingestion.service import DocumentIngestionService


@pytest.mark.asyncio
async def test_ingest_indexes_document_chunks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "knowledge.txt"
    file_path.write_text(
        "Enterprise AI knowledge assistant content.",
        encoding="utf-8",
    )

    extracted_document = ExtractedDocument(
        filename="knowledge.txt",
        content_type="text/plain",
        pages=[
            DocumentPage(
                page_number=1,
                text="Enterprise AI knowledge assistant content.",
            ),
        ],
    )

    def extract_mock(path: Path) -> ExtractedDocument:
        return extracted_document

    monkeypatch.setattr(
        "app.ingestion.service.extract_txt",
        extract_mock,
    )

    indexer = AsyncMock()

    service = DocumentIngestionService(
        chunker=TextChunker(
            chunk_size=1000,
            chunk_overlap=200,
        ),
        indexer=indexer,
    )

    document_id = uuid4()
    uploaded_by = uuid4()

    result = await service.ingest(
        file_path,
        document_id=document_id,
        uploaded_by=uploaded_by,
    )

    assert result == 1
    indexer.index_chunks.assert_awaited_once()

    indexed_chunks = indexer.index_chunks.await_args.args[0]

    assert len(indexed_chunks) == 1
    assert indexed_chunks[0]["content"] == (
        "Enterprise AI knowledge assistant content."
    )
    assert indexed_chunks[0]["document_id"] == document_id
    assert indexed_chunks[0]["uploaded_by"] == uploaded_by
    assert indexed_chunks[0]["id"]


@pytest.mark.asyncio
async def test_ingest_rejects_unsupported_file_type(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "knowledge.csv"
    file_path.write_text(
        "some,data",
        encoding="utf-8",
    )

    indexer = AsyncMock()

    service = DocumentIngestionService(
        chunker=TextChunker(),
        indexer=indexer,
    )

    with pytest.raises(
        ValueError,
        match="Unsupported document type: .csv",
    ):
        await service.ingest(
            file_path,
            document_id=uuid4(),
            uploaded_by=uuid4(),
        )

    indexer.index_chunks.assert_not_awaited()