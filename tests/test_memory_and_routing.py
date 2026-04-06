from __future__ import annotations

from agent.core.models import Message, TaskContext, TaskType
from agent.core.router import ModelRouter
from agent.memory.store import MemoryStore
from agent.providers.deepseek_provider import DeepSeekProvider
from agent.providers.openai_provider import OpenAIProvider


class TestMemoryStore:
    def test_add_and_retrieve(self, tmp_path):
        db = tmp_path / "mem.db"
        store = MemoryStore(str(db))
        store.add("u1", "preference", "User prefers short concise posts", salience=0.9)
        store.add("u1", "episodic", "Yesterday post succeeded on Telegram", salience=0.5)

        found = store.retrieve("u1", "concise post", top_k=1)
        assert found
        assert "short" in found[0].text.lower()


class TestModelRouter:
    def test_fallback_when_primary_key_missing(self):
        openai = OpenAIProvider(api_key="")
        deepseek = DeepSeekProvider(api_key="valid")
        router = ModelRouter(openai_provider=openai, deepseek_provider=deepseek)

        ctx = TaskContext(
            user_id="u1",
            task_type=TaskType.CODING,
            prompt="generate code",
            messages=[Message(role="user", content="generate code")],
        )
        response = router.run(ctx)
        assert response.success is True
        assert response.provider == "deepseek"
