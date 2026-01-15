from pydantic import BaseModel
from typing import Optional, Dict, Any

class ManualUpdate(BaseModel):
    text: str

class DiagnosisRequest(BaseModel):
    query: str
    anomaly_context: Optional[Dict[str, Any]] = None
    anomaly_id: Optional[int] = None  # For linking chat to specific anomaly
    provider: str  # "ollama" or "gemini"
    config: Optional[Dict[str, Any]] = {} 
    # config can contain apiKey for Gemini, or url/model for Ollama
