from fastapi import APIRouter, HTTPException
from typing import Optional
from .service import service
from .database import get_chat_history, save_chat_message, get_anomaly_event_by_id

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

@router.get("/events/{event_id}")
def get_event_by_id(event_id: int):
    """Get a specific anomaly event by ID"""
    event = get_anomaly_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.get("/events/{event_id}/chat")
def get_event_chat(event_id: int):
    """Get chat history for a specific anomaly event"""
    # Verify event exists
    event = get_anomaly_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    chat_history = get_chat_history(event_id)
    return {"anomaly_id": event_id, "messages": chat_history}

@router.post("/events/{event_id}/chat")
def add_chat_message(event_id: int, role: str, content: str):
    """Add a chat message to an anomaly event's history"""
    # Verify event exists
    event = get_anomaly_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    msg_id = save_chat_message(event_id, role, content)
    return {"message_id": msg_id, "status": "saved"}
