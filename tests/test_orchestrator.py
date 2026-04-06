from __future__ import annotations

from agent.core.models import Message, TaskContext, TaskType
from agent.core.orchestrator import Orchestrator
from agent.core.router import ModelRouter
from agent.learning.feedback import LearningEngine
from agent.memory.store import MemoryStore
from agent.providers.deepseek_provider import DeepSeekProvider
from agent.providers.openai_provider import OpenAIProvider


def test_posting_workflow(tmp_path):
    memory = MemoryStore(str(tmp_path / "agent.db"))
    router = ModelRouter(OpenAIProvider(api_key="k1"), DeepSeekProvider(api_key="k2"))
    learner = LearningEngine()
    orchestrator = Orchestrator(router=router, memory=memory, learner=learner)

    ctx = TaskContext(
        user_id="u-post",
        task_type=TaskType.POSTING,
        prompt="Write and post announcement",
        messages=[Message(role="user", content="Announce launch tomorrow")],
        metadata={"target": "telegram", "task_id": "t-1"},
    )

    result = orchestrator.run(ctx)
    assert result.ok is True
    assert "Posted successfully" in result.summary
    assert result.details["url"].startswith("telegram://")


def test_failure_learns_fix(tmp_path):
    memory = MemoryStore(str(tmp_path / "agent.db"))
    router = ModelRouter(OpenAIProvider(api_key=""), DeepSeekProvider(api_key=""))
    learner = LearningEngine()
    orchestrator = Orchestrator(router=router, memory=memory, learner=learner)

    ctx = TaskContext(
        user_id="u-fail",
        task_type=TaskType.CODING,
        prompt="Generate script",
        messages=[Message(role="user", content="Generate script")],
        metadata={"task_id": "t-2", "attempt": 1},
    )

    result = orchestrator.run(ctx)
    assert result.ok is False
    assert learner.failures
    assert "suggested_fix" in result.details
