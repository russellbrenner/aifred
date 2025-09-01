from __future__ import annotations

from typing import Dict


# Best-effort defaults; adjust as providers update their limits.
MODEL_CAPS: Dict[str, Dict[str, int]] = {
    # OpenAI
    "openai:gpt-4o": {"context": 128_000, "max_output_tokens": 4_096},
    "openai:gpt-4o-mini": {"context": 128_000, "max_output_tokens": 4_096},
    "openai:gpt-4-turbo": {"context": 128_000, "max_output_tokens": 4_096},
    "openai:o4-mini": {"context": 128_000, "max_output_tokens": 4_096},
    "openai:o4": {"context": 128_000, "max_output_tokens": 4_096},
    "openai:o3-mini": {"context": 128_000, "max_output_tokens": 4_096},
    # Anthropic
    "anthropic:claude-3-7-sonnet": {"context": 200_000, "max_output_tokens": 8_192},
    "anthropic:claude-3-5-sonnet-20241022": {"context": 200_000, "max_output_tokens": 8_192},
    "anthropic:claude-3-5-haiku-20241022": {"context": 200_000, "max_output_tokens": 4_096},
    "anthropic:claude-3-opus-20240229": {"context": 200_000, "max_output_tokens": 8_192},
    "anthropic:claude-3-sonnet-20240229": {"context": 200_000, "max_output_tokens": 8_192},
    "anthropic:claude-3-haiku-20240307": {"context": 200_000, "max_output_tokens": 4_096},
}


def get_caps(provider: str, model: str) -> Dict[str, int]:
    key = f"{provider}:{model}"
    # Allow user overrides via config or JSON file
    try:
        from utils.user_config import get_option
        overrides = get_option("model_caps", {}) or {}
        if key in overrides:
            return overrides[key]
    except Exception:
        pass
    try:
        import os, json
        path = os.getenv("AIFRED_MODEL_CAPS_PATH")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if key in data:
                    return data[key]
    except Exception:
        pass
    if key in MODEL_CAPS:
        return MODEL_CAPS[key]
    # Fallbacks per provider
    if provider == "openai":
        return {"context": 128_000, "max_output_tokens": 4_096}
    if provider == "anthropic":
        return {"context": 200_000, "max_output_tokens": 8_192}
    return {"context": 32_000, "max_output_tokens": 2_048}
