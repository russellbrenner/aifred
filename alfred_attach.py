#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from providers.anthropic_client import AnthropicClient
from providers.openai_client import OpenAIClient
from utils.config import get_defaults
from store import Store


def extract_text(path: Path) -> str:
    """Extract text using pandoc if present; fallback to plain read."""
    try:
        if shutil.which("pandoc"):
            out = subprocess.check_output(["pandoc", "-t", "plain", str(path)], timeout=30)
            return out.decode("utf-8", errors="ignore")
    except Exception:
        pass
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return f"[Attachment: {path.name}]"


def summarize_text(text: str, client, model: str) -> str:
    prompt = f"Summarize the following document briefly and list key points if helpful.\n\n{text[:8000]}"
    resp = client.send(
        system="You summarize documents clearly and concisely.",
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=0.2,
        max_tokens=600,
        tools=[],
    )
    return resp.get("text", "")


def main():
    if len(sys.argv) < 2:
        print("Usage: alfred_attach.py <file_path>")
        return
    file_path = Path(sys.argv[1]).expanduser()
    if not file_path.exists():
        print("File not found")
        return
    defaults = get_defaults()
    provider = defaults.provider
    model = defaults.model_openai if provider == "openai" else defaults.model_anthropic
    client = OpenAIClient() if provider == "openai" else AnthropicClient()

    text = extract_text(file_path)
    summary = summarize_text(text, client, model)

    # Create a new thread and persist the attachment summary
    store = Store()
    thread_id = store.create_thread(provider, model, name=file_path.stem, profile=defaults.profile)
    store.add_message(thread_id, "user", f"[Attached file: {file_path.name}]")
    if summary:
        store.add_message(thread_id, "assistant", summary)
    print(f"Attached and summarized: {file_path.name}\nThread ID: {thread_id}")


if __name__ == "__main__":
    main()
