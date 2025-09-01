#!/usr/bin/env python3

import json
import sys

from utils.config import get_defaults, DEFAULT_LEGAL_PROMPT
from utils.user_config import get_option, set_option, load_config


def items(lst):
    print(json.dumps({"items": lst}))


def list_settings():
    d = get_defaults()
    cfg = load_config()
    notify = cfg.get("notify", False)
    clip = cfg.get("copy_clipboard", False)
    profile = cfg.get("profile", d.profile)
    max_in = cfg.get("max_input_tokens", d.max_input_tokens)
    tool_exec = cfg.get("tool_exec", False)
    stream = cfg.get("stream", False)
    persona = cfg.get("active_persona", None) or ("legal" if d.legal_mode else None)

    lst = [
        {"uid": "notify", "title": f"Notifications: {'On' if notify else 'Off'}", "arg": "toggle:notify"},
        {"uid": "clipboard", "title": f"Copy Replies: {'On' if clip else 'Off'}", "arg": "toggle:clipboard"},
        {"uid": "tool_exec", "title": f"Tool Execution: {'On' if tool_exec else 'Off'}", "arg": "toggle:tool_exec"},
        {"uid": "stream", "title": f"Streaming (OpenAI): {'On' if stream else 'Off'}", "arg": "toggle:stream"},
        {"uid": "profile", "title": f"Profile: {profile}", "arg": "set:profile:"},
        {"uid": "max_in", "title": f"Max Input Tokens: {max_in}", "arg": "set:max_input_tokens:"},
        {"uid": "persona", "title": f"Persona: {persona or 'none'}", "arg": "set:active_persona:"},
        {"uid": "persona-legal", "title": "Enable Legal Persona (defaults)", "subtitle": "Australian English, Victorian bar level", "arg": "enable:legal"},
        {"uid": "persona-legal-edit", "title": "Edit Legal Persona Prompt…", "arg": "set:persona_prompt:legal:"},
    ]
    items(lst)


def handle_action(arg: str):
    if arg.startswith("toggle:notify"):
        cur = bool(get_option("notify", False))
        set_option("notify", not cur)
        print("Notifications toggled")
        return
    if arg.startswith("toggle:clipboard"):
        cur = bool(get_option("copy_clipboard", False))
        set_option("copy_clipboard", not cur)
        print("Clipboard toggle updated")
        return
    if arg.startswith("set:profile:"):
        value = arg.split(":", 2)[2]
        if not value:
            print("Provide a profile name")
            return
        set_option("profile", value)
        print(f"Profile set to {value}")
        return
    if arg.startswith("set:max_input_tokens:"):
        value = arg.split(":", 2)[2]
        try:
            n = int(value)
            set_option("max_input_tokens", n)
            print(f"Max input tokens set to {n}")
        except Exception:
            print("Invalid number")
    if arg.startswith("toggle:tool_exec"):
        cur = bool(get_option("tool_exec", False))
        set_option("tool_exec", not cur)
        print("Tool execution toggled")
        return
    if arg.startswith("toggle:stream"):
        cur = bool(get_option("stream", False))
        set_option("stream", not cur)
        print("Streaming toggle updated")
        return
    if arg.startswith("set:active_persona:"):
        value = arg.split(":", 2)[2]
        if not value:
            set_option("active_persona", None)
            print("Persona disabled")
        else:
            set_option("active_persona", value)
            print(f"Persona set to {value}")
        return
    if arg.startswith("enable:legal"):
        # ensure personas map contains legal with default prompt
        cfg = load_config()
        personas = cfg.get("personas", {}) or {}
        if "legal" not in personas:
            personas["legal"] = {"prompt": DEFAULT_LEGAL_PROMPT}
        cfg["personas"] = personas
        cfg["active_persona"] = "legal"
        set_option("legal_mode", True)
        # Save back
        from utils.user_config import save_config
        save_config(cfg)
        print("Enabled legal persona with defaults")
        return
    if arg.startswith("set:persona_prompt:legal:"):
        value = arg.split(":", 3)[3]
        cfg = load_config()
        personas = cfg.get("personas", {}) or {}
        personas.setdefault("legal", {})["prompt"] = value or DEFAULT_LEGAL_PROMPT
        from utils.user_config import save_config
        cfg["personas"] = personas
        save_config(cfg)
        print("Updated legal persona prompt")


def main():
    if len(sys.argv) == 1:
        list_settings()
        return
    handle_action(sys.argv[1])


if __name__ == "__main__":
    main()
