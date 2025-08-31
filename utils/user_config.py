from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


def _config_path() -> Path:
    data_dir = os.getenv("alfred_workflow_data")
    if data_dir:
        p = Path(data_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p / "aifred_config.json"
    return Path("aifred_config.json")


def load_config() -> Dict[str, Any]:
    p = _config_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_config(cfg: Dict[str, Any]) -> None:
    p = _config_path()
    p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def set_option(key: str, value: Any) -> None:
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)


def get_option(key: str, default: Any = None) -> Any:
    return load_config().get(key, default)

