from __future__ import annotations

from abc import ABC, abstractmethod

from agent.core.models import Message, ModelResponse


class LLMProvider(ABC):
    name: str
    model: str

    @abstractmethod
    def generate(self, messages: list[Message], *, temperature: float = 0.2) -> ModelResponse:
        """Generate a model response from a chat transcript."""
