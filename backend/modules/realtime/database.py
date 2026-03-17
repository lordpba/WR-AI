"""
SQLite persistence for realtime samples and rule-based events.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "realtime_data.db"


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS realtime_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_realtime_samples_ts
            ON realtime_samples(timestamp)
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS realtime_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                type TEXT NOT NULL,
                message TEXT,
                details TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_realtime_events_ts
            ON realtime_events(timestamp)
            """
        )
        conn.commit()
        logger.info(f"Realtime database initialized at {DB_PATH}")


def save_sample(timestamp: float, payload: Dict[str, Any]) -> int:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO realtime_samples (timestamp, payload) VALUES (?, ?)",
            (timestamp, json.dumps(payload)),
        )
        conn.commit()
        return int(cur.lastrowid)


def save_event(timestamp: float, event_type: str, message: str, details: Optional[Dict[str, Any]] = None) -> int:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO realtime_events (timestamp, type, message, details) VALUES (?, ?, ?, ?)",
            (timestamp, event_type, message, json.dumps(details or {})),
        )
        conn.commit()
        return int(cur.lastrowid)


def get_samples_between(ts_from: float, ts_to: float, limit: int = 50_000) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT timestamp, payload
            FROM realtime_samples
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp ASC
            LIMIT ?
            """,
            (ts_from, ts_to, limit),
        )
        out: List[Dict[str, Any]] = []
        for row in cur.fetchall():
            payload = json.loads(row["payload"]) if row["payload"] else {}
            payload["timestamp"] = row["timestamp"]
            out.append(payload)
        return out


def get_latest_sample() -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT timestamp, payload
            FROM realtime_samples
            ORDER BY timestamp DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        if not row:
            return None
        payload = json.loads(row["payload"]) if row["payload"] else {}
        payload["timestamp"] = row["timestamp"]
        return payload


def get_latest_events(limit: int = 100) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, timestamp, type, message, details
            FROM realtime_events
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        )
        out: List[Dict[str, Any]] = []
        for row in cur.fetchall():
            out.append(
                {
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "type": row["type"],
                    "message": row["message"],
                    "details": json.loads(row["details"]) if row["details"] else {},
                }
            )
        return out


def clear_samples(confirm: bool) -> int:
    if not confirm:
        return 0
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM realtime_samples")
        conn.commit()
        return int(cur.rowcount)


def clear_events(confirm: bool) -> int:
    if not confirm:
        return 0
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM realtime_events")
        conn.commit()
        return int(cur.rowcount)

