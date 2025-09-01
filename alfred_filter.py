#!/usr/bin/env python3

import json
import os
import sys
from datetime import datetime

from providers.router import route
from utils.config import get_defaults
from store import Store
from utils.directives import parse_directives, summarise_directives


def alfred_items(items):
    return json.dumps({"items": items})


def _resolve_provider_model(model_hint, provider_hint):
    defaults = get_defaults()
    provider_default = defaults.provider
    provider = route(model_hint, provider_hint) if (model_hint or provider_hint) else provider_default
    if provider == "openai":
        model = model_hint or defaults.model_openai
    elif provider == "anthropic":
        model = model_hint or defaults.model_anthropic
    elif provider == "perplexity":
        model = model_hint or defaults.model_perplexity
    elif provider == "gemini":
        model = model_hint or defaults.model_gemini
    elif provider == "openrouter":
        model = model_hint or defaults.model_openrouter
    else:
        model = model_hint or defaults.model_openai
    return provider, model


def _thread_item(t) -> dict:
    title = t.name or "(untitled)"
    subtitle = f"{t.provider} {t.model} • {t.updated_at}"
    # Provide Large Type and copy previews using the last assistant message
    # We fetch on-demand in alfred_action if needed, but also surface via text field when available
    # Note: Alfred shows Large Type with ⌘L
    try:
        store = Store()
        msgs = store.get_thread_messages(t.id, limit=1_000)
        last_assistant = next((m for m in reversed(msgs) if m.role == "assistant" and m.content), None)
        preview = last_assistant.content if last_assistant else ""
    except Exception:
        preview = ""
    payload = {
        "query": "",
        "directives": {"cont": True, "provider": t.provider, "model": t.model, "name": t.name},
        "thread_hint": {"id": t.id},
    }
    return {
        "uid": f"thread-{t.id}",
        "title": f"{title}",
        "subtitle": subtitle,
        "arg": json.dumps(payload),
        "text": {"copy": preview, "largetype": f"{title}\n\n{preview[:2000]}"} if preview else None,
    }


def build_items(query: str) -> str:
    store = Store()
    defaults = get_defaults()
    cleaned, d = parse_directives(query)
    provider, model = _resolve_provider_model(d.model, d.provider)

    items = []

    # When query text exists, show "Send" option first
    if cleaned:
        summary = summarise_directives(d)
        # If legal mode and no explicit tools, show intended default tools
        try:
            defs = get_defaults()
            if defs.legal_mode and not d.tools:
                summary = (summary + (" | " if summary else "")) + "tools: " + ",".join(defs.legal_tools)
            # Show persona
            if defs.persona_name:
                summary = (summary + (" | " if summary else "")) + f"persona: {defs.persona_name}"
        except Exception:
            pass
        payload = {
            "query": cleaned,
            "directives": d.to_dict(),
            "provider": provider,
            "model": model,
            "thread_hint": None,
        }
        items.append({
            "uid": "send",
            "title": f"Send to {provider} {model}",
            "subtitle": summary,
            "arg": json.dumps(payload),
        })

    # List recent threads (limit 5 when query, else 20)
    limit = 5 if cleaned else 20
    for t in store.get_recent_threads(limit=limit, profile=defaults.profile):
        items.append(_thread_item(t))

    # Empty state
    if not items:
        items.append({
            "uid": "empty",
            "title": "Type to start a conversation",
            "subtitle": "Use @directives for model, temp, tools, etc.",
            "arg": json.dumps({"query": "", "directives": {}, "thread_hint": None}),
        })

    return alfred_items(items)


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    print(build_items(query))


if __name__ == "__main__":
    main()
