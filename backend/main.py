from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from modules.foundation.simulator import simulator
from modules.foundation.router import router as foundation_router
from modules.anomaly_detection.router import router as anomaly_router
from modules.guided_diagnosis.router import router as diagnosis_router

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(foundation_router)
app.include_router(anomaly_router)
app.include_router(diagnosis_router)

from modules.anomaly_detection.service import service as anomaly_service

@app.on_event("startup")
async def startup_event():
    # Start simulation loop in background
    asyncio.create_task(run_simulation())
    # Start Anomaly Service Loop
    asyncio.create_task(anomaly_service.start_loop())

async def run_simulation():
    while True:
        simulator.update()
        await asyncio.sleep(1)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

