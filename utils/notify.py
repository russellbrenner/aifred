from __future__ import annotations

import os
from subprocess import Popen, PIPE


def notify(title: str, message: str) -> None:
    if os.getenv("AIFRED_NOTIFY") != "1":
        return
    try:
        script = f'display notification "{message}" with title "{title}"'
        Popen(["osascript", "-e", script], stdout=PIPE, stderr=PIPE)
    except Exception:
        pass

