@echo off
setlocal enabledelayedexpansion

echo ===========================================
echo    WR-AI POC Launcher (Windows)
echo ===========================================

REM --- Backend ---
echo Starting Backend (FastAPI)...
pushd backend

IF NOT EXIST ".env" (
  echo .env not found. Creating backend\.env from .env.example...
  copy /Y ".env.example" ".env" >nul
)

IF NOT EXIST "venv" (
  echo Creating Python venv...
  python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Start backend in a new window (keeps logs visible)
start "WR-AI Backend" cmd /k "cd /d %CD% && venv\Scripts\activate.bat && uvicorn main:app --reload --port 8000"
popd

REM --- Frontend ---
echo Starting Frontend (Vite)...
pushd frontend

IF NOT EXIST ".env" (
  echo .env not found. Creating frontend\.env...
  > .env echo VITE_API_URL=http://localhost:8000
)

IF NOT EXIST "node_modules" (
  echo node_modules not found. Running npm install...
  npm install
)

start "WR-AI Frontend" cmd /k "cd /d %CD% && npm run dev"
popd

echo.
echo Dashboard: http://localhost:5173
echo Backend:   http://localhost:8000
echo.
echo Close the two opened terminal windows to stop.

endlocal

