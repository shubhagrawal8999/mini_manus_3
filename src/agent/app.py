from __future__ import annotations

from agent.core.config import settings
from agent.core.models import Message, TaskContext, TaskType
from agent.core.orchestrator import Orchestrator
from agent.core.router import ModelRouter
from agent.learning.feedback import LearningEngine
from agent.memory.store import MemoryStore
from agent.providers.deepseek_provider import DeepSeekProvider
from agent.providers.openai_provider import OpenAIProvider


def build_orchestrator(db_path: str = "agent.db") -> Orchestrator:
    openai = OpenAIProvider(api_key=settings.openai_api_key)
    deepseek = DeepSeekProvider(api_key=settings.deepseek_api_key)
    router = ModelRouter(openai_provider=openai, deepseek_provider=deepseek, policy=settings.router_policy)
    memory = MemoryStore(db_path=db_path)
    learner = LearningEngine()
    return Orchestrator(router=router, memory=memory, learner=learner)


def run_demo() -> None:
    orchestrator = build_orchestrator()
    ctx = TaskContext(
        user_id="demo-user",
        task_type=TaskType.CHAT,
        prompt="Write a short welcome message.",
        messages=[Message(role="user", content="Write a short welcome message.")],
        metadata={"task_id": "demo-1"},
    )
    result = orchestrator.run(ctx)
    print(result.summary)


if __name__ == "__main__":
    run_demo()
