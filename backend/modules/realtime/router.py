from fastapi import APIRouter, Body, HTTPException
from typing import Optional
import time

from .collector import collector
from .database import get_latest_events, get_samples_between, clear_events, clear_samples


router = APIRouter(prefix="/api/realtime", tags=["Realtime"])


@router.get("/status")
def get_status():
    return collector.get_status()


@router.get("/stream")
def get_stream(seconds: int = 60, limit: int = 5000):
    now = time.time()
    seconds = max(1, min(int(seconds), 24 * 3600))
    limit = max(1, min(int(limit), 50_000))
    return get_samples_between(now - seconds, now, limit=limit)


@router.get("/events")
def get_events(limit: int = 100):
    limit = max(1, min(int(limit), 500))
    return get_latest_events(limit=limit)


@router.post("/clear")
def clear(scope: str = Body(default="ui"), confirm: bool = Body(default=False)):
    """
    scope=ui: no-op (frontend clears its own state)
    scope=db: clear realtime SQLite tables (confirm required)
    """
    scope = (scope or "ui").strip().lower()
    if scope == "ui":
        return {"status": "success", "scope": "ui", "message": "UI can clear local state; acquisition continues."}
    if scope != "db":
        raise HTTPException(status_code=400, detail="scope must be 'ui' or 'db'")
    deleted_samples = clear_samples(confirm=confirm)
    deleted_events = clear_events(confirm=confirm)
    return {"status": "success", "scope": "db", "deleted_samples": deleted_samples, "deleted_events": deleted_events}

