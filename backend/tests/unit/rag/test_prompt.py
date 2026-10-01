from app.rag.prompt import RAGPromptBuilder
from app.schemas.rag import RAGContext


def test_prompt_builder_includes_context_and_question() -> None:
    context = RAGContext(
        query="What is RAG?",
        chunks=[],
        context="RAG retrieves relevant information before generation.",
    )

    system_prompt, user_prompt = RAGPromptBuilder().build(context)

    assert "enterprise knowledge assistant" in system_prompt.lower()
    assert "RAG retrieves relevant information" in user_prompt
    assert "What is RAG?" in user_prompt
