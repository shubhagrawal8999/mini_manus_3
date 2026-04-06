# /app/agent/tools/email.py
from agent.tools.base import BaseTool

class EmailReader(BaseTool):
    name = "email_reader"

    async def execute(self, input_data):
        return {"emails": ["example email"], "priority": "high"}
