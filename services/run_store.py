import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DB_PATH = Path("data/runs.db")


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                mode TEXT NOT NULL,
                status TEXT NOT NULL,
                result_json TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
            """
        )


def create_run(mode: str) -> str:
    _init_db()
    run_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO runs (id, mode, status, created_at) VALUES (?, ?, ?, ?)",
            (run_id, mode, "running", now),
        )
    return run_id


def complete_run(run_id: str, status: str, result: dict[str, Any]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            UPDATE runs
            SET status = ?, result_json = ?, completed_at = ?
            WHERE id = ?
            """,
            (status, json.dumps(result), now, run_id),
        )


def list_runs(limit: int = 20) -> list[dict[str, Any]]:
    _init_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, mode, status, result_json, created_at, completed_at
            FROM runs
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def get_run(run_id: str) -> dict[str, Any] | None:
    _init_db()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id, mode, status, result_json, created_at, completed_at
            FROM runs WHERE id = ?
            """,
            (run_id,),
        ).fetchone()
    return _row_to_dict(row) if row else None


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    result = {
        "id": row["id"],
        "mode": row["mode"],
        "status": row["status"],
        "created_at": row["created_at"],
        "completed_at": row["completed_at"],
    }
    if row["result_json"]:
        result["result"] = json.loads(row["result_json"])
    return result
