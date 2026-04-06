# /app/agent/tools/research.py
from agent.tools.base import BaseTool

class ResearchTool(BaseTool):
    name = "research"

    async def execute(self, input_data):
        return {"summary": "research result"}
