from __future__ import annotations

from typing import Dict, List


def openai_tool_defs(tool_names: List[str]) -> List[Dict]:
    defs: List[Dict] = []
    for t in tool_names:
        if t == "browse":
            defs.append(
                {
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "description": "Search the web for up-to-date information.",
                        "parameters": {
                            "type": "object",
                            "properties": {"query": {"type": "string"}},
                            "required": ["query"],
                        },
                    },
                }
            )
        elif t == "code":
            defs.append(
                {
                    "type": "function",
                    "function": {
                        "name": "code_run",
                        "description": "Draft or explain code; returns code text.",
                        "parameters": {
                            "type": "object",
                            "properties": {"instructions": {"type": "string"}},
                            "required": ["instructions"],
                        },
                    },
                }
            )
        elif t == "python":
            defs.append(
                {
                    "type": "function",
                    "function": {
                        "name": "python_run",
                        "description": "Propose Python to execute elsewhere (no local execution).",
                        "parameters": {
                            "type": "object",
                            "properties": {"code": {"type": "string"}},
                            "required": ["code"],
                        },
                    },
                }
            )
    return defs


def anthropic_tool_defs(tool_names: List[str]) -> List[Dict]:
    defs: List[Dict] = []
    for t in tool_names:
        if t == "browse":
            defs.append(
                {
                    "name": "web_search",
                    "description": "Search the web for up-to-date information.",
                    "input_schema": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"],
                    },
                }
            )
        elif t == "code":
            defs.append(
                {
                    "name": "code_run",
                    "description": "Draft or explain code; returns code text.",
                    "input_schema": {
                        "type": "object",
                        "properties": {"instructions": {"type": "string"}},
                        "required": ["instructions"],
                    },
                }
            )
        elif t == "python":
            defs.append(
                {
                    "name": "python_run",
                    "description": "Propose Python to execute elsewhere (no local execution).",
                    "input_schema": {
                        "type": "object",
                        "properties": {"code": {"type": "string"}},
                        "required": ["code"],
                    },
                }
            )
    return defs

