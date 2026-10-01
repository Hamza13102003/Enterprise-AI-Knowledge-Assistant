from pathlib import Path

from app.ingestion.models.document import DocumentPage, ExtractedDocument


def extract_txt(path: Path) -> ExtractedDocument:
    """
    Extract text from a plain-text document.
    """
    text = path.read_text(encoding="utf-8")

    return ExtractedDocument(
        filename=path.name,
        content_type="text/plain",
        pages=[
            DocumentPage(
                page_number=1,
                text=text.strip(),
            )
        ],
    )
