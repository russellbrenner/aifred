from __future__ import annotations

import os
from typing import Dict, List, Optional


class PerplexityClient:
    """Minimal Perplexity client using OpenAI-compatible Chat Completions schema.

    API: https://api.perplexity.ai/chat/completions
    Auth: Authorization: Bearer <PERPLEXITY_API_KEY>
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.dry_run = os.getenv("AIFRED_DRY_RUN") == "1"

    def name(self) -> str:
        return "perplexity"

    def _missing_key_error(self) -> Dict:
        return {
            "text": "Error: Perplexity API key missing. Set PERPLEXITY_API_KEY.",
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
                "text": f"[dry-run perplexity:{model}] {messages[-1]['content']}",
                "tool_calls": [],
                "usage": {},
            }
        if not self.api_key:
            return self._missing_key_error()

        # Build OpenAI-like messages (prepend system if provided)
        req_msgs = []
        if system:
            req_msgs.append({"role": "system", "content": system})
        req_msgs += [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in messages]

        payload: Dict = {
            "model": model,
            "messages": req_msgs,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            import requests
            resp = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})
            return {"text": text, "tool_calls": [], "usage": usage}
        except Exception as e:
            return {"text": f"Error contacting Perplexity: {e}", "tool_calls": [], "usage": {}, "error": True}

