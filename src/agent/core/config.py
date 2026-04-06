from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    model_primary: str = os.getenv("MODEL_PRIMARY", "openai:gpt-4.1-mini")
    model_fallback: str = os.getenv("MODEL_FALLBACK", "deepseek:deepseek-chat")
    router_policy: str = os.getenv("ROUTER_POLICY", "quality_first")


settings = Settings()
