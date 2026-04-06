from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Poster(Protocol):
    def post(self, content: str) -> str:
        ...


@dataclass(slots=True)
class TelegramPoster:
    channel: str

    def post(self, content: str) -> str:
        return f"telegram://{self.channel}/message/{abs(hash(content)) % 100000}"


@dataclass(slots=True)
class LinkedInPoster:
    organization: str

    def post(self, content: str) -> str:
        return f"linkedin://{self.organization}/post/{abs(hash(content)) % 100000}"
