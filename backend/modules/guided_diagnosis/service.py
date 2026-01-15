import os
from .llm_client import LLMFactory

MANUAL_FILE = os.path.join(os.path.dirname(__file__), "manual.txt")

class DiagnosisService:
    def __init__(self):
        self._ensure_manual_file()

    def _ensure_manual_file(self):
        if not os.path.exists(MANUAL_FILE):
            with open(MANUAL_FILE, "w") as f:
                f.write("Machine Manual Placeholder. Please update with real manual text.")

    def get_manual(self):
        with open(MANUAL_FILE, "r") as f:
            return f.read()

    def update_manual(self, text: str):
        with open(MANUAL_FILE, "w") as f:
            f.write(text)
        return {"status": "success", "message": "Manual updated"}

    def diagnose(self, anomaly_context: dict, user_query: str, provider: str, config: dict):
        manual_text = self.get_manual()
        
        # Prepare Context
        system_context = f"""
You are an expert industrial machine diagnostician.
Use the following Machine Manual context to answer the user's request and diagnosing the anomaly.
        
--- MACHINE MANUAL BEGIN ---
{manual_text}
--- MACHINE MANUAL END ---
"""

        # Prepare Anomaly Data presentation
        anomaly_str = "No specific anomaly data provided."
        if anomaly_context:
            # Handle standard anomaly object or the raw event object from frontend
            # The frontend 'events' array has structure: { type, message, details: { vibration, threshold } }
            # While the internal model has slightly different fields. Let's try to adapt.
            
            # If it comes from the event list in UI:
            details = anomaly_context.get('details', {})
            
            anomaly_str = f"""
Detected Anomaly Context:
- Type/Severity: {anomaly_context.get('type', anomaly_context.get('severity', 'N/A'))}
- Message/Description: {anomaly_context.get('message', anomaly_context.get('description', 'N/A'))}
- Signal Data: {details if details else anomaly_context.get('value', 'N/A')}
- Timestamp: {anomaly_context.get('timestamp', 'N/A')}
"""

        full_user_query = f"""
{anomaly_str}

User Query: {user_query}

Provide a diagnosis and suggested steps.
"""
        
        try:
            client = LLMFactory.get_client(provider, config)
            response = client.generate(full_user_query, system_context)
            return {"response": response}
        except Exception as e:
            return {"error": str(e)}

service = DiagnosisService()
