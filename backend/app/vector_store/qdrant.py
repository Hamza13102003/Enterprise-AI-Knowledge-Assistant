from typing import Any
from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PointStruct,
    ScoredPoint,
    VectorParams,
)

from app.core.settings import settings


class QdrantService:
    """
    Service responsible for storing and searching document embeddings.
    """

    COLLECTION_NAME = "enterprise_documents"

    def __init__(self) -> None:
        self.client = AsyncQdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )

    async def ensure_collection(self) -> None:
        """
        Create the document collection if it does not already exist.
        """
        collections = await self.client.get_collections()

        collection_names = {
            collection.name
            for collection in collections.collections
        }

        if self.COLLECTION_NAME not in collection_names:
            await self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension,
                    distance=Distance.COSINE,
                ),
            )

    async def upsert(
        self,
        point_id: UUID,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """
        Insert or update a single vector point.
        """
        await self.ensure_collection()

        point = PointStruct(
            id=str(point_id),
            vector=vector,
            payload=payload,
        )

        await self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[point],
        )

    async def upsert_many(
        self,
        points: list[PointStruct],
    ) -> None:
        """
        Insert or update multiple vector points.
        """
        if not points:
            return

        await self.ensure_collection()

        await self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
        )

    async def search(
        self,
        vector: list[float],
        *,
        user_id: UUID,
        limit: int = 5,
        score_threshold: float = 0.50,
    ) -> list[ScoredPoint]:
        """
        Search for the most similar document chunks belonging
        to the specified user.
        """
        await self.ensure_collection()

        user_filter = Filter(
            must=[
                FieldCondition(
                    key="uploaded_by",
                    match=MatchValue(
                        value=str(user_id),
                    ),
                ),
            ],
        )

        results = await self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=vector,
            query_filter=user_filter,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
        )

        return results.points

    async def delete_by_document_id(
        self,
        document_id: UUID,
    ) -> None:
        """
        Delete all vector chunks belonging to a document.
        """
        await self.ensure_collection()

        document_filter = Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(
                        value=str(document_id),
                    ),
                ),
            ],
        )

        await self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=FilterSelector(
                filter=document_filter,
            ),
        )

    async def close(self) -> None:
        """
        Close the Qdrant client.
        """
        await self.client.close()