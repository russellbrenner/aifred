from __future__ import annotations

import os
from typing import Dict, List, Optional


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

    def _build_payload(
        self,
        system: str,
        messages: List[Dict],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        tools: List[str],
    ) -> Dict:
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

        # Tool schemas (placeholders, not executed here)
        if tools:
            try:
                from utils.tools import anthropic_tool_defs
                tool_defs = anthropic_tool_defs(tools)
                if tool_defs:
                    payload["tools"] = tool_defs
                    payload["tool_choice"] = "auto"
            except Exception:
                pass
        return payload

    def send(
        self,
        system: str,
        messages: List[Dict],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        tools: List[str],
    ) -> Dict:
        payload = self._build_payload(system, messages, model, temperature, max_tokens, tools)
        if self.dry_run:
            return {
                "text": f"[dry-run anthropic:{model}] {messages[-1]['content']}",
                "tool_calls": [],
                "usage": {"input_tokens": 0, "output_tokens": 0},
            }

        if not self.api_key:
            return self._missing_key_error()

        headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        try:
            import requests  # lazy import to allow dry-run without dependency
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data.get("content", [])
            text_parts = []
            tool_calls = []
            for c in content:
                ctype = c.get("type")
                if ctype in {None, "text"}:
                    text_parts.append(c.get("text", ""))
                elif ctype == "tool_use":
                    # Normalise tool calls without execution
                    tool_calls.append({
                        "name": c.get("name"),
                        "arguments": c.get("input", {}),
                    })
            text = "".join(text_parts)
            usage = data.get("usage", {})
            return {"text": text, "tool_calls": tool_calls, "usage": usage}
        except Exception as e:
            return {
                "text": f"Error contacting Anthropic: {e}",
                "tool_calls": [],
                "usage": {},
                "error": True,
            }
