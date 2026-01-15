from fastapi import APIRouter, HTTPException
from .service import service
from .model import ManualUpdate, DiagnosisRequest

router = APIRouter(prefix="/api/diagnosis", tags=["guided_diagnosis"])

@router.get("/manual")
async def get_manual():
    return {"text": service.get_manual()}

@router.post("/manual")
async def update_manual(update: ManualUpdate):
    return service.update_manual(update.text)

@router.post("/analyze")
async def diagnose(request: DiagnosisRequest):
    result = service.diagnose(
        request.anomaly_context, 
        request.query, 
        request.provider, 
        request.config
    )
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
