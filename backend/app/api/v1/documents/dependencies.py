from app.embeddings.ollama import OllamaEmbeddingService
from app.ingestion.chunking.text_chunker import TextChunker
from app.ingestion.indexing.service import DocumentIndexingService
from app.ingestion.service import DocumentIngestionService
from app.vector_store.qdrant import QdrantService


def get_document_ingestion_service() -> DocumentIngestionService:
    """Build the document ingestion service."""
    embedding_service = OllamaEmbeddingService()
    vector_store = QdrantService()

    indexer = DocumentIndexingService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    return DocumentIngestionService(
        chunker=TextChunker(),
        indexer=indexer,
    )
