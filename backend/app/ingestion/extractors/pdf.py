from pathlib import Path

from pypdf import PdfReader

from app.ingestion.models.document import DocumentPage, ExtractedDocument


def extract_pdf(path: Path) -> ExtractedDocument:
    """
    Extract text from a PDF document.
    """
    reader = PdfReader(path)

    pages: list[DocumentPage] = []

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append(
            DocumentPage(
                page_number=index,
                text=text.strip(),
            )
        )

    return ExtractedDocument(
        filename=path.name,
        content_type="application/pdf",
        pages=pages,
    )
