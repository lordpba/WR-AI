## Setup guide (Linux / Windows)

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- (Optional) **Ollama** if you want local LLM (`http://localhost:11434`)

---

## Windows

### 1) One-time setup
- Run `setup.bat`

This will:
- create `backend\.env` from `backend\.env.example` (if missing)
- create Python venv in `backend\venv` and install dependencies
- create `frontend\.env` (if missing) and install npm dependencies

### 2) Run
- Run `start.bat`

It opens 2 terminal windows:
- Backend (FastAPI): `http://localhost:8000`
- Frontend (Vite): `http://localhost:5173`

Stop by closing the two windows.

---

## Linux

### 1) One-time setup
```bash
cp backend/.env.example backend/.env
```

### 2) Run
```bash
chmod +x start.sh
./start.sh
```

---

## Configuration (recommended)

### LLM
- In the UI go to **Settings**:
  - **Ollama base URL**: `http://<ollama-ip>:11434` (can be remote)
  - **Ollama model**: select installed model
  - Or switch to **Gemini** and set API key + model

### Data acquisition (PanelPC / PLC)
- In the UI go to **Settings → Data acquisition**
- For now, keep `None / Waiting device` until you know the PLC protocol/format.

