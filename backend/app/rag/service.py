import logging
import time
from uuid import UUID

from app.core.settings import settings
from app.llm.ollama import OllamaLLMService
from app.rag.context import RAGContextBuilder
from app.rag.prompt import RAGPromptBuilder
from app.rag.retriever import RAGRetriever
from app.schemas.rag import RAGResponse

logger = logging.getLogger(__name__)


class RAGService:
    """
    Orchestrates retrieval-augmented generation.
    """

    FALLBACK_ANSWER = (
        "The information is not available in the provided documents."
    )

    def __init__(
        self,
        retriever: RAGRetriever,
        context_builder: RAGContextBuilder,
        prompt_builder: RAGPromptBuilder,
        llm_service: OllamaLLMService,
    ) -> None:
        self.retriever = retriever
        self.context_builder = context_builder
        self.prompt_builder = prompt_builder
        self.llm_service = llm_service

    async def answer(
        self,
        query: str,
        *,
        user_id: UUID,
        top_k: int = 5,
    ) -> RAGResponse:
        """
        Retrieve relevant context and generate an evidence-grounded answer.
        """

        total_start = time.perf_counter()

        # ---------------------------------------------------------
        # 0. Query validation
        # ---------------------------------------------------------
        if not query.strip():
            logger.warning(
                "RAG query rejected | reason=empty_query | user_id=%s",
                user_id,
            )

            return RAGResponse(
                answer=self.FALLBACK_ANSWER,
                sources=[],
            )

        # ---------------------------------------------------------
        # 1. Retrieval
        # ---------------------------------------------------------
        retrieval_start = time.perf_counter()

        chunks = await self.retriever.retrieve(
            query,
            user_id=user_id,
            top_k=top_k,
        )

        retrieval_time = time.perf_counter() - retrieval_start

        # ---------------------------------------------------------
        # 2. Retrieval confidence
        # ---------------------------------------------------------
        confidence = self.retriever.calculate_retrieval_confidence(
            chunks
        )

        logger.info(
            "RAG retrieval completed | "
            "user_id=%s chunks=%d confidence=%.3f "
            "threshold=%.3f retrieval_time=%.3fs",
            user_id,
            len(chunks),
            confidence,
            settings.rag_retrieval_threshold,
            retrieval_time,
        )

        if confidence < settings.rag_retrieval_threshold:
            total_time = time.perf_counter() - total_start

            logger.warning(
                "RAG fallback | "
                "reason=low_retrieval_confidence "
                "user_id=%s chunks=%d confidence=%.3f "
                "threshold=%.3f total_time=%.3fs",
                user_id,
                len(chunks),
                confidence,
                settings.rag_retrieval_threshold,
                total_time,
            )

            return RAGResponse(
                answer=self.FALLBACK_ANSWER,
                sources=chunks,
            )

        # ---------------------------------------------------------
        # 3. Context construction
        # ---------------------------------------------------------
        context_start = time.perf_counter()

        context = self.context_builder.build(
            query,
            chunks,
        )

        context_time = time.perf_counter() - context_start

        # ---------------------------------------------------------
        # 4. Prompt construction
        # ---------------------------------------------------------
        prompt_start = time.perf_counter()

        system_prompt, user_prompt = self.prompt_builder.build(
            context,
        )

        prompt_time = time.perf_counter() - prompt_start

        # ---------------------------------------------------------
        # 5. LLM generation
        # ---------------------------------------------------------
        llm_start = time.perf_counter()

        try:
            answer = await self.llm_service.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        except Exception:
            llm_time = time.perf_counter() - llm_start

            logger.exception(
                "RAG LLM generation failed | "
                "user_id=%s llm_time=%.3fs",
                user_id,
                llm_time,
            )

            raise

        llm_time = time.perf_counter() - llm_start

        # ---------------------------------------------------------
        # 6. Answer cleanup
        # ---------------------------------------------------------
        cleanup_start = time.perf_counter()

        answer = self._clean_answer(answer)

        cleanup_time = time.perf_counter() - cleanup_start

        if not answer:
            total_time = time.perf_counter() - total_start

            logger.warning(
                "RAG fallback | "
                "reason=empty_llm_response "
                "user_id=%s llm_time=%.3fs total_time=%.3fs",
                user_id,
                llm_time,
                total_time,
            )

            answer = self.FALLBACK_ANSWER

        # ---------------------------------------------------------
        # 7. Total latency
        # ---------------------------------------------------------
        total_time = time.perf_counter() - total_start

        logger.info(
            "RAG query completed | "
            "user_id=%s chunks=%d confidence=%.3f "
            "retrieval_time=%.3fs context_time=%.3fs "
            "prompt_time=%.3fs llm_time=%.3fs "
            "cleanup_time=%.3fs total_time=%.3fs",
            user_id,
            len(chunks),
            confidence,
            retrieval_time,
            context_time,
            prompt_time,
            llm_time,
            cleanup_time,
            total_time,
        )

        return RAGResponse(
            answer=answer,
            sources=chunks,
        )

    @staticmethod
    def _clean_answer(answer: str) -> str:
        """
        Clean common formatting artifacts from the LLM response.

        This does not change the semantic content of the answer.
        """

        cleaned = answer.strip()

        if not cleaned:
            return ""

        prefixes = (
            "Final Answer:",
            "Answer:",
            "Final answer:",
        )

        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()

        unwanted_prefixes = (
            "Retrieved Evidence:",
            "Retrieved Context:",
            "Context:",
        )

        for prefix in unwanted_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()

        return cleaned