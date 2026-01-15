# WR-AI: Industrial AI Integration POC

![WR-AI Dashboard](WR-AI.png)

**WR-AI** is an intelligent "smart layer" designed to monitor, diagnose, and optimize industrial machines. The POC now delivers three working modules end-to-end: OEE foundation, AI anomaly detection (historical view), and guided diagnosis with per-anomaly chat memory.

## 🎥 Demo Video
Watch the interface in action:

[![WR-AI Interface Demo](https://img.youtube.com/vi/FvLEpaICaD8/0.jpg)](https://youtu.be/FvLEpaICaD8)

## 🚀 What’s Included Today
- **Module 1 – Foundation & OEE**: Real-time machine status, OEE (Availability/Performance/Quality), energy analytics, Pareto of downtime causes.
- **Module 2 – Anomaly Detection**: 
  - **Real-time Statistical Baseline**: Lightweight monitoring with rolling statistics (mean, std, min/max) and visual bands on charts
  - **On-Demand ML Analysis**: Choice of algorithms (Isolation Forest, One-Class SVM, DBSCAN) for deeper batch analysis
  - **Flexible Detection**: Statistical thresholds for continuous monitoring, ML models for scheduled or manual deep analysis
  - Historical charts with clickable anomaly markers and debounced alerts
- **Module 3 – Guided Diagnosis (LLM)**: Dual LLM (Ollama default, Gemini optional), manual/RAG context, anomaly context injection, chat UI, and per-anomaly chat history saved to SQLite.

## 🛠 Architecture & Stack
- **Backend**: FastAPI, modular (foundation, anomaly_detection, guided_diagnosis), statistical baseline + multiple ML algorithms (Isolation Forest, One-Class SVM, DBSCAN), logging, SQLite persistence at [backend/modules/anomaly_detection/anomaly_data.db](backend/modules/anomaly_detection/anomaly_data.db).
- **Frontend**: React (Vite), Recharts with statistical bands visualization, Lucide icons, Error Boundary wrapper for crash-safe UI.
- **Config**: Environment variables via [backend/.env.example](backend/.env.example); default LLM provider is Ollama (`OLLAMA_MODEL=llama3.1:latest`).

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) Ollama running locally for default LLM

### Quick Start
```bash
chmod +x start.sh
./start.sh
```
This will set up the Python venv, install backend/frontend deps, run FastAPI on http://localhost:8000 and Vite on http://localhost:5173.

### Configuration
1) Copy the sample env: `cp backend/.env.example backend/.env`
2) Set `LLM_PROVIDER` to `ollama` (local) or `gemini` (cloud). For Gemini, add your `GEMINI_API_KEY`.
3) Optional thresholds and loop intervals can be tuned in `.env`.

## 🧭 Using the POC
- **Monitor**: Foundation dashboard shows live OEE, power, and Pareto data.
- **Detect**: 
  - Anomaly dashboard shows real-time statistical monitoring with visual bands (mean ± 2.5σ)
  - Statistical anomalies are automatically flagged and shown as red markers on charts
  - Click "ML Analysis" button to run deeper analysis with selectable algorithms
  - Red points or event rows are clickable to open diagnosis
- **Diagnose**: Guided Diagnosis chat auto-injects anomaly context; chats are persisted per anomaly and retrievable via `/api/anomaly/events/{id}/chat`.

## 🔌 Key APIs
- `GET /api/anomaly/events` – latest anomalies (persisted to SQLite)
- `GET /api/anomaly/events/{id}` – single anomaly with details
- `GET /api/anomaly/events/{id}/chat` – chat history for an anomaly
- `POST /api/anomaly/events/{id}/chat` – append chat message (role, content)
- `GET /api/anomaly/stats` – current statistical baseline statistics (mean, std, bounds)
- `GET /api/anomaly/ml/algorithms` – available ML algorithms with descriptions
- `POST /api/anomaly/ml/analyze` – run on-demand ML analysis (algorithm, window_size, params)
- `GET /api/anomaly/ml/last-analysis` – get most recent ML analysis result
- `POST /api/diagnosis/analyze` – run LLM diagnosis (supports `anomaly_id` to store chat)

## 🔮 Future Roadmap
See [ROADMAP.md](ROADMAP.md) for the planned evolution (Predictive Maintenance, Energy Analytics, CV Quality, Auto-tuning, Digital Twin, etc.).
