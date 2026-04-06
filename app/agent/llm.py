# /app/agent/llm.py
import openai

class LLMRouter:
    async def plan(self, event, memory):
        # enforce structured output
        return [
            {"tool": "email_reader", "input": event}
        ]
