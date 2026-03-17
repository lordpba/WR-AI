@echo off
setlocal enabledelayedexpansion

echo ===========================================
echo    WR-AI Setup (Windows)
echo ===========================================

REM Basic checks
where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python not found. Install Python 3.10+ and ensure "python" is in PATH.
  exit /b 1
)

where node >nul 2>nul
if errorlevel 1 (
  echo ERROR: Node.js not found. Install Node.js 18+ and ensure "node" is in PATH.
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo ERROR: npm not found. Reinstall Node.js (includes npm).
  exit /b 1
)

echo OK: Python and Node.js found.

REM Backend setup
echo.
echo --- Backend setup ---
pushd backend
IF NOT EXIST ".env" (
  echo Creating backend\.env from .env.example...
  copy /Y ".env.example" ".env" >nul
  echo NOTE: Update backend\.env for Ollama/Gemini and acquisition settings later.
)
IF NOT EXIST "venv" (
  echo Creating Python venv...
  python -m venv venv
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
popd

REM Frontend setup
echo.
echo --- Frontend setup ---
pushd frontend
IF NOT EXIST ".env" (
  echo Creating frontend\.env...
  > .env echo VITE_API_URL=http://localhost:8000
)
IF NOT EXIST "node_modules" (
  echo Installing frontend dependencies...
  npm install
)
popd

echo.
echo Setup complete.
echo Next:
echo   1) Run start.bat
echo   2) Open http://localhost:5173
echo.

endlocal

