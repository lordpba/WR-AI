from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from simulator import PLCSimulator

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

simulator = PLCSimulator()

@app.on_event("startup")
async def startup_event():
    # Start simulation loop in background
    asyncio.create_task(run_simulation())

async def run_simulation():
    while True:
        simulator.update()
        await asyncio.sleep(1)

@app.get("/api/status")
def get_status():
    return simulator.get_status()

@app.get("/api/metrics")
def get_metrics():
    # Return last 60 seconds for live charts
    data = simulator.history[-60:] if len(simulator.history) > 60 else simulator.history
    return {
        "history": data
    }

@app.get("/api/pareto")
def get_pareto():
    return simulator.get_pareto_data()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
