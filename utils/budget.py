from __future__ import annotations

import math
from typing import Dict, List, Tuple

_ENC = None

def _get_encoder():
    global _ENC
    if _ENC is not None:
        return _ENC
    try:
        import tiktoken  # type: ignore
        _ENC = tiktoken.get_encoding("cl100k_base")
    except Exception:
        _ENC = None
    return _ENC


def estimate_tokens_text(text: str) -> int:
    if not text:
        return 0
    enc = _get_encoder()
    if enc is not None:
        try:
            return max(1, len(enc.encode(text)))
        except Exception:
            pass
    # Fallback heuristic: ~4 chars per token
    return max(1, math.ceil(len(text) / 4))


def estimate_tokens_messages(messages: List[Dict[str, str]], system: str | None = None) -> int:
    total = 0
    if system:
        total += estimate_tokens_text(system)
    for m in messages:
        total += estimate_tokens_text(m.get("content", ""))
    return total


def trim_history(messages: List[Dict[str, str]], system: str | None, max_input_tokens: int, reserve_for_completion: int = 400) -> Tuple[List[Dict[str, str]], int]:
    """Trim oldest messages to keep input token estimate under cap.

    Returns (trimmed_messages, est_tokens).
    """
    if max_input_tokens <= 0:
        return messages, estimate_tokens_messages(messages, system)
    budget = max(1, max_input_tokens - max(0, reserve_for_completion))
    # Keep the latest messages while under budget
    kept: List[Dict[str, str]] = []
    running = estimate_tokens_text(system) if system else 0
    for m in reversed(messages):
        t = estimate_tokens_text(m.get("content", ""))
        if running + t > budget and kept:
            break
        kept.append(m)
        running += t
    kept.reverse()
    return kept, running + (estimate_tokens_text(system) if system else 0)
