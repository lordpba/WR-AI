# WR-AI Project Roadmap & Modules

Il sistema WR-AI è concepito come un "layer intelligente" che evolve attraverso 10 moduli progressivi.
Di seguito il dettaglio dei moduli pianificati.

---

## ✅ Modulo 1: Dashboard OEE + Energia (Foundation) - COMPLETATO
**Obiettivo**: Misurazione e trasparenza operativa.
- Dashboard real-time (React).
- Calcolo OEE (Availability, Performance, Quality).
- Monitoraggio trend energetici (kW).
- Analisi Pareto cause fermo.

## ✅ Modulo 2: Anomaly Detection (Early Warning) - COMPLETATO
**Obiettivo**: Intercettare derive meccaniche/processo prima del guasto.
- Algoritmi ML su segnali (correnti, temp) -> **Implemented: Isolation Forest**.
- Alert con severità e trend -> **Implemented: Real-time Risk Score**.
- Monitoraggio Vibrazioni/Temperatura simulate via "Serial Port Adapter".

## 📅 Modulo 3: Diagnosi Guidata
**Obiettivo**: Ridurre MTTR e standardizzare il troubleshooting.
- Sistema Rule-based + Knowledge Base.
- Checklist contestuali per ogni codice allarme.
- Supporto operatori junior.

## 📅 Modulo 4: Manutenzione Predittiva
**Obiettivo**: Stima rischio guasto e vita residua (RUL).
- Integrazione storico manutenzioni.
- Previsione finestre di intervento ottimali.
- Gestione proattiva ricambi.

## 📅 Modulo 5: Energy Analytics Avanzato
**Obiettivo**: Identificazione sprechi e "Signature" energetica.
- Analisi consumo per fase/ricetta.
- Alert su consumi anomali (es. stand-by eccessivo).
- Suggerimenti modalità Eco.

## 📅 Modulo 6: Computer Vision (Quality)
**Obiettivo**: Controllo qualità automatico.
- Riconoscimento difetti visivi (deformazioni, errori assemblaggio).
- Correlazione difetti-parametri processo.
- Riduzione scarti e rilavorazioni.

## 📅 Modulo 7: Auto-tuning Setpoint (Human-in-the-loop)
**Obiettivo**: Ottimizzazione parametri di processo.
- L'AI propone aggiustamenti ai setpoint (A/B testing).
- Focus su trade-off Qualità/Energia/Throughput.
- Approvazione finale operatore.

## 📅 Modulo 8: Copilota Conversazionale (RAG LLM)
**Obiettivo**: Assistente virtuale per manualistica e diagnosi.
- Chatbot addestrato su manuali tecnici e log macchina.
- Q&A immediato per operatori.
- Citazione fonti e procedure di sicurezza.

## 📅 Modulo 9: Scheduling Lotti & Changeover
**Obiettivo**: Ottimizzazione sequenza produzione.
- Minimizzazione tempi di cambio formato (Changeover)
- Piani alternativi (A/B) basati su vincoli e priorità.
- Riduzione lead time.

## 📅 Modulo 10: Digital Twin Simulativo
**Obiettivo**: Simulazione "What-if" offline.
- Modello virtuale (Twin) della linea.
- Test strategie (velocità, manutenzione) senza rischi reali.
- Ottimizzazione multi-KPI.
