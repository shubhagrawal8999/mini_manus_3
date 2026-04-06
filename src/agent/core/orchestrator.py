from __future__ import annotations

from agent.core.models import ExecutionResult, Message, TaskContext, TaskType
from agent.core.router import ModelRouter
from agent.learning.feedback import ErrorType, FailureEvent, LearningEngine
from agent.memory.store import MemoryStore
from agent.tools.posting import LinkedInPoster, TelegramPoster


class Orchestrator:
    def __init__(self, router: ModelRouter, memory: MemoryStore, learner: LearningEngine) -> None:
        self.router = router
        self.memory = memory
        self.learner = learner

    def _augment_messages_with_memory(self, ctx: TaskContext) -> list[Message]:
        retrieved = self.memory.retrieve(ctx.user_id, ctx.prompt, top_k=3)
        memory_notes = "\n".join(f"- {m.text}" for m in retrieved)
        system_prefix = "Known user preferences:\n" + (memory_notes or "- none")
        return [Message(role="system", content=system_prefix), *ctx.messages]

    def run(self, ctx: TaskContext) -> ExecutionResult:
        try:
            enriched = TaskContext(
                user_id=ctx.user_id,
                task_type=ctx.task_type,
                prompt=ctx.prompt,
                messages=self._augment_messages_with_memory(ctx),
                tools=ctx.tools,
                metadata=ctx.metadata,
            )
            model_result = self.router.run(enriched)
            if not model_result.success:
                raise RuntimeError(model_result.error or "Unknown provider failure")

            if ctx.task_type == TaskType.POSTING:
                target = ctx.metadata.get("target", "telegram")
                url = self._post(target=target, content=model_result.content)
                self.memory.add(ctx.user_id, "episodic", f"Posted to {target}: {url}", salience=0.8)
                return ExecutionResult(ok=True, summary=f"Posted successfully to {target}", details={"url": url})

            self.memory.add(ctx.user_id, "episodic", model_result.content[:240], salience=0.6)
            return ExecutionResult(ok=True, summary=model_result.content, details={"provider": model_result.provider})
        except Exception as exc:  # noqa: BLE001
            event = FailureEvent(
                task_id=str(ctx.metadata.get("task_id", "unknown")),
                error_type=ErrorType.EXECUTION,
                error_message=str(exc),
                attempt=int(ctx.metadata.get("attempt", 1)),
            )
            self.learner.record_failure(event)
            fix = self.learner.suggest_fix(event)
            self.memory.add(ctx.user_id, "procedural", f"Failure: {event.error_message}; Fix: {fix}", salience=0.9)
            return ExecutionResult(ok=False, summary="Task failed", details={"error": str(exc), "suggested_fix": fix})

    def _post(self, target: str, content: str) -> str:
        if target == "linkedin":
            return LinkedInPoster(organization="default-org").post(content)
        return TelegramPoster(channel="default-channel").post(content)
