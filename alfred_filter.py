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
    provider_default, model_openai, model_anthropic = (
        defaults.provider,
        defaults.model_openai,
        defaults.model_anthropic,
    )
    provider = route(model_hint, provider_hint) if (model_hint or provider_hint) else provider_default
    if provider == "openai":
        model = model_hint or model_openai
    else:
        model = model_hint or model_anthropic
    return provider, model


def _thread_item(t) -> dict:
    title = t.name or "(untitled)"
    subtitle = f"{t.provider} {t.model} • {t.updated_at}"
    payload = {
        "query": "",
        "directives": {"cont": True, "provider": t.provider, "model": t.model, "name": t.name},
        "thread_hint": {"id": t.id},
    }
    return {
        "uid": f"thread-{t.id}",
        "title": title,
        "subtitle": subtitle,
        "arg": json.dumps(payload),
    }


def build_items(query: str) -> str:
    store = Store()
    cleaned, d = parse_directives(query)
    provider, model = _resolve_provider_model(d.model, d.provider)

    items = []

    # When query text exists, show "Send" option first
    if cleaned:
        summary = summarise_directives(d)
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
    for t in store.get_recent_threads(limit=limit):
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
