from __future__ import annotations

import os
from typing import Any, Dict


def run_web_search(args: Dict[str, Any]) -> Dict[str, Any]:
    query = args.get("query", "").strip()
    if not query:
        return {"error": "missing query"}
    # If disabled or no network, return stub
    if os.getenv("AIFRED_DRY_RUN") == "1" or os.getenv("AIFRED_NO_NET") == "1":
        return {"results": [f"Stub result for: {query}"]}
    try:
        import requests  # lazy import
        resp = requests.get(
            "https://duckduckgo.com/html/",
            params={"q": query},
            timeout=10,
            headers={"User-Agent": "aifred/1.0"},
        )
        resp.raise_for_status()
        # naive parse of snippet text
        text = resp.text
        hits = []
        for line in text.splitlines():
            line = line.strip()
            if "result__a" in line and ">" in line:
                # strip tags
                title = line.split(">", 1)[-1]
                title = title.replace("</a", "").strip()
                hits.append(title)
            if len(hits) >= 3:
                break
        if not hits:
            hits = ["No results parsed"]
        return {"results": hits}
    except Exception as e:
        return {"error": str(e)}


def run_code_run(args: Dict[str, Any]) -> Dict[str, Any]:
    instructions = args.get("instructions", "")
    return {"message": "Code generation tool placeholder", "instructions": instructions}


def run_python_run(args: Dict[str, Any]) -> Dict[str, Any]:
    code = args.get("code", "")
    return {"message": "Python execution not supported; returning code for review.", "code": code}


TOOL_IMPL = {
    "web_search": run_web_search,
    "code_run": run_code_run,
    "python_run": run_python_run,
}


def execute_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    fn = TOOL_IMPL.get(name)
    if not fn:
        return {"error": f"unknown tool: {name}"}
    return fn(arguments or {})

