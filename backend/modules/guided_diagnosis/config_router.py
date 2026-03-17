import logging
import os
from fastapi import APIRouter, HTTPException, Body, Query
import requests

from .config_store import get_config, set_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/llm", tags=["llm_config"])


@router.get("/config")
def read_config():
    cfg = get_config()
    # Provide defaults if not set yet
    cfg.setdefault("ollama_base_url", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    cfg.setdefault("ollama_model", os.getenv("OLLAMA_MODEL", "llama3.1:latest"))
    cfg.setdefault("llm_provider", os.getenv("LLM_PROVIDER", "ollama"))
    cfg.setdefault("gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
    cfg.setdefault("gemini_model", os.getenv("GEMINI_MODEL", "gemini-1.5-pro"))
    return cfg


@router.post("/config")
def write_config(values: dict = Body(default={})):
    try:
        allowed = {}
        for k in ("ollama_base_url", "ollama_model", "llm_provider", "gemini_api_key", "gemini_model"):
            if k in values:
                allowed[k] = values[k]
        cfg = set_config(allowed)
        return {"status": "success", "config": cfg}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ollama/models")
def list_ollama_models(base_url: str = Query(default="")):
    cfg = read_config()
    base_url = (base_url or "").strip() or str(cfg.get("ollama_base_url") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    base_url = base_url.rstrip("/")
    url = f"{base_url}/api/tags"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        models = [m.get("name") for m in (data.get("models") or []) if m.get("name")]
        return {"base_url": base_url, "models": models}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch Ollama models from {base_url}: {e}")

