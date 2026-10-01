from dataclasses import dataclass, field


@dataclass(slots=True)
class DocumentPage:
    """
    Represents extracted text from a single document page.
    """

    page_number: int
    text: str


@dataclass(slots=True)
class ExtractedDocument:
    """
    Represents a fully extracted document.
    """

    filename: str
    content_type: str
    pages: list[DocumentPage] = field(default_factory=list)


@dataclass(slots=True)
class DocumentChunk:
    """
    Represents a chunk of text ready for embedding and retrieval.
    """

    text: str
    chunk_index: int
    document_filename: str
    page_number: int | None = None
