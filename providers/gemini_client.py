from __future__ import annotations

import os
from typing import Dict, List, Optional


class GeminiClient:
    """Minimal Gemini client using REST (generateContent).

    Endpoint: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=API_KEY
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.dry_run = os.getenv("AIFRED_DRY_RUN") == "1"

    def name(self) -> str:
        return "gemini"

    def _missing_key_error(self) -> Dict:
        return {
            "text": "Error: Gemini API key missing. Set GEMINI_API_KEY.",
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
                "text": f"[dry-run gemini:{model}] {messages[-1]['content']}",
                "tool_calls": [],
                "usage": {},
            }
        if not self.api_key:
            return self._missing_key_error()

        # Gemini expects contents with role + parts
        contents = []
        for m in messages:
            role = m.get("role", "user")
            contents.append({"role": role, "parts": [{"text": m.get("content", "")}]} )

        payload: Dict = {
            "contents": contents,
            "generationConfig": {"temperature": temperature},
        }
        if max_tokens is not None:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            resp = requests.post(url, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            text = ""
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    text = parts[0].get("text", "")
            usage = data.get("usageMetadata", {})
            return {"text": text, "tool_calls": [], "usage": usage}
        except Exception as e:
            return {"text": f"Error contacting Gemini: {e}", "tool_calls": [], "usage": {}, "error": True}
