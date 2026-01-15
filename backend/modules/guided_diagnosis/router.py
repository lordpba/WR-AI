import logging
from fastapi import APIRouter, HTTPException
from .service import service
from .model import ManualUpdate, DiagnosisRequest
from modules.anomaly_detection.database import save_chat_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/diagnosis", tags=["guided_diagnosis"])

@router.get("/manual")
async def get_manual():
    return {"text": service.get_manual()}

@router.post("/manual")
async def update_manual(update: ManualUpdate):
    return service.update_manual(update.text)

@router.post("/analyze")
async def diagnose(request: DiagnosisRequest):
    logger.info(f"Diagnosis request for anomaly_id={request.anomaly_id}")
    
    result = service.diagnose(
        request.anomaly_context, 
        request.query, 
        request.provider, 
        request.config
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    # Save chat messages to database if anomaly_id is provided
    if request.anomaly_id:
        try:
            # Save user query
            save_chat_message(request.anomaly_id, "user", request.query)
            # Save assistant response
            save_chat_message(request.anomaly_id, "assistant", result.get("response", ""))
            logger.info(f"Chat saved for anomaly {request.anomaly_id}")
        except Exception as e:
            logger.warning(f"Failed to save chat for anomaly {request.anomaly_id}: {e}")
    
    return result
