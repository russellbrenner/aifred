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
        # Extract inline PPLX options from system string: [PPLX_OPTS:{json}]
        pplx_opts = {}
        if system and "[PPLX_OPTS:" in system:
            try:
                marker = system.split("[PPLX_OPTS:", 1)[1]
                json_part = marker.split("]", 1)[0]
                import json as _json
                pplx_opts = _json.loads(json_part)
            except Exception:
                pplx_opts = {}
            # strip marker from system
            try:
                system = system.replace(f"[PPLX_OPTS:{json_part}]", "").strip()
            except Exception:
                pass
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
        # Perplexity options
        if tools:
            payload["return_citations"] = True
        # Map selected PPLX options
        if pplx_opts.get("recency"):
            payload["search_recency"] = pplx_opts["recency"]
        if pplx_opts.get("depth"):
            payload["search_depth"] = pplx_opts["depth"]
        if pplx_opts.get("domain"):
            payload["search_domain"] = pplx_opts["domain"]
        if pplx_opts.get("citations") is not None:
            payload["return_citations"] = str(pplx_opts["citations"]).lower() in {"1", "true", "yes", "on"}
        if pplx_opts.get("images") is not None:
            payload["return_images"] = str(pplx_opts["images"]).lower() in {"1", "true", "yes", "on"}

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
