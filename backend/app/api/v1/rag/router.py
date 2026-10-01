from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.database.models.user import User
from app.embeddings.ollama import OllamaEmbeddingService
from app.llm.ollama import OllamaLLMService
from app.rag.context import RAGContextBuilder
from app.rag.prompt import RAGPromptBuilder
from app.rag.retriever import RAGRetriever
from app.rag.service import RAGService
from app.schemas.api_response import APIResponse
from app.schemas.rag import RAGQueryRequest
from app.utils.response import success_response
from app.vector_store.qdrant import QdrantService

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


def create_rag_service() -> RAGService:
    """
    Create the RAG service with its required dependencies.
    """
    embedding_service = OllamaEmbeddingService()
    vector_store = QdrantService()

    retriever = RAGRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    context_builder = RAGContextBuilder()
    prompt_builder = RAGPromptBuilder()
    llm_service = OllamaLLMService()

    return RAGService(
        retriever=retriever,
        context_builder=context_builder,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )


@router.post(
    "/query",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
async def query_rag(
    payload: RAGQueryRequest,
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    """
    Query the authenticated user's knowledge base using RAG.
    """
    service = create_rag_service()

    try:
        result = await service.answer(
            payload.query,
            user_id=current_user.id,
            top_k=payload.top_k,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RAG query failed.",
        ) from exc

    return success_response(
        message="RAG query completed successfully.",
        data=result,
    )