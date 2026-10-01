from typing import Any, cast

import httpx

from app.core.settings import settings


class OllamaEmbeddingService:
    """
    Generate text embeddings using a local Ollama embedding model.
    """

    def __init__(self) -> None:
        self.host = settings.ollama_host.rstrip("/")
        self.model = settings.embedding_model

    async def embed(self, text: str) -> list[float]:
        """
        Generate an embedding for a single piece of text.
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "input": text,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.host}/api/embed",
                json=payload,
            )

        response.raise_for_status()

        data = cast(dict[str, Any], response.json())
        embeddings = data.get("embeddings")

        if not isinstance(embeddings, list) or not embeddings:
            raise ValueError("Ollama returned no embeddings.")

        embedding = embeddings[0]

        if not isinstance(embedding, list):
            raise ValueError("Ollama returned an invalid embedding.")

        return [float(value) for value in embedding]

    async def embed_many(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """
        if not texts:
            return []

        payload: dict[str, Any] = {
            "model": self.model,
            "input": texts,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.host}/api/embed",
                json=payload,
            )

        response.raise_for_status()

        data = cast(dict[str, Any], response.json())
        embeddings = data.get("embeddings")

        if not isinstance(embeddings, list) or not embeddings:
            raise ValueError("Ollama returned no embeddings.")

        result: list[list[float]] = []

        for embedding in embeddings:
            if not isinstance(embedding, list):
                raise ValueError("Ollama returned an invalid embedding.")

            result.append([float(value) for value in embedding])

        return result
