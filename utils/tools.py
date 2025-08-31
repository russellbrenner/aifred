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
        elif t == "fetch_url":
            defs.append(
                {
                    "type": "function",
                    "function": {
                        "name": "fetch_url",
                        "description": "Fetch and extract readable text from a URL (best-effort).",
                        "parameters": {
                            "type": "object",
                            "properties": {"url": {"type": "string"}},
                            "required": ["url"],
                        },
                    },
                }
            )
        elif t == "citation_extract":
            defs.append(
                {
                    "type": "function",
                    "function": {
                        "name": "citation_extract",
                        "description": "Extract legal citations (cases, statutes) from text.",
                        "parameters": {
                            "type": "object",
                            "properties": {"text": {"type": "string"}},
                            "required": ["text"],
                        },
                    },
                }
            )
        elif t == "case_search":
            defs.append(
                {
                    "type": "function",
                    "function": {
                        "name": "case_search",
                        "description": "Search case law by keyword (CourtListener API).",
                        "parameters": {
                            "type": "object",
                            "properties": {"query": {"type": "string"}},
                            "required": ["query"],
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
        elif t == "fetch_url":
            defs.append(
                {
                    "name": "fetch_url",
                    "description": "Fetch and extract readable text from a URL (best-effort).",
                    "input_schema": {
                        "type": "object",
                        "properties": {"url": {"type": "string"}},
                        "required": ["url"],
                    },
                }
            )
        elif t == "citation_extract":
            defs.append(
                {
                    "name": "citation_extract",
                    "description": "Extract legal citations (cases, statutes) from text.",
                    "input_schema": {
                        "type": "object",
                        "properties": {"text": {"type": "string"}},
                        "required": ["text"],
                    },
                }
            )
        elif t == "case_search":
            defs.append(
                {
                    "name": "case_search",
                    "description": "Search case law by keyword (CourtListener API).",
                    "input_schema": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"],
                    },
                }
            )
    return defs
