from __future__ import annotations

from agent.core.models import ModelResponse, TaskContext, TaskType
from agent.providers.base import LLMProvider


class ModelRouter:
    def __init__(self, openai_provider: LLMProvider, deepseek_provider: LLMProvider, policy: str = "quality_first") -> None:
        self.openai_provider = openai_provider
        self.deepseek_provider = deepseek_provider
        self.policy = policy

    def select_provider(self, ctx: TaskContext) -> LLMProvider:
        if self.policy == "cost_first":
            return self.deepseek_provider
        if ctx.task_type in {TaskType.CODING, TaskType.REPAIR, TaskType.POSTING}:
            return self.openai_provider
        return self.deepseek_provider

    def run(self, ctx: TaskContext) -> ModelResponse:
        primary = self.select_provider(ctx)
        fallback = self.deepseek_provider if primary is self.openai_provider else self.openai_provider

        response = primary.generate(ctx.messages)
        if response.success:
            return response
        return fallback.generate(ctx.messages)
