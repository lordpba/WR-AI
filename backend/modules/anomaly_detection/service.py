import asyncio
import logging
from typing import List, Dict
from .serial_adapter import serial_source
from .statistical_baseline import statistical_baseline
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
        logger.info("🕵️ Anomaly Detection Loop Started (Statistical Baseline Mode)")
        while self.running:
            data = serial_source.read_data()
            if data:
                # Use statistical baseline for real-time monitoring
                analysis = statistical_baseline.add_data_point(
                    data['temperature'],
                    data['vibration'],
                    data['power']
                )
                
                # Enhance data packet with analysis results
                data['anomaly_score'] = analysis['risk_score']
                data['status'] = analysis['status']
                data['model_ready'] = analysis['is_calibrated']
                data['stats'] = analysis['stats']
                data['anomalies'] = analysis.get('anomalies', {})
                
                # Store history
                self.history.append(data)
                if len(self.history) > 1000:
                    self.history.pop(0)

                # Log event if anomaly detected
                if analysis['status'] in ["warning", "critical"]:
                    if not self.events or (data['timestamp'] - self.events[0].get('timestamp', 0) > 5):
                        # Debounce events (don't spam every second)
                        # Create detailed event message
                        anomaly_signals = list(analysis['anomalies'].keys())
                        anomaly_desc = ', '.join([
                            f"{sig}: {analysis['anomalies'][sig]['type']} ({analysis['anomalies'][sig]['deviation_sigma']:.1f}σ)"
                            for sig in anomaly_signals
                        ])
                        
                        event = {
                            "timestamp": data['timestamp'],
                            "type": analysis['status'].upper(),
                            "message": f"Statistical anomaly detected! {anomaly_desc}",
                            "details": data
                        }
                        
                        # Save to database and get ID
                        try:
                            event_id = save_anomaly_event(event)
                            event['id'] = event_id
                            logger.info(f"Anomaly event saved with ID {event_id}: {anomaly_desc}")
                        except Exception as e:
                            logger.error(f"Failed to persist anomaly event: {e}")
                        
                        self.events.insert(0, event)
                        # Keep max 50 events in memory
                        if len(self.events) > 50:
                            self.events.pop()

            await asyncio.sleep(1)  # Read every 1s (Simulating 1Hz sample rate)

service = AnomalyService()
