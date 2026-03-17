from fastapi import APIRouter
from modules.realtime.collector import collector
from modules.realtime.database import get_latest_events, get_latest_sample

router = APIRouter(
    prefix="/api",
    tags=["Foundation"]
)

@router.get("/status")
def get_status():
    status = collector.get_status()
    last = status.get("last_sample") or get_latest_sample() or {}
    # Keep fields used by frontend header; fall back to safe defaults.
    return {
        "state": "RUN" if status.get("connected") else "STOP",
        "recipe": "Realtime",
        "speed": 0,
        "produced": 0,
        "scrap": 0,
        "energy_kwh": last.get("energy_total_kwh") or 0,
        "oee_percent": 0,
        "timestamp": (last.get("timestamp") and __import__("datetime").datetime.fromtimestamp(last["timestamp"]).isoformat())
        or __import__("datetime").datetime.now().isoformat(),
        # Include raw realtime fields for convenience
        "realtime": status,
    }

@router.get("/metrics")
def get_metrics():
    # Deprecated: kept for frontend compatibility; use /api/realtime/stream instead.
    return {"history": []}

@router.get("/pareto")
def get_pareto():
    # Deprecated: kept for frontend compatibility.
    return []
