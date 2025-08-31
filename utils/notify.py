from __future__ import annotations

import os
from subprocess import Popen, PIPE


def notify(title: str, message: str) -> None:
    enabled = os.getenv("AIFRED_NOTIFY") == "1"
    if not enabled:
        try:
            from utils.user_config import get_option
            enabled = bool(get_option("notify", False))
        except Exception:
            enabled = False
    if not enabled:
        return
    try:
        script = f'display notification "{message}" with title "{title}"'
        Popen(["osascript", "-e", script], stdout=PIPE, stderr=PIPE)
    except Exception:
        pass
