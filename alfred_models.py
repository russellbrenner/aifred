#!/usr/bin/env python3

import json
import sys
from typing import Dict, List

from utils.user_config import get_option, set_option


POPULAR: Dict[str, List[str]] = {
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o4-mini"],
    "anthropic": ["claude-3-7-sonnet", "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
    "perplexity": ["llama-3.1-70b-instruct", "llama-3.1-8b-instruct"],
    "gemini": ["gemini-1.5-pro", "gemini-1.5-flash"],
    "openrouter": [
        "openrouter/anthropic/claude-3.5-sonnet",
        "openrouter/openai/gpt-4o",
        "openrouter/google/gemini-1.5-pro",
    ],
}


def jprint(items):
    print(json.dumps({"items": items}))


def list_providers():
    active = get_option("provider", None)
    items = []
    for p in ["openai", "anthropic", "perplexity", "gemini", "openrouter"]:
        mark = "✓" if p == active else ""
        items.append({
            "uid": f"prov-{p}",
            "title": f"{p} {mark}",
            "arg": json.dumps({"cmd": "set-provider", "provider": p}),
        })
    jprint(items)


def list_models(provider: str):
    current = get_option(f"model_default_{provider}", None)
    items = []
    for m in POPULAR.get(provider, []):
        mark = "✓" if m == current else ""
        items.append({
            "uid": f"model-{provider}-{m}",
            "title": f"{m} {mark}",
            "arg": json.dumps({"cmd": "set-model", "provider": provider, "model": m}),
        })
    jprint(items or [{"uid": "empty", "title": "No models listed", "arg": "{}"}])


def run_action(a: str):
    try:
        action = json.loads(a)
    except Exception:
        print("Invalid action")
        return
    cmd = action.get("cmd")
    if cmd == "set-provider":
        set_option("provider", action.get("provider"))
        print(f"Provider set to {action.get('provider')}")
        return
    if cmd == "set-model":
        prov = action.get("provider")
        model = action.get("model")
        set_option(f"model_default_{prov}", model)
        print(f"Default model for {prov} set to {model}")
        return
    print("No-op")


def main():
    if len(sys.argv) == 1:
        list_providers()
        return
    q = sys.argv[1].strip()
    if q.startswith("{"):
        run_action(q)
        return
    # If provider name entered, list models
    prov = q.lower()
    if prov in POPULAR:
        list_models(prov)
    else:
        list_providers()


if __name__ == "__main__":
    main()
