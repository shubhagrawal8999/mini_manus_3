# /app/worker.py
from celery import Celery
import os

celery = Celery(
    "agent",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL")
)
