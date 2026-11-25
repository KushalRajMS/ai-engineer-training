import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from ai_training.settings import get_settings

def _db_path() -> str:
    return get_settings().audit_db_path

def _connect():
    path= Path(_db_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            session_id TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            args TEXT NOT NULL,
            result TEXT NOT NULL,
            success INTEGER NOT NULL
        )"""
    )
    return conn

def record(session_id: str, tool_name: str, args: dict, result: dict) -> None:
    with closing(_connect()) as conn:
        conn.execute(
            "INSERT INTO audit (ts, session_id, tool_name, args, result, success) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                datetime.now(timezone.utc).isoformat(),
                session_id,
                tool_name,
                json.dumps(args, default=str),
                json.dumps(result.get("result"), default=str),
                1 if result.get("success") else 0,
            ),
        )
        conn.commit()

def get_log(limit: int = 50) -> list[dict]:
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT * FROM audit ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]