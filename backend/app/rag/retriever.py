from uuid import UUID

from qdrant_client.models import ScoredPoint

from app.core.settings import settings
from app.embeddings.ollama import OllamaEmbeddingService
from app.schemas.rag import RetrievedChunk
from app.vector_store.qdrant import QdrantService


class RAGRetriever:
    """
    Retrieve and prepare relevant document chunks for a user query.

    Responsibilities:
    - Embed the user query.
    - Search Qdrant for the authenticated user's documents.
    - Filter low-confidence results.
    - Validate payloads.
    - Sort results by relevance.
    - Remove duplicate chunks.
    """

    def __init__(
        self,
        embedding_service: OllamaEmbeddingService,
        vector_store: QdrantService,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    async def retrieve(
        self,
        query: str,
        *,
        user_id: UUID,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """
        Retrieve relevant document chunks belonging
        to the authenticated user.
        """

        if not query or not query.strip():
            return []

        query_embedding = await self.embedding_service.embed(query)

        results = await self.vector_store.search(
            query_embedding,
            user_id=user_id,
            limit=top_k,
        )

        relevant_results = [
            result
            for result in results
            if result.score >= settings.rag_relevance_threshold
            and self._has_valid_payload(result)
        ]

        # Highest-scoring evidence first.
        relevant_results.sort(
            key=lambda result: float(result.score),
            reverse=True,
        )

        chunks: list[RetrievedChunk] = []
        seen_chunk_ids: set[str] = set()

        for result in relevant_results:
            payload = result.payload or {}

            chunk_id = str(payload["chunk_id"])

            # Avoid duplicate chunks.
            if chunk_id in seen_chunk_ids:
                continue

            seen_chunk_ids.add(chunk_id)

            chunks.append(
                self._convert_result(result)
            )

        return chunks

    @staticmethod
    def _has_valid_payload(
        result: ScoredPoint,
    ) -> bool:
        """
        Check whether a Qdrant result contains
        all required payload fields.
        """

        payload = result.payload or {}

        required_keys = (
            "chunk_id",
            "document_id",
            "uploaded_by",
            "content",
        )

        return all(
            key in payload
            and payload[key] is not None
            and str(payload[key]).strip()
            for key in required_keys
        )

    @staticmethod
    def _convert_result(
        result: ScoredPoint,
    ) -> RetrievedChunk:
        """
        Convert a Qdrant result into the
        application-level RetrievedChunk schema.
        """

        payload = result.payload or {}

        return RetrievedChunk(
            chunk_id=str(payload["chunk_id"]),
            document_id=str(payload["document_id"]),
            content=str(payload["content"]).strip(),
            score=float(result.score),
        )

    @staticmethod
    def calculate_retrieval_confidence(
        chunks: list[RetrievedChunk],
    ) -> float:
        """
        Calculate retrieval confidence.

        The highest similarity score represents the strongest
        evidence available for the query.
        """

        if not chunks:
            return 0.0

        return max(
            chunk.score
            for chunk in chunks
        )