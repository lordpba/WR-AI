import asyncio
import logging
from typing import List, Dict
from .serial_adapter import serial_source
from .model import anomaly_model
from .database import init_database, save_anomaly_event, get_anomaly_events

logger = logging.getLogger(__name__)

class AnomalyService:
    def __init__(self):
        self.history: List[Dict] = []
        self.events: List[Dict] = []
        self.running = False
        self._load_persisted_events()
        
    def _load_persisted_events(self):
        """Load previously saved events from database on startup"""
        try:
            self.events = get_anomaly_events(limit=50)
            logger.info(f"Loaded {len(self.events)} persisted anomaly events")
        except Exception as e:
            logger.warning(f"Could not load persisted events: {e}")
            self.events = []
        
    async def start_loop(self):
        self.running = True
        logger.info("🕵️ Anomaly Detection Loop Started")
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
                if len(self.history) > 1000:
                    self.history.pop(0)

                # Log event if anomaly
                if status in ["warning", "critical"]:
                    if not self.events or (data['timestamp'] - self.events[0].get('timestamp', 0) > 5):
                        # Debounce events (don't spam every second)
                        event = {
                            "timestamp": data['timestamp'],
                            "type": status.upper(),
                            "message": f"Anomaly detected! Score: {risk_score:.1f}",
                            "details": data
                        }
                        
                        # Save to database and get ID
                        try:
                            event_id = save_anomaly_event(event)
                            event['id'] = event_id
                            logger.info(f"Anomaly event saved with ID {event_id}")
                        except Exception as e:
                            logger.error(f"Failed to persist anomaly event: {e}")
                        
                        self.events.insert(0, event)
                        # Keep max 50 events in memory
                        if len(self.events) > 50:
                            self.events.pop()

            await asyncio.sleep(1)  # Read every 1s (Simulating 1Hz sample rate)

service = AnomalyService()
