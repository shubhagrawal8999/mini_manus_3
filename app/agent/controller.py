# /app/agent/controller.py
from agent.llm import LLMRouter
from agent.memory import MemoryManager
from agent.tools.registry import ToolRegistry

class AgentController:
    def __init__(self):
        self.llm = LLMRouter()
        self.memory = MemoryManager()
        self.tools = ToolRegistry()

    async def process(self, event: dict):
        plan = await self.llm.plan(event, self.memory.get_context())

        results = []
        for step in plan:
            tool = self.tools.get(step["tool"])
            result = await tool.execute(step["input"])

            self.memory.store(step, result)
            results.append(result)

        await self.llm.reflect(results)

        return {"status": "ok", "results": results}
