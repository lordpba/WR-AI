# WR-AI Project Roadmap & Modules

The WR-AI system is designed as an "intelligent layer" that evolves through 10 progressive modules.
Below is the detail of the planned modules.

---

## ✅ Module 1: OEE + Energy Dashboard (Foundation) - COMPLETED
**Objective**: Operational measurement and transparency.
- Real-time dashboard (React).
- OEE calculation (Availability, Performance, Quality).
- Energy trend monitoring (kW).
- Pareto analysis of downtime causes.

## ✅ Module 2: Anomaly Detection (Early Warning) - COMPLETED
**Objective**: Intercept mechanical/process drifts before failure.
- ML algorithms on signals (currents, temperature) -> **Implemented: Isolation Forest**.
- Alerts with severity and trend -> **Implemented: Real-time Risk Score**.
- Historical charts with clickable anomalies (no WebSocket needed for POC).
- Vibration/Temperature monitoring simulated via "Serial Port Adapter".

## ✅ Module 3: Guided Diagnostics - COMPLETED
**Objective**: Reduce MTTR and standardize troubleshooting.
- **LLM Integration**: Support for Local (Ollama) and Remote (Gemini) models.
- **RAG System**: Ingestion of Machine Manuals for context-aware answers.
- **Anomaly Context**: Automatic injection of detected anomalies into the prompt.
- **Persisted Chats**: Each anomaly has its own saved chat history in SQLite.
- Interactive Chat Interface for operators.

## ✅ Platform Improvements
- Logging-first backend (replaced prints), lifespan startup, and graceful background tasks.
- SQLite persistence for anomaly events and chat history.
- Environment-driven LLM configuration via `.env` sample.
- Frontend Error Boundary to keep the UI responsive on runtime errors.

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
