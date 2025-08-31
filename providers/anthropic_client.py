from __future__ import annotations

import os
from typing import Dict, List, Optional

import requests


class AnthropicClient:
    """Minimal Anthropic client that normalises responses.

    Implements v1/messages shape with a normalised return.
    Tools are placeholders; no tool schema is enabled by default.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
        self.dry_run = os.getenv("AIFRED_DRY_RUN") == "1"

    def name(self) -> str:
        return "anthropic"

    def _missing_key_error(self) -> Dict:
        return {
            "text": "Error: Anthropic API key missing. Set ANTHROPIC_API_KEY.",
            "tool_calls": [],
            "usage": {},
            "error": True,
        }

    def send(
        self,
        system: str,
        messages: List[Dict],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        tools: List[str],
    ) -> Dict:
        if self.dry_run:
            return {
                "text": f"[dry-run anthropic:{model}] {messages[-1]['content']}",
                "tool_calls": [],
                "usage": {"input_tokens": 0, "output_tokens": 0},
            }

        if not self.api_key:
            return self._missing_key_error()

        anthropic_messages: List[Dict] = []
        # Anthropic supports a system string separate from messages
        for m in messages:
            role = m.get("role", "user")
            # map 'assistant' -> 'assistant', others -> 'user'/'tool'
            role_map = {
                "system": "user",  # system handled separately
                "user": "user",
                "assistant": "assistant",
                "tool": "tool",
            }
            a_role = role_map.get(role, "user")
            anthropic_messages.append({"role": a_role, "content": m.get("content", "")})

        payload: Dict = {
            "model": model,
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 1024,
        }
        if system:
            payload["system"] = system

        headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data.get("content", [])
            text = "".join([c.get("text", "") for c in content if c.get("type") in {None, "text"}])
            usage = data.get("usage", {})
            return {"text": text, "tool_calls": [], "usage": usage}
        except Exception as e:
            return {
                "text": f"Error contacting Anthropic: {e}",
                "tool_calls": [],
                "usage": {},
                "error": True,
            }

