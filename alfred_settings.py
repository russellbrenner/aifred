#!/usr/bin/env python3

import json
import sys

from utils.config import get_defaults
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

    lst = [
        {"uid": "notify", "title": f"Notifications: {'On' if notify else 'Off'}", "arg": "toggle:notify"},
        {"uid": "clipboard", "title": f"Copy Replies: {'On' if clip else 'Off'}", "arg": "toggle:clipboard"},
        {"uid": "profile", "title": f"Profile: {profile}", "arg": "set:profile:"},
        {"uid": "max_in", "title": f"Max Input Tokens: {max_in}", "arg": "set:max_input_tokens:"},
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


def main():
    if len(sys.argv) == 1:
        list_settings()
        return
    handle_action(sys.argv[1])


if __name__ == "__main__":
    main()

