#!/bin/bash

# Function to ensure background processes are killed when this script exits
trap 'kill $(jobs -p) 2>/dev/null' EXIT

echo "==========================================="
echo "   🚀 WR-AI POC Launcher"
echo "==========================================="

# Start Backend
echo "📡 Starting Backend (Python/FastAPI)..."
cd backend
# Check if venv exists, if not warn (but assume user followed setup)
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found in backend/venv. Please run setup first."
    exit 1
fi
source venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready (simple sleep)
sleep 2

# Start Frontend
echo "💻 Starting Frontend (React/Vite)..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules not found. Running npm install..."
    npm install
fi

echo "👉 Dashboard will be available at http://localhost:5173"
echo "Press Ctrl+C to stop servers."
echo "==========================================="

npm run dev

# Wait for background processes
wait
