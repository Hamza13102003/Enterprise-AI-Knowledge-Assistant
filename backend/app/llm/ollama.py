from typing import Any

import httpx

from app.core.settings import settings


class OllamaLLMService:
    """
    Service responsible for generating answers using a local Ollama model.
    """

    def __init__(
        self,
        host: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.host = (host or settings.ollama_host).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout

    async def generate(
        self,
        prompt: str | None = None,
        *,
        system_prompt: str | None = None,
        user_prompt: str | None = None,
    ) -> str:
        """
        Generate a response from the configured Ollama model.

        Supports both a simple prompt and separate system/user prompts.
        """

        if prompt is not None:
            final_prompt = prompt.strip()

        else:
            system = (system_prompt or "").strip()
            user = (user_prompt or "").strip()

            if not user:
                return ""

            final_prompt = (
                f"{system}\n\n{user}"
                if system
                else user
            )

        if not final_prompt:
            return ""

        url = f"{self.host}/api/generate"

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": final_prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": 150,

            },
        }

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:

            response = await client.post(
                url,
                json=payload,
            )

            response.raise_for_status()

        data: dict[str, Any] = response.json()

        response_text = data.get("response")

        if not isinstance(response_text, str):
            raise ValueError(
                "Ollama returned an invalid response."
            )

        return response_text.strip()


# Backward-compatible name used by existing tests
# and older code.
OllamaGenerationService = OllamaLLMService