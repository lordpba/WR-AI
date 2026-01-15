from pydantic import BaseModel
from typing import Optional, Dict, Any

class ManualUpdate(BaseModel):
    text: str

class DiagnosisRequest(BaseModel):
    query: str
    anomaly_context: Optional[Dict[str, Any]] = None
    provider: str # "ollama" or "gemini"
    config: Optional[Dict[str, Any]] = {} 
    # config can contain apiKey for Gemini, or url/model for Ollama
