from app.ingestion.models.document import DocumentChunk, ExtractedDocument


class TextChunker:
    """
    Split extracted document text into overlapping chunks.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        document: ExtractedDocument,
    ) -> list[DocumentChunk]:
        """
        Split a document into overlapping text chunks.
        """
        chunks: list[DocumentChunk] = []
        chunk_index = 0

        for page in document.pages:
            text = page.text

            if not text:
                continue

            start = 0

            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                chunk_text = text[start:end].strip()

                if chunk_text:
                    chunks.append(
                        DocumentChunk(
                            text=chunk_text,
                            chunk_index=chunk_index,
                            document_filename=document.filename,
                            page_number=page.page_number,
                        )
                    )

                    chunk_index += 1

                if end >= len(text):
                    break

                start = end - self.chunk_overlap

        return chunks
