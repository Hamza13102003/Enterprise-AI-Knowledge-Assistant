from pathlib import Path
from uuid import UUID, uuid4

from app.ingestion.chunking.text_chunker import TextChunker
from app.ingestion.extractors.docx import extract_docx
from app.ingestion.extractors.pdf import extract_pdf
from app.ingestion.extractors.txt import extract_txt
from app.ingestion.indexing.service import DocumentIndexingService


class DocumentIngestionService:
    """
    Orchestrates document extraction, chunking, and vector indexing.
    """

    def __init__(
        self,
        chunker: TextChunker,
        indexer: DocumentIndexingService,
    ) -> None:
        self.chunker = chunker
        self.indexer = indexer

    async def ingest(
        self,
        file_path: Path,
        *,
        document_id: UUID,
        uploaded_by: UUID,
    ) -> int:
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            document = extract_pdf(file_path)
        elif suffix == ".docx":
            document = extract_docx(file_path)
        elif suffix == ".txt":
            document = extract_txt(file_path)
        else:
            raise ValueError(
                f"Unsupported document type: {suffix}",
            )

        chunks = self.chunker.chunk_document(document)

        if not chunks:
            return 0

        chunk_payloads = [
            {
                "id": uuid4(),
                "document_id": document_id,
                "uploaded_by": uploaded_by,
                "content": chunk.text,
            }
            for chunk in chunks
        ]

        await self.indexer.index_chunks(chunk_payloads)

        return len(chunks)