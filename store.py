from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_db_path() -> Path:
    # Priority: explicit env -> Alfred workflow data -> local file
    env_path = os.getenv("AIFRED_DB_PATH")
    if env_path:
        return Path(env_path)

    alfred_dir = os.getenv("alfred_workflow_data")
    if alfred_dir:
        p = Path(alfred_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p / "aifred.db"

    return Path("aifred.db")


@dataclass
class Thread:
    id: int
    provider: str
    model: str
    name: Optional[str]
    created_at: str
    updated_at: str


@dataclass
class Message:
    id: int
    thread_id: int
    role: str
    content: str
    meta: Optional[str]
    created_at: str


class Store:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = Path(db_path) if db_path else _default_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS threads (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  provider TEXT NOT NULL,
                  model TEXT NOT NULL,
                  name TEXT,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  thread_id INTEGER NOT NULL,
                  role TEXT NOT NULL,
                  content TEXT NOT NULL,
                  meta JSON,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY(thread_id) REFERENCES threads(id)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id)"
            )
            conn.commit()

    # Thread API
    def create_thread(self, provider: str, model: str, name: Optional[str]) -> int:
        now = utcnow_iso()
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO threads(provider, model, name, created_at, updated_at) VALUES (?,?,?,?,?)",
                (provider, model, name, now, now),
            )
            conn.commit()
            return int(cur.lastrowid)

    def update_thread_name(self, thread_id: int, name: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE threads SET name = ?, updated_at = ? WHERE id = ?",
                (name, utcnow_iso(), thread_id),
            )
            conn.commit()

    def touch_thread(self, thread_id: int) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE threads SET updated_at = ? WHERE id = ?",
                (utcnow_iso(), thread_id),
            )
            conn.commit()

    def get_recent_threads(self, limit: int = 20) -> List[Thread]:
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT id, provider, model, name, created_at, updated_at FROM threads ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            )
            rows = cur.fetchall()
        return [Thread(*row) for row in rows]

    def get_thread(self, thread_id: int) -> Optional[Thread]:
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT id, provider, model, name, created_at, updated_at FROM threads WHERE id = ?",
                (thread_id,),
            )
            row = cur.fetchone()
        return Thread(*row) if row else None

    def get_latest_thread(self, provider: str, model: Optional[str] = None) -> Optional[Thread]:
        with self._conn() as conn:
            if model:
                cur = conn.execute(
                    "SELECT id, provider, model, name, created_at, updated_at FROM threads WHERE provider = ? AND model = ? ORDER BY updated_at DESC LIMIT 1",
                    (provider, model),
                )
            else:
                cur = conn.execute(
                    "SELECT id, provider, model, name, created_at, updated_at FROM threads WHERE provider = ? ORDER BY updated_at DESC LIMIT 1",
                    (provider,),
                )
            row = cur.fetchone()
        return Thread(*row) if row else None

    # Messages API
    def add_message(self, thread_id: int, role: str, content: str, meta: Optional[dict] = None) -> int:
        now = utcnow_iso()
        meta_json = json.dumps(meta) if meta is not None else None
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO messages(thread_id, role, content, meta, created_at) VALUES (?,?,?,?,?)",
                (thread_id, role, content, meta_json, now),
            )
            conn.execute(
                "UPDATE threads SET updated_at = ? WHERE id = ?",
                (now, thread_id),
            )
            conn.commit()
            return int(cur.lastrowid)

    def get_thread_messages(self, thread_id: int, limit: int = 50) -> List[Message]:
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT id, thread_id, role, content, meta, created_at FROM messages WHERE thread_id = ? ORDER BY id ASC",
                (thread_id,),
            )
            rows = cur.fetchall()
        msgs = [Message(*row) for row in rows]
        if limit and len(msgs) > limit:
            return msgs[-limit:]
        return msgs
