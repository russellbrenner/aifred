#!/usr/bin/env python3

import json
import sys
from typing import Dict, Any

from utils.config import DEFAULT_LEGAL_PROMPT
from utils.user_config import load_config, save_config


def jprint(items):
    print(json.dumps({"items": items}))


def list_items(query: str) -> None:
    cfg = load_config()
    personas: Dict[str, Dict[str, Any]] = cfg.get("personas", {}) or {}
    active = cfg.get("active_persona")

    q = query.strip()
    items = []

    # Creation via query: "new <name>: <prompt>"
    if q.lower().startswith("new ") or q.lower().startswith("create "):
        head, rest = q.split(" ", 1)
        if ":" in rest:
            name, prompt = rest.split(":", 1)
            name = name.strip()
            prompt = prompt.strip()
        else:
            name = rest.strip()
            prompt = DEFAULT_LEGAL_PROMPT if name.lower() == "legal" else "You are a helpful assistant."
        if name:
            items.append({
                "uid": f"create-{name}",
                "title": f"Create persona \"{name}\"",
                "subtitle": (prompt[:80] + ("…" if len(prompt) > 80 else "")) if prompt else "Default prompt",
                "arg": json.dumps({"cmd": "create", "name": name, "prompt": prompt}),
            })
            return jprint(items)

    # Edit via query: "edit <name>: <prompt>"
    if q.lower().startswith("edit ") and ":" in q:
        _, rest = q.split(" ", 1)
        name, prompt = rest.split(":", 1)
        name = name.strip()
        prompt = prompt.strip()
        if name:
            items.append({
                "uid": f"edit-{name}",
                "title": f"Update prompt for \"{name}\"",
                "subtitle": prompt[:80] + ("…" if len(prompt) > 80 else ""),
                "arg": json.dumps({"cmd": "edit", "name": name, "prompt": prompt}),
            })
            return jprint(items)

    # Default: list personas
    if personas:
        for name, data in personas.items():
            is_active = (name == active)
            title = f"{name} {'✓' if is_active else ''}"
            subtitle = (data.get("prompt") or "").strip()[:80]
            items.append({
                "uid": f"persona-{name}",
                "title": title,
                "subtitle": subtitle,
                "arg": json.dumps({"cmd": "activate", "name": name}),
                "mods": {
                    "alt": {"subtitle": "Delete persona", "arg": json.dumps({"cmd": "delete", "name": name})},
                    "cmd": {"subtitle": "Edit prompt: type 'edit %s: <prompt>'" % name, "arg": json.dumps({"cmd": "noop"})}
                }
            })
    # Helper hints
    items.insert(0, {
        "uid": "hint-new",
        "title": "New persona…",
        "subtitle": "Type: new <name>: <prompt>",
        "arg": json.dumps({"cmd": "noop"})
    })
    jprint(items or [{"uid": "empty", "title": "No personas yet", "subtitle": "Type: new <name>: <prompt>", "arg": json.dumps({"cmd": "noop"})}])


def run_action(action_json: str) -> None:
    try:
        action = json.loads(action_json)
    except Exception:
        print("Invalid action payload")
        return
    cmd = action.get("cmd")
    cfg = load_config()
    personas: Dict[str, Dict[str, Any]] = cfg.get("personas", {}) or {}
    if cmd == "create":
        name = action.get("name")
        prompt = action.get("prompt") or "You are a helpful assistant."
        if not name:
            print("Missing name")
            return
        personas[name] = {"prompt": prompt}
        cfg["personas"] = personas
        cfg["active_persona"] = name
        save_config(cfg)
        print(f"Created persona '{name}' and set active")
    elif cmd == "activate":
        name = action.get("name")
        if name not in personas:
            print("Persona not found")
            return
        cfg["active_persona"] = name
        save_config(cfg)
        print(f"Activated persona '{name}'")
    elif cmd == "edit":
        name = action.get("name")
        prompt = action.get("prompt")
        if name not in personas or not prompt:
            print("Missing persona or prompt")
            return
        personas[name]["prompt"] = prompt
        cfg["personas"] = personas
        save_config(cfg)
        print(f"Updated persona '{name}' prompt")
    elif cmd == "delete":
        name = action.get("name")
        if name in personas:
            del personas[name]
            cfg["personas"] = personas
            if cfg.get("active_persona") == name:
                cfg["active_persona"] = None
            save_config(cfg)
            print(f"Deleted persona '{name}'")
        else:
            print("Persona not found")
    else:
        print("No operation")


def main():
    if len(sys.argv) == 1:
        list_items("")
        return
    arg = sys.argv[1]
    # If arg looks like JSON, treat as action
    if (arg.startswith("{") and arg.endswith("}")) or arg.startswith("["):
        run_action(arg)
    else:
        list_items(arg)


if __name__ == "__main__":
    main()
