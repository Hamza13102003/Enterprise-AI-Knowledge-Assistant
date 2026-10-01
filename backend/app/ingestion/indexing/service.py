from uuid import UUID

from qdrant_client.models import PointStruct

from app.embeddings.ollama import OllamaEmbeddingService
from app.vector_store.qdrant import QdrantService


class DocumentIndexingService:
    """
    Convert document chunks into embeddings and store them in Qdrant.
    """

    def __init__(
        self,
        embedding_service: OllamaEmbeddingService,
        vector_store: QdrantService,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    async def index_chunks(
        self,
        chunks: list[dict[str, object]],
    ) -> None:
        """
        Generate embeddings for chunks and store them in Qdrant.
        """
        if not chunks:
            return

        texts = [str(chunk["content"]) for chunk in chunks]

        embeddings = await self.embedding_service.embed_many(texts)

        points: list[PointStruct] = []

        for chunk, embedding in zip(chunks, embeddings, strict=True):
            chunk_id = UUID(str(chunk["id"]))

            payload = {
                "document_id": str(chunk["document_id"]),
                "uploaded_by": str(chunk["uploaded_by"]),
                "chunk_id": str(chunk["id"]),
                "content": str(chunk["content"]),
            }

            points.append(
                PointStruct(
                    id=str(chunk_id),
                    vector=embedding,
                    payload=payload,
                )
            )

        await self.vector_store.upsert_many(points)