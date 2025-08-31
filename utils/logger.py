from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def _log_path() -> Path:
    p = os.getenv("AIFRED_LOG_PATH")
    if p:
        return Path(p)
    return Path("aifred.log")


_LOGGER = None


def get_logger() -> logging.Logger:
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER
    logger = logging.getLogger("aifred")
    logger.setLevel(logging.INFO)
    log_file = _log_path()
    try:
        handler = RotatingFileHandler(log_file, maxBytes=512_000, backupCount=3)
        fmt = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    except Exception:
        # Fallback to stderr only
        stream = logging.StreamHandler()
        logger.addHandler(stream)
    _LOGGER = logger
    return logger

