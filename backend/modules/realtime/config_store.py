from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "realtime_config.db"


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS realtime_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        conn.commit()
        logger.info(f"Realtime config DB initialized at {DB_PATH}")


def get_config() -> Dict[str, Any]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT key, value FROM realtime_config")
        out: Dict[str, Any] = {}
        for row in cur.fetchall():
            k = row["key"]
            v = row["value"]
            try:
                out[k] = json.loads(v)
            except Exception:
                out[k] = v
        return out


def set_config(values: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(values, dict):
        raise ValueError("values must be an object")
    with get_db_connection() as conn:
        cur = conn.cursor()
        for k, v in values.items():
            cur.execute(
                "INSERT INTO realtime_config(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(k), json.dumps(v)),
            )
        conn.commit()
    return get_config()

