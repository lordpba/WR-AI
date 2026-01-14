from fastapi import APIRouter
from .simulator import simulator

router = APIRouter(
    prefix="/api",
    tags=["Foundation"]
)

@router.get("/status")
def get_status():
    return simulator.get_status()

@router.get("/metrics")
def get_metrics():
    # Return last 60 seconds for live charts
    data = simulator.history[-60:] if len(simulator.history) > 60 else simulator.history
    return {
        "history": data
    }

@router.get("/pareto")
def get_pareto():
    return simulator.get_pareto_data()
