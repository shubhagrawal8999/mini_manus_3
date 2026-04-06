# /app/agent/llm.py
import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class LLMRouter:
    async def plan(self, event, context):
        prompt = f"""
        You are an AI agent planner.
        Return JSON steps.

        Event: {event}
        Context: {context}
        """

        res = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        return res.choices[0].message.content["steps"]

    async def reflect(self, results):
        return
