from fastapi import APIRouter, HTTPException, Body
from typing import Optional, Dict, Any
from datetime import datetime
import csv
import io
from .service import service
from .database import get_chat_history, save_chat_message, get_anomaly_event_by_id
from .ml_analyzer import ml_analyzer
from .statistical_baseline import statistical_baseline

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

# New endpoints for ML analysis

@router.get("/stats")
def get_statistical_stats():
    """Get current statistical baseline statistics"""
    return statistical_baseline.get_current_stats()

@router.get("/ml/algorithms")
def get_ml_algorithms():
    """Get available ML algorithms for analysis"""
    return ml_analyzer.get_available_algorithms()

@router.post("/ml/analyze")
def run_ml_analysis(
    algorithm: str = Body(default="isolation_forest"),
    window_size: int = Body(default=500),
    params: Optional[Dict[str, Any]] = Body(default=None)
):
    """
    Run ML-based anomaly analysis on recent historical data.
    This is an on-demand operation, not continuous.
    
    Args:
        algorithm: One of 'isolation_forest', 'one_class_svm', 'dbscan'
        window_size: Number of recent data points to analyze (default 500)
        params: Optional algorithm-specific parameters
    """
    # Get recent data from history
    if window_size <= 0:
        data_points = service.history
    else:
        data_points = service.history[-window_size:] if len(service.history) >= window_size else service.history
    
    if not data_points:
        raise HTTPException(status_code=400, detail="No historical data available for analysis")
    
    # Run analysis
    result = ml_analyzer.analyze(data_points, algorithm, params)
    
    if not result.get('success'):
        raise HTTPException(status_code=400, detail=result.get('error', 'Analysis failed'))
    
    return result

@router.get("/ml/last-analysis")
def get_last_ml_analysis():
    """Get the most recent ML analysis result"""
    result = ml_analyzer.get_last_analysis()
    if not result:
        raise HTTPException(status_code=404, detail="No ML analysis has been run yet")
    return result

# Data management endpoints

@router.get("/export/csv")
def export_history_csv():
    """Export historical data as CSV"""
    if not service.history:
        raise HTTPException(status_code=400, detail="No historical data to export")
    
    # Create CSV in memory
    output = io.StringIO()
    
    if service.history:
        # Get field names from first record
        fieldnames = list(service.history[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in service.history:
            # Convert anomalies dict to string for CSV
            row_copy = row.copy()
            if 'anomalies' in row_copy and isinstance(row_copy['anomalies'], dict):
                row_copy['anomalies'] = str(row_copy['anomalies'])
            if 'stats' in row_copy and isinstance(row_copy['stats'], dict):
                row_copy['stats'] = str(row_copy['stats'])
            writer.writerow(row_copy)
    
    csv_content = output.getvalue()
    
    return {
        "status": "success",
        "filename": f"wr-ai_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "data": csv_content,
        "rows_count": len(service.history),
        "message": f"Exported {len(service.history)} data points"
    }

@router.post("/clear-history")
def clear_history(confirm: bool = Body(default=False)):
    """
    Clear all historical data from memory.
    
    Args:
        confirm: Must be True to actually delete the data
    """
    if not confirm:
        return {
            "status": "warning",
            "message": "Confirm deletion by sending confirm=true",
            "data_count": len(service.history),
            "warning": "This will delete all historical monitoring data from memory"
        }
    
    try:
        rows_deleted = len(service.history)
        service.history.clear()
        
        # Reset statistical baseline
        from .statistical_baseline import StatisticalBaseline
        statistical_baseline.__dict__ = StatisticalBaseline().__dict__
        
        return {
            "status": "success",
            "message": f"Deleted {rows_deleted} data points from history",
            "data_deleted": rows_deleted,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")

@router.post("/clear-events")
def clear_events(confirm: bool = Body(default=False)):
    """
    Clear all anomaly events from memory (does not affect database).
    
    Args:
        confirm: Must be True to actually delete the data
    """
    if not confirm:
        return {
            "status": "warning",
            "message": "Confirm deletion by sending confirm=true",
            "events_count": len(service.events),
            "warning": "This will clear the event log from memory (database records remain intact)"
        }
    
    try:
        rows_deleted = len(service.events)
        service.events.clear()
        
        return {
            "status": "success",
            "message": f"Cleared {rows_deleted} anomaly events from memory",
            "events_deleted": rows_deleted,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear events: {str(e)}")