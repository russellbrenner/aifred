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
    legal_mode: bool
    legal_tools: list[str]


def get_defaults() -> Defaults:
    provider = os.getenv("AIFRED_PROVIDER_DEFAULT", "openai").lower()
    model_openai = os.getenv("AIFRED_MODEL_DEFAULT_OPENAI", "gpt-4o")
    model_anthropic = os.getenv("AIFRED_MODEL_DEFAULT_ANTHROPIC", "claude-3-7-sonnet")
    # Rough input token cap for history (independent of output max)
    max_input_tokens = int(os.getenv("AIFRED_MAX_INPUT_TOKENS", "4000"))
    profile = os.getenv("AIFRED_PROFILE", "default")
    # Overlay with user config if present
    try:
        from utils.user_config import get_option
        profile = get_option("profile", profile)
        max_input_tokens = int(get_option("max_input_tokens", max_input_tokens))
        legal_mode = bool(get_option("legal_mode", os.getenv("AIFRED_LEGAL_MODE") == "1"))
    except Exception:
        legal_mode = os.getenv("AIFRED_LEGAL_MODE") == "1"
    legal_tools = ["browse", "fetch_url", "citation_extract", "case_search"]
    return Defaults(provider, model_openai, model_anthropic, max_input_tokens, profile, legal_mode, legal_tools)


def get_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip() in {"1", "true", "TRUE", "yes", "on"}
