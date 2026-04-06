# /app/agent/tools/linkedin.py
from agent.tools.base import BaseTool

class LinkedInPoster(BaseTool):
    name = "linkedin_post"

    async def execute(self, input_data):
        return {"status": "posted", "content": input_data}
