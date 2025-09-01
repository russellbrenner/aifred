from __future__ import annotations

import os
from typing import Dict, List, Optional


class OpenRouterClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.dry_run = os.getenv("AIFRED_DRY_RUN") == "1"

    def name(self) -> str:
        return "openrouter"

    def _missing_key_error(self) -> Dict:
        return {"text": "Error: OpenRouter API key missing. Set OPENROUTER_API_KEY.", "tool_calls": [], "usage": {}, "error": True}

    def send(self, system: str, messages: List[Dict], model: str, temperature: float, max_tokens: Optional[int], tools: List[str]) -> Dict:
        if self.dry_run:
            return {"text": f"[dry-run openrouter:{model}] {messages[-1]['content']}", "tool_calls": [], "usage": {}}
        if not self.api_key:
            return self._missing_key_error()
        req_msgs = []
        if system:
            req_msgs.append({"role": "system", "content": system})
        for m in messages:
            req_msgs.append({"role": m.get("role", "user"), "content": m.get("content", "")})
        payload: Dict = {"model": model, "messages": req_msgs, "temperature": temperature}
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "X-Title": os.getenv("OPENROUTER_TITLE", "aifred")}
        try:
            import os, requests
            if os.getenv("AIFRED_STREAM") == "1":
                with requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={**payload, "stream": True}, timeout=60, stream=True) as r:
                    r.raise_for_status()
                    acc = []
                    for line in r.iter_lines(decode_unicode=True):
                        if not line:
                            continue
                        if line.startswith("data: "):
                            data_str = line[len("data: ") :].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                import json as _json
                                evt = _json.loads(data_str)
                                delta = evt.get("choices", [{}])[0].get("delta", {})
                                if "content" in delta:
                                    acc.append(delta["content"])
                            except Exception:
                                continue
                    return {"text": "".join(acc), "tool_calls": [], "usage": {}}
            else:
                resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                choice = data.get("choices", [{}])[0]
                text = choice.get("message", {}).get("content", "")
                usage = data.get("usage", {})
                return {"text": text, "tool_calls": [], "usage": usage}
        except Exception as e:
            return {"text": f"Error contacting OpenRouter: {e}", "tool_calls": [], "usage": {}, "error": True}
