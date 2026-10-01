from app.schemas.rag import RAGContext, RetrievedChunk


class RAGContextBuilder:
    """
    Build a structured, evidence-focused context from retrieved chunks.
    """

    def build(
        self,
        query: str,
        chunks: list[RetrievedChunk],
    ) -> RAGContext:
        """
        Assemble retrieved chunks into an LLM-ready evidence context.

        Chunks are ordered by descending retrieval score.
        """

        if not chunks:
            return RAGContext(
                query=query,
                chunks=[],
                context="No relevant documents were found.",
            )

        sorted_chunks = sorted(
            chunks,
            key=lambda chunk: chunk.score,
            reverse=True,
        )

        context_parts: list[str] = []

        for index, chunk in enumerate(sorted_chunks, start=1):
            context_parts.append(
                f"[Source {index}]\n"
                f"Document ID: {chunk.document_id}\n"
                f"Chunk ID: {chunk.chunk_id}\n"
                f"Retrieval Score: {chunk.score:.4f}\n"
                f"Evidence:\n"
                f"{chunk.content.strip()}"
            )

        return RAGContext(
            query=query,
            chunks=sorted_chunks,
            context="\n\n".join(context_parts),
        )