from __future__ import annotations

from agent.core.models import Message, ModelResponse
from agent.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4.1-mini") -> None:
        self.name = "openai"
        self.model = model
        self.api_key = api_key

    def generate(self, messages: list[Message], *, temperature: float = 0.2) -> ModelResponse:
        if not self.api_key:
            return ModelResponse(
                provider=self.name,
                model=self.model,
                success=False,
                content="",
                error="OPENAI_API_KEY is missing",
            )

        # Placeholder implementation for local/test environments.
        user_text = "\n".join(m.content for m in messages if m.role == "user")
        return ModelResponse(
            provider=self.name,
            model=self.model,
            content=f"[OpenAI simulated] {user_text.strip()[:400]}",
        )
