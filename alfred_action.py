#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
from typing import Dict, List

from providers.anthropic_client import AnthropicClient
from providers.openai_client import OpenAIClient
from providers.router import route, validate_tools
from store import Store
from utils.directives import Directives, parse_directives
from utils.logger import get_logger


def _defaults():
    provider = os.getenv("AIFRED_PROVIDER_DEFAULT", "openai").lower()
    model_openai = os.getenv("AIFRED_MODEL_DEFAULT_OPENAI", "gpt-4o")
    model_anthropic = os.getenv("AIFRED_MODEL_DEFAULT_ANTHROPIC", "claude-3-7-sonnet")
    return provider, model_openai, model_anthropic


def _load_system_prompt(directives_sys: str | None) -> str:
    if directives_sys:
        return directives_sys
    path = os.getenv("AIFRED_SYSTEM_PROMPT_PATH")
    if path and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return "You are a helpful assistant. Keep answers concise and clear."


def _get_client(provider: str):
    return OpenAIClient() if provider == "openai" else AnthropicClient()


def _resolve_provider_model(d: Directives) -> tuple[str, str]:
    provider_default, model_openai, model_anthropic = _defaults()
    provider = route(d.model, d.provider) if (d.model or d.provider) else provider_default
    model = d.model or (model_openai if provider == "openai" else model_anthropic)
    return provider, model


def _payload_from_arg(arg: str) -> Dict:
    try:
        return json.loads(arg)
    except Exception:
        # Legacy fallbacks
        if arg.startswith("continue:"):
            return {"legacy": arg}
        if arg.startswith("new:"):
            return {"legacy": arg}
        return {"error": "Unrecognised argument"}


def handle_action(arg: str) -> None:
    log = get_logger()
    store = Store()

    payload = _payload_from_arg(arg)
    if "error" in payload:
        print(payload["error"])
        return

    # Legacy paths currently not supported in new flow
    if payload.get("legacy"):
        print("Legacy actions are deprecated in this version.")
        return

    query = payload.get("query", "")
    directives_dict = payload.get("directives", {})
    d = Directives(**{k: directives_dict.get(k) for k in Directives().__dict__.keys() if k in directives_dict})

    provider, model = _resolve_provider_model(d)
    tools_requested = d.tools or []
    tools_supported, tools_dropped = validate_tools(provider, tools_requested)

    system_prompt = _load_system_prompt(d.sys)

    # Resolve thread
    thread_hint = payload.get("thread_hint")
    thread = None
    if d.new:
        thread_id = store.create_thread(provider, model, d.name)
        thread = store.get_latest_thread(provider, model)
    elif thread_hint and isinstance(thread_hint, dict) and thread_hint.get("id"):
        # Minimal fetch to ensure existence
        # Use latest messages afterward
        thread = store.get_latest_thread(provider, model)  # best-effort
        if not thread:
            thread_id = store.create_thread(provider, model, d.name)
            thread = store.get_latest_thread(provider, model)
    elif d.cont:
        thread = store.get_latest_thread(provider, model if d.model else None)
        if not thread:
            thread_id = store.create_thread(provider, model, d.name)
            thread = store.get_latest_thread(provider, model)
    else:
        # Default: create a new thread when sending a fresh query
        thread = store.get_latest_thread(provider, model if d.model else None)
        if not thread or query:
            thread_id = store.create_thread(provider, model, d.name)
            thread = store.get_latest_thread(provider, model)

    if not thread:
        print("Failed to resolve thread")
        return

    # Assemble messages
    history = [
        {"role": m.role, "content": m.content} for m in store.get_thread_messages(thread.id, limit=50)
    ]
    if query:
        store.add_message(thread.id, "user", query, meta={"directives": directives_dict})
        history.append({"role": "user", "content": query})

    client = _get_client(provider)
    resp = client.send(
        system=system_prompt,
        messages=history,
        model=model,
        temperature=float(d.temp) if d.temp is not None else 0.4,
        max_tokens=int(d.max) if d.max is not None else None,
        tools=tools_supported,
    )

    text = resp.get("text", "")
    usage = resp.get("usage", {})
    had_error = resp.get("error", False)

    # Persist assistant response
    if text:
        store.add_message(thread.id, "assistant", text, meta={"usage": usage, "tools_dropped": tools_dropped})

    # Minimal user feedback output for Alfred
    header = f"{provider} {model}"
    if tools_dropped:
        header += f" | unsupported tools dropped: {', '.join(tools_dropped)}"

    print(f"{header}\n\n{text if text else 'No response.'}")

    # Logging (meta only unless AIFRED_DEBUG=1)
    debug = os.getenv("AIFRED_DEBUG") == "1"
    if debug:
        log.info(
            "sent provider=%s model=%s tools=%s usage=%s query=%s",
            provider,
            model,
            tools_supported,
            usage,
            query,
        )
    else:
        log.info(
            "sent provider=%s model=%s tools=%s usage=%s",
            provider,
            model,
            tools_supported,
            usage,
        )


def main() -> None:
    if len(sys.argv) < 2:
        print("No action specified")
        return
    arg = sys.argv[1]
    handle_action(arg)


if __name__ == "__main__":
    main()
