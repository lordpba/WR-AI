#!/bin/bash

# Function to ensure background processes are killed when this script exits
trap 'kill $(jobs -p) 2>/dev/null' EXIT

echo "==========================================="
echo "   🚀 WR-AI POC Launcher"
echo "==========================================="

# Start Backend
echo "📡 Starting Backend (Python/FastAPI)..."
cd backend
# Check if .env exists, if not create it
if [ ! -f ".env" ]; then
    echo "ℹ️  .env file not found. Creating default .env..."
    cat > .env << 'EOF'
# Backend Configuration
DATABASE_URL=sqlite:///./test.db
DEBUG=true
EOF
fi
# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "ℹ️  Virtual environment not found. Creating venv..."
    python3 -m venv venv
    source venv/bin/activate
else
    source venv/bin/activate
fi

echo "📦 Checking and installing dependencies..."
pip install -r requirements.txt

# Always install/update dependencies
echo "📦 Checking/Installing dependencies..."
pip install -r requirements.txt

uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready (simple sleep)
sleep 2

# Start Frontend
echo "💻 Starting Frontend (React/Vite)..."
cd frontend
# Check if .env exists, if not create it
if [ ! -f ".env" ]; then
    echo "ℹ️  .env file not found. Creating default .env..."
    cat > .env << 'EOF'
# Frontend Configuration
VITE_API_URL=http://localhost:8000
EOF
fi
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
