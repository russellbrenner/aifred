#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
from typing import Dict

from providers.anthropic_client import AnthropicClient
from providers.openai_client import OpenAIClient
from providers.router import route
from utils.config import get_defaults


def _client(provider: str):
    return OpenAIClient() if provider == "openai" else AnthropicClient()


def _apply_action(text: str, action: Dict) -> str:
    # If action carries a full prompt, substitute {{text}}
    prompt = action.get("prompt")
    if prompt:
        return prompt.replace("{{text}}", text)
    # Otherwise, treat action["prompt"] or custom prompt as instruction
    p = action.get("prompt") or action.get("instruction") or action.get("id")
    return f"{p}:\n\n{text}"


def paste_text(s: str) -> None:
    try:
        from subprocess import Popen, PIPE
        p = Popen(["pbcopy"], stdin=PIPE)
        p.communicate(input=s.encode("utf-8"))
        # Attempt paste keystroke
        os.system('osascript -e "tell application \"System Events\" to keystroke \"v\" using {command down}"')
    except Exception:
        pass


def main():
    if len(sys.argv) < 3:
        print("Usage: alfred_actions_run.py '<action_json>' '<selected_text>'")
        return
    action = json.loads(sys.argv[1])
    selected = sys.argv[2]

    defaults = get_defaults()
    provider = defaults.provider
    model = defaults.model_openai if provider == "openai" else defaults.model_anthropic

    # Build instruction as a user message and send
    instruction = _apply_action(selected, action)
    messages = [{"role": "user", "content": instruction}]
    client = _client(provider)
    resp = client.send(
        system="You transform text as instructed. Output only the transformed text.",
        messages=messages,
        model=model,
        temperature=0.2,
        max_tokens=None,
        tools=[],
    )
    text = resp.get("text", "")
    mode = action.get("mode", "copy")
    if mode == "paste":
        paste_text(text)
    else:
        try:
            from subprocess import Popen, PIPE
            p = Popen(["pbcopy"], stdin=PIPE)
            p.communicate(input=text.encode("utf-8"))
        except Exception:
            pass
    print(text)


if __name__ == "__main__":
    main()
