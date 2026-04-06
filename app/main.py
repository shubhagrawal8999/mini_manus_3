# /app/main.py
from fastapi import FastAPI
from agent.controller import AgentController

app = FastAPI()
agent = AgentController()

@app.post("/event")
async def handle_event(event: dict):
    return await agent.process(event)
