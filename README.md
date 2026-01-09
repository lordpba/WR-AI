# WR-AI: Industrial AI Integration POC

**WR-AI** is an intelligent "smart layer" designed to monitor, diagnose, and optimize industrial machines. This project serves as a Proof of Concept (POC) demonstrating the core capabilities of data acquisition, OEE monitoring, and energy analysis.

## 🚀 Project Overview

The system transforms raw machine data (simulated for this POC) into actionable operational decisions, focusing on sustainability (energy reduction) and efficiency (OEE maximization).

### Current Module: Dashboard & Foundation
- **Real-time Monitoring**: Visualization of machine state, speed, and production data.
- **OEE Calculation**: Instant efficiency metrics (Availability, Performance, Quality).
- **Energy Analytics**: Live power consumption monitoring (kW).
- **Pareto Analysis**: Identification of top downtime causes.

## 🛠 Tech Stack

- **Backend**: Python (FastAPI) - Simulates PLC logic and serves API endpoints.
- **Frontend**: React (Vite) + Recharts - "Premium" dark-mode dashboard for visualization.

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+

### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The dashboard will be available at `http://localhost:5173`.

## 🔮 Future Roadmap

See [ROADMAP.md](./ROADMAP.md) for the detailed list of future AI modules (Anomaly Detection, Predictive Maintenance, Computer Vision, etc.).
