from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class TaskType(str, Enum):
    CHAT = "chat"
    CODING = "coding"
    RESEARCH = "research"
    POSTING = "posting"
    REPAIR = "repair"


@dataclass(slots=True)
class Message:
    role: str
    content: str


@dataclass(slots=True)
class TaskContext:
    user_id: str
    task_type: TaskType
    prompt: str
    messages: list[Message] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ModelResponse:
    provider: str
    model: str
    content: str
    success: bool = True
    error: str | None = None


@dataclass(slots=True)
class ExecutionResult:
    ok: bool
    summary: str
    details: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
