from __future__ import annotations

import math
from typing import Dict, List, Tuple


def estimate_tokens_text(text: str) -> int:
    # Crude heuristic: ~4 chars per token
    if not text:
        return 0
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

