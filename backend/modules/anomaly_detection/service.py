import asyncio
from typing import List, Dict
from .serial_adapter import serial_source
from .model import anomaly_model

class AnomalyService:
    def __init__(self):
        self.history: List[Dict] = []
        self.events: List[Dict] = []
        self.running = False
        
    async def start_loop(self):
        self.running = True
        print("🕵️ Anomaly Detection Loop Started")
        while self.running:
            data = serial_source.read_data()
            if data:
                # Extract features for ML
                features = [data['temperature'], data['vibration'], data['power']]
                
                # Get prediction
                risk_score, status = anomaly_model.add_data_point(features)
                
                # Enhance data packet
                data['anomaly_score'] = risk_score
                data['status'] = status
                data['model_ready'] = anomaly_model.is_trained
                
                # Store history
                self.history.append(data)
                if len(self.history) > 100:
                    self.history.pop(0)

                # Log event if anomaly
                if status in ["warning", "critical"]:
                    if not self.events or (data['timestamp'] - self.events[-1]['timestamp'] > 5):
                         # Debounce events (don't spam every second)
                        self.events.insert(0, {
                            "timestamp": data['timestamp'],
                            "type": status.upper(),
                            "message": f"Anomaly detected! Score: {risk_score:.1f}",
                            "details": data
                        })
                        # Keep max 50 events
                        if len(self.events) > 50:
                            self.events.pop()

            await asyncio.sleep(1) # Read every 1s (Simulating 1Hz sample rate)

service = AnomalyService()
