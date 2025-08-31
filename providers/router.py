from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple, TypedDict


class ProviderCapability(TypedDict):
    tool_use: bool
    tool_names: Set[str]


OPENAI_PREFIXES: Tuple[str, ...] = (
    "gpt-",
    "o4",
    "o3",
)

ANTHROPIC_PREFIXES: Tuple[str, ...] = (
    "claude-",
)


def route(model_hint: Optional[str], provider_hint: Optional[str]) -> str:
    """Return "openai" or "anthropic" using model prefixes or hint.

    Priority: explicit provider_hint -> model prefix mapping -> default "openai".
    """
    if provider_hint in {"openai", "anthropic"}:
        return provider_hint

    if model_hint:
        m = model_hint.lower()
        if any(m.startswith(p) for p in OPENAI_PREFIXES):
            return "openai"
        if any(m.startswith(p) for p in ANTHROPIC_PREFIXES):
            return "anthropic"

    return "openai"


PROVIDER_CAPS: Dict[str, ProviderCapability] = {
    "openai": {
        "tool_use": True,
        "tool_names": {"browse", "code", "python", "fetch_url", "citation_extract", "case_search"},
    },
    "anthropic": {
        "tool_use": True,
        "tool_names": {"browse", "code", "fetch_url", "citation_extract", "case_search"},
    },
}


def validate_tools(provider: str, requested: List[str]) -> Tuple[List[str], List[str]]:
    """Return (supported, dropped) tools for provider.

    Unknown tools are dropped and reported.
    """
    caps = PROVIDER_CAPS.get(provider, {"tool_use": False, "tool_names": set()})
    if not caps.get("tool_use"):
        return [], list(requested)
    allowed = caps.get("tool_names", set())
    supported = [t for t in requested if t in allowed]
    dropped = [t for t in requested if t not in allowed]
    return supported, dropped
