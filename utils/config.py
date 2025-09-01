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
    tool_exec: bool
    stream: bool
    persona_name: str | None
    persona_prompt: str | None


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

    # Execution and streaming toggles
    try:
        from utils.user_config import get_option
        tool_exec = bool(get_option("tool_exec", os.getenv("AIFRED_TOOL_EXEC") == "1"))
        stream = bool(get_option("stream", os.getenv("AIFRED_STREAM") == "1"))
        persona_name = get_option("active_persona", None)
        persona_prompt = None
        if persona_name:
            personas = get_option("personas", {}) or {}
            if persona_name in personas:
                persona_prompt = personas[persona_name].get("prompt")
        # If persona_name indicates legal, ensure legal_mode defaults true
        if persona_name == "legal":
            legal_mode = True
            if not persona_prompt:
                persona_prompt = DEFAULT_LEGAL_PROMPT
    except Exception:
        tool_exec = os.getenv("AIFRED_TOOL_EXEC") == "1"
        stream = os.getenv("AIFRED_STREAM") == "1"
        persona_name = None
        persona_prompt = None

    return Defaults(
        provider,
        model_openai,
        model_anthropic,
        max_input_tokens,
        profile,
        legal_mode,
        legal_tools,
        tool_exec,
        stream,
        persona_name,
        persona_prompt,
    )


def get_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip() in {"1", "true", "TRUE", "yes", "on"}


# Default persona prompts
DEFAULT_LEGAL_PROMPT = (
    "You are a legal researcher. You respond at a Victorian bar level. "
    "You speak Australian English (syntax, grammar, spelling) and use metric units. "
    "Provide citations when appropriate."
)
