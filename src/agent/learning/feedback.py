from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ErrorType(str, Enum):
    PLANNING = "planning"
    TOOL = "tool"
    EXECUTION = "execution"
    MEMORY = "memory"
    SAFETY = "safety"


@dataclass(slots=True)
class FailureEvent:
    task_id: str
    error_type: ErrorType
    error_message: str
    attempt: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class LearningEngine:
    failures: list[FailureEvent] = field(default_factory=list)
    playbook: dict[str, str] = field(default_factory=dict)

    def record_failure(self, event: FailureEvent) -> None:
        self.failures.append(event)

    def suggest_fix(self, event: FailureEvent) -> str:
        known = self.playbook.get(event.error_message)
        if known:
            return known

        if "429" in event.error_message:
            return "Apply exponential backoff and retry with jitter"
        if "missing" in event.error_message.lower():
            return "Validate required credentials and schema before execution"
        return "Escalate to human review and capture detailed RCA"

    def learn_fix(self, error_message: str, fix: str) -> None:
        self.playbook[error_message] = fix
