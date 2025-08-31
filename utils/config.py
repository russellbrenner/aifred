from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Defaults:
    provider: str
    model_openai: str
    model_anthropic: str
    max_input_tokens: int
    profile: str


def get_defaults() -> Defaults:
    provider = os.getenv("AIFRED_PROVIDER_DEFAULT", "openai").lower()
    model_openai = os.getenv("AIFRED_MODEL_DEFAULT_OPENAI", "gpt-4o")
    model_anthropic = os.getenv("AIFRED_MODEL_DEFAULT_ANTHROPIC", "claude-3-7-sonnet")
    # Rough input token cap for history (independent of output max)
    max_input_tokens = int(os.getenv("AIFRED_MAX_INPUT_TOKENS", "4000"))
    profile = os.getenv("AIFRED_PROFILE", "default")
    return Defaults(provider, model_openai, model_anthropic, max_input_tokens, profile)


def get_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip() in {"1", "true", "TRUE", "yes", "on"}
