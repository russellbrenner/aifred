#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def load_actions():
    p = Path("actions/actions.json")
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return []


def items(lst):
    print(json.dumps({"items": lst}))


def build(query: str):
    acts = load_actions()
    q = query.strip()
    out = []
    # Custom instruction and question entries similar to Ayai
    if q:
        out.append({
            "uid": "custom-instruction",
            "title": "Custom Instruction",
            "subtitle": q,
            "arg": json.dumps({"id": "custom-instruction", "prompt": q, "mode": "copy"}),
            "mods": {
                "cmd": {"subtitle": "Paste (replace)", "arg": json.dumps({"id": "custom-instruction", "prompt": q, "mode": "paste"})},
                "alt": {"subtitle": "Stream (preserve)", "arg": json.dumps({"id": "custom-instruction", "prompt": q, "mode": "stream"})}
            }
        })
        out.append({
            "uid": "custom-question",
            "title": "Custom Question",
            "subtitle": q + " ?",
            "arg": json.dumps({"id": "custom-question", "prompt": q + "?", "mode": "copy"}),
            "mods": {
                "cmd": {"subtitle": "Paste (replace)", "arg": json.dumps({"id": "custom-question", "prompt": q + "?", "mode": "paste"})},
                "alt": {"subtitle": "Stream (preserve)", "arg": json.dumps({"id": "custom-question", "prompt": q + "?", "mode": "stream"})}
            }
        })
    for a in acts:
        out.append({
            "uid": a["id"],
            "title": a["title"],
            "subtitle": a.get("prompt", "")[:80],
            "arg": json.dumps({"id": a["id"], "mode": "copy"}),
            "mods": {
                "cmd": {"subtitle": "Paste (replace)", "arg": json.dumps({"id": a["id"], "mode": "paste"})},
                "alt": {"subtitle": "Stream (preserve)", "arg": json.dumps({"id": a["id"], "mode": "stream"})}
            }
        })
    if not out:
        out.append({
            "uid": "empty",
            "title": "Type an instruction or pick a preset",
            "subtitle": "Press Enter to copy, Cmd-Enter to paste, Alt-Enter to stream",
            "arg": "{}"
        })
    items(out)


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    build(query)


if __name__ == "__main__":
    main()
