import httpx
import pytest
from pytest import MonkeyPatch

from app.llm.ollama import OllamaGenerationService


@pytest.mark.asyncio
async def test_generate_returns_ollama_response(
    monkeypatch: MonkeyPatch,
) -> None:
    service = OllamaGenerationService(
        host="http://localhost:11434",
        model="qwen2.5:3b",
    )

    class MockResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, str]:
            return {"response": "This is the generated answer."}

    async def mock_post(
        self: httpx.AsyncClient,
        url: str,
        **kwargs: object,
    ) -> MockResponse:
        assert url == "http://localhost:11434/api/generate"
        return MockResponse()

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    result = await service.generate("What is RAG?")

    assert result == "This is the generated answer."


@pytest.mark.asyncio
async def test_empty_prompt_returns_empty_string() -> None:
    service = OllamaGenerationService()

    result = await service.generate("   ")

    assert result == ""
