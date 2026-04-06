# /app/agent/tools/registry.py
from agent.tools.email import EmailReader
from agent.tools.linkedin import LinkedInPoster
from agent.tools.research import ResearchTool

class ToolRegistry:
    def __init__(self):
        self.tools = {
            "email_reader": EmailReader(),
            "linkedin_post": LinkedInPoster(),
            "research": ResearchTool(),
        }

    def get(self, name):
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        return self.tools[name]
