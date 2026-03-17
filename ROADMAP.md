# WR-AI Project Roadmap & Modules

The WR-AI system is designed as an "intelligent layer" that evolves through 10 progressive modules.
Below is the detail of the planned modules.

---

## ✅ Roadmap (Implemented in this POC)

### ✅ Module 1: OEE + Energy Dashboard (Foundation) - COMPLETED
**Objective**: Operational measurement and transparency.
- Real-time dashboard (React).
- OEE calculation (Availability, Performance, Quality).
- Energy trend monitoring (kW).
- Pareto analysis of downtime causes.

### ✅ Module 2: Anomaly Detection (Early Warning) - COMPLETED
**Objective**: Intercept mechanical/process drifts before failure.
- ML algorithms on signals (currents, temperature) -> **Implemented: Isolation Forest**.
- Alerts with severity and trend -> **Implemented: Real-time Risk Score**.
- Historical charts with clickable anomalies (no WebSocket needed for POC).
- Vibration/Temperature monitoring simulated via "Serial Port Adapter".

### ✅ Module 3: Guided Diagnostics - COMPLETED
**Objective**: Reduce MTTR and standardize troubleshooting.
- **LLM Integration**: Support for Local (Ollama) and Remote (Gemini) models.
- **RAG System**: Ingestion of Machine Manuals for context-aware answers.
- **Anomaly Context**: Automatic injection of detected anomalies into the prompt.
- **Persisted Chats**: Each anomaly has its own saved chat history in SQLite.
- Interactive Chat Interface for operators.

### ✅ Platform Improvements (Completed)
- Logging-first backend (replaced prints), lifespan startup, and graceful background tasks.
- SQLite persistence for anomaly events and chat history.
- Environment-driven LLM configuration via `.env` sample.
- Frontend Error Boundary to keep the UI responsive on runtime errors.

### ✅ Recent Implementation Updates (Thermoformatrice / Industrial PanelPC direction)
- **Offline import in Anomaly dashboard**: upload `.xlsx` (e.g. `dati_test/Termoformatrice4.xlsx`) and analyze signals (V/A/cosφ/kWh) with computed `power_kw`.
- **Statistical baseline upgraded**: dynamic multi-signal baseline (supports arbitrary signal keys, not only temp/vibration/power).
- **Realtime vs Analysis separation**:
  - New **Realtime** page focused on rule-based alerts and connection status.
  - **Anomaly Detection** supports historical interval loading via `GET /api/anomaly/history` and keeps XLSX upload as alternative data source.
- **Realtime backend plumbing (prepared for PLC)**:
  - Modbus TCP collector + SQLite time-series/events (`backend/modules/realtime/`).
  - Rule-based realtime alerts (range/low PF/high current/stuck signals).
- **Global Settings (backend-shared)**:
  - Ollama remote base URL + model selection with model discovery (backend proxy).
  - Added “Data acquisition” settings section (prepared; to be wired to real PLC source once available).

## 📅 Module 4: Predictive Maintenance
**Objective**: Estimate failure risk and remaining useful life (RUL).
- Integration of maintenance history.
- Prediction of optimal intervention windows.
- Proactive spare parts management.

## 📅 Module 5: Advanced Energy Analytics
**Objective**: Identify waste and energy "signature".
- Consumption analysis per phase/recipe.
- Alerts on anomalous consumption (e.g., excessive standby).
- Eco-mode suggestions.

## 📅 Module 6: Computer Vision (Quality)
**Objective**: Automatic quality control.
- Recognition of visual defects (deformations, assembly errors).
- Correlation of defects with process parameters.
- Scrap and rework reduction.

## 📅 Module 7: Auto-tuning Setpoint (Human-in-the-loop)
**Objective**: Process parameter optimization.
- AI proposes setpoint adjustments (A/B testing).
- Focus on Quality/Energy/Throughput trade-offs.
- Final operator approval.

## 📅 Module 8: Conversational Copilot (RAG LLM)
**Objective**: Virtual assistant for manuals and diagnostics.
- Chatbot trained on technical manuals and machine logs.
- Immediate Q&A for operators.
- Source citation and safety procedures.

## 📅 Module 9: Lot Scheduling & Changeover
**Objective**: Production sequence optimization.
- Minimization of format changeover times.
- Alternative plans (A/B) based on constraints and priorities.
- Lead time reduction.

## 📅 Module 10: Simulative Digital Twin
**Objective**: "What-if" simulation offline.
- Virtual model (Twin) of the production line.
- Strategy testing (speed, maintenance) without real-world risks.
- Multi-KPI optimization.

---

## 🛠 Plan Improvements (Next actions)

### Data acquisition (PanelPC / PLC)
- **Auto-detect source**: implement a device manager that can switch from `WAITING_DEVICE` to `CONNECTED` when a USB/serial device appears.
- **Serial “raw preview”**: endpoint + UI to show the first received lines to quickly identify the PLC/gateway output format.
- **Source adapters**:
  - serial line protocol (CSV/JSON per line)
  - Modbus RTU (serial) as alternative to Modbus TCP (if required)
- **Config wiring**: make realtime collector read `source_type` and choose the correct adapter (today it’s prepared but mainly Modbus TCP-oriented).

### Anomaly analysis (historical)
- **Persist historical anomaly results** (optional): store analysis runs linked to interval and parameters.
- **Clear semantics**:
  - clear UI state vs clear in-memory session vs clear persisted DB records (separate buttons with explicit confirmations).
- **Better interval UX**: presets (last 1h/6h/24h), validation, timezone handling.

### LLM / Guided Diagnosis
- **Unify settings**: Guided Diagnosis uses global backend config only (already done), add UI hints/link to Settings.
- **Diagnostics context**: enrich anomaly context with interval summary (min/max/avg and detected events) when analyzing historical windows.
