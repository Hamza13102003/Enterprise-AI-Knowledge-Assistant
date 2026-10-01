from app.ingestion.chunking.text_chunker import TextChunker
from app.ingestion.models.document import DocumentPage, ExtractedDocument


def test_chunk_document_creates_chunks() -> None:
    document = ExtractedDocument(
        filename="test.txt",
        content_type="text/plain",
        pages=[
            DocumentPage(
                page_number=1,
                text="A" * 2500,
            )
        ],
    )

    chunker = TextChunker(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = chunker.chunk_document(document)

    assert len(chunks) == 3
    assert chunks[0].chunk_index == 0
    assert chunks[0].page_number == 1
    assert chunks[0].document_filename == "test.txt"


def test_empty_pages_are_ignored() -> None:
    document = ExtractedDocument(
        filename="empty.txt",
        content_type="text/plain",
        pages=[
            DocumentPage(
                page_number=1,
                text="",
            )
        ],
    )

    chunker = TextChunker()

    chunks = chunker.chunk_document(document)

    assert chunks == []
