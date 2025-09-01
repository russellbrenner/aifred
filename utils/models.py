from __future__ import annotations

from typing import Dict


# Best-effort defaults; adjust as providers update their limits.
MODEL_CAPS: Dict[str, Dict[str, int]] = {
    # OpenAI
    "openai:gpt-4o": {"context": 128_000, "max_output_tokens": 4_096},
    "openai:o4-mini": {"context": 128_000, "max_output_tokens": 4_096},
    "openai:o4": {"context": 128_000, "max_output_tokens": 4_096},
    # Anthropic
    "anthropic:claude-3-7-sonnet": {"context": 200_000, "max_output_tokens": 8_192},
    "anthropic:claude-3-sonnet-20240229": {"context": 200_000, "max_output_tokens": 8_192},
}


def get_caps(provider: str, model: str) -> Dict[str, int]:
    key = f"{provider}:{model}"
    if key in MODEL_CAPS:
        return MODEL_CAPS[key]
    # Fallbacks per provider
    if provider == "openai":
        return {"context": 128_000, "max_output_tokens": 4_096}
    if provider == "anthropic":
        return {"context": 200_000, "max_output_tokens": 8_192}
    return {"context": 32_000, "max_output_tokens": 2_048}

