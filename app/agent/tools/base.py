# /app/agent/tools/base.py
class BaseTool:
    name = "base"

    async def execute(self, input_data: dict):
        raise NotImplementedError
