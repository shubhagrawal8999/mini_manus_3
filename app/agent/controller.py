# /app/agent/controller.py
from agent.llm import LLMRouter
from agent.memory import MemoryManager
from agent.tools import ToolRegistry

class AgentController:
    def __init__(self):
        self.llm = LLMRouter()
        self.memory = MemoryManager()
        self.tools = ToolRegistry()

    async def process(self, event: dict):
        plan = await self.llm.plan(event, self.memory)

        results = []
        for step in plan:
            tool = self.tools.get(step["tool"])
            result = await tool.execute(step["input"])
            self.memory.store(result)
            results.append(result)

        return results
