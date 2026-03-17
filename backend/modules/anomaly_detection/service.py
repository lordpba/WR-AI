import asyncio
import logging
from typing import Any, Dict, List, Optional
from .statistical_baseline import statistical_baseline
from .database import init_database, save_anomaly_event, get_anomaly_events

logger = logging.getLogger(__name__)

class AnomalyService:
    def __init__(self):
        self.history: List[Dict] = []
        self.events: List[Dict] = []
        self.running = False
        self.source_mode: str = "realtime"  # "realtime" | "file"
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
            if self.source_mode == "realtime":
                # Lazy import to avoid side effects when realtime loop is disabled
                from .serial_adapter import serial_source
                data = serial_source.read_data()
                if data:
                    self._process_point(data, persist_event=True)

            await asyncio.sleep(1)  # Read every 1s (Simulating 1Hz sample rate)

    def set_source_mode(self, mode: str) -> str:
        mode = (mode or "").strip().lower()
        if mode not in ("realtime", "file"):
            mode = "realtime"
        self.source_mode = mode
        return self.source_mode

    def load_history_from_import(
        self,
        points: List[Dict[str, Any]],
        max_points: int = 1000,
        clear_events: bool = True,
    ) -> Dict[str, Any]:
        # Reset baseline for a clean calibration on the imported dataset
        from .statistical_baseline import StatisticalBaseline
        statistical_baseline.__dict__ = StatisticalBaseline().__dict__

        if clear_events:
            self.events.clear()

        self.history.clear()
        self.set_source_mode("file")

        points_sorted = sorted(points, key=lambda p: float(p.get("timestamp", 0.0)))
        if len(points_sorted) > max_points:
            points_sorted = points_sorted[-max_points:]

        for p in points_sorted:
            self._process_point(dict(p), persist_event=False)

        return {
            "mode": self.source_mode,
            "points_loaded": len(self.history),
            "events_generated": len(self.events),
        }

    def _process_point(self, data: Dict[str, Any], persist_event: bool) -> Optional[Dict[str, Any]]:
        if not data or "timestamp" not in data:
            return None

        if data.get("power") is None and data.get("power_kw") is not None:
            data["power"] = data.get("power_kw")

        signals = {
            "temperature": data.get("temperature"),
            "vibration": data.get("vibration"),
            "power": data.get("power"),
            "voltage_v": data.get("voltage_v"),
            "current_a": data.get("current_a"),
            "power_factor": data.get("power_factor"),
        }
        analysis = statistical_baseline.add_signals(signals)

        data["anomaly_score"] = analysis["risk_score"]
        data["status"] = analysis["status"]
        data["model_ready"] = analysis["is_calibrated"]
        data["stats"] = analysis["stats"]
        data["anomalies"] = analysis.get("anomalies", {})

        self.history.append(data)
        if len(self.history) > 1000:
            self.history.pop(0)

        if analysis["status"] in ["warning", "critical"]:
            if not self.events or (data["timestamp"] - self.events[0].get("timestamp", 0) > 5):
                anomaly_signals = list(analysis["anomalies"].keys())
                anomaly_desc = ", ".join(
                    [
                        f"{sig}: {analysis['anomalies'][sig]['type']} ({analysis['anomalies'][sig]['deviation_sigma']:.1f}σ)"
                        for sig in anomaly_signals
                    ]
                )

                event = {
                    "timestamp": data["timestamp"],
                    "type": analysis["status"].upper(),
                    "message": f"Statistical anomaly detected! {anomaly_desc}",
                    "details": data,
                }

                if persist_event:
                    try:
                        event_id = save_anomaly_event(event)
                        event["id"] = event_id
                        logger.info(f"Anomaly event saved with ID {event_id}: {anomaly_desc}")
                    except Exception as e:
                        logger.error(f"Failed to persist anomaly event: {e}")

                self.events.insert(0, event)
                if len(self.events) > 50:
                    self.events.pop()

        return data

service = AnomalyService()
