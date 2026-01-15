from fastapi import APIRouter
from .service import service

router = APIRouter(
    prefix="/api/anomaly",
    tags=["Anomaly Detection"]
)

@router.get("/status")
def get_anomaly_status():
    last_reading = service.history[-1] if service.history else None
    return {
        "status": last_reading['status'] if last_reading else "calibrating",
        "active_models": 1, 
        "model_ready": last_reading['model_ready'] if last_reading else False,
        "last_reading": last_reading
    }

@router.get("/stream")
def get_stream(limit: int = 60):
    # Return last 'limit' points for charts. If limit is 0 or negative, return all.
    if limit <= 0:
        return service.history
    return service.history[-limit:]

@router.get("/events")
def get_events():
    return service.events
