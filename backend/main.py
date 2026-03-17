import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from modules.foundation.router import router as foundation_router
from modules.anomaly_detection.router import router as anomaly_router
from modules.guided_diagnosis.router import router as diagnosis_router
from modules.guided_diagnosis.config_router import router as llm_config_router
from modules.anomaly_detection.database import init_database
from modules.realtime.database import init_database as init_realtime_db
from modules.realtime.collector import collector
from modules.realtime.router import router as realtime_router
from modules.realtime.config_store import init_db as init_realtime_config_db
from modules.realtime.config_router import router as realtime_config_router
from modules.guided_diagnosis.config_store import init_db as init_llm_config_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown"""
    # Startup
    logger.info("🚀 WR-AI Backend Starting...")
    
    # Initialize database
    init_database()
    init_realtime_db()
    init_llm_config_db()
    init_realtime_config_db()
    logger.info("📦 Database initialized")
    
    # Start background tasks
    collector_task = await collector.start()
    logger.info("✅ All services started")
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("🛑 WR-AI Backend Shutting down...")
    # Ensure collector loop is stopped and connections closed
    await collector.stop()

app = FastAPI(lifespan=lifespan)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(foundation_router)
app.include_router(anomaly_router)
app.include_router(diagnosis_router)
app.include_router(realtime_router)
app.include_router(llm_config_router)
app.include_router(realtime_config_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

