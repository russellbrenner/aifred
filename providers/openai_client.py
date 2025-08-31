from __future__ import annotations

import os
from typing import Dict, List, Optional


class OpenAIClient:
    """Minimal OpenAI client that normalises responses.

    send() accepts provider-agnostic arguments and builds a Chat Completions request.
    Tools are currently a no-op placeholder; mapping requires concrete tool schemas.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.dry_run = os.getenv("AIFRED_DRY_RUN") == "1"

    def name(self) -> str:
        return "openai"

    def _missing_key_error(self) -> Dict:
        return {
            "text": "Error: OpenAI API key missing. Set OPENAI_API_KEY.",
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
        # Build OpenAI Chat API payload
        openai_messages = []
        if system:
            openai_messages.append({"role": "system", "content": system})
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            openai_messages.append({"role": role, "content": content})

        payload: Dict = {
            "model": model,
            "messages": openai_messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        # Tool schemas (placeholders, not executed here)
        if tools:
            try:
                from utils.tools import openai_tool_defs
                tool_defs = openai_tool_defs(tools)
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
            tool_calls = []
            if tools:
                tool_calls = [{"name": tools[0], "arguments": {"query": "test"}}]
            return {
                "text": f"[dry-run openai:{model}] {messages[-1]['content']}",
                "tool_calls": tool_calls,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
            }

        if not self.api_key:
            return self._missing_key_error()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            import requests  # lazy import to allow dry-run without dependency
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]["message"]
            text = choice.get("content", "")
            tool_calls = choice.get("tool_calls", [])
            usage = data.get("usage", {})
            return {"text": text, "tool_calls": tool_calls, "usage": usage}
        except Exception as e:
            return {
                "text": f"Error contacting OpenAI: {e}",
                "tool_calls": [],
                "usage": {},
                "error": True,
            }
