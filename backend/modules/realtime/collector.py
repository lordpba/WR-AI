from __future__ import annotations

import asyncio
import logging
import math
import os
import time
from typing import Any, Dict, Optional

from .database import save_event, save_sample, get_latest_sample
from .modbus_client import modbus_source
from .rules import realtime_rules
from .config_store import get_config

logger = logging.getLogger(__name__)


def _calc_power_kw(point: Dict[str, Any]) -> Optional[float]:
    # If already present, trust it
    p = point.get("power_kw")
    if isinstance(p, (int, float)):
        return float(p)

    v = point.get("voltage_v")
    i = point.get("current_a")
    pf = point.get("power_factor")
    if not all(isinstance(x, (int, float)) for x in (v, i, pf)):
        return None

    phase = os.getenv("RT_ELECTRICAL_MODE", "three_phase").strip().lower()
    scale = math.sqrt(3.0) if phase == "three_phase" else 1.0
    return (scale * float(v) * float(i) * float(pf)) / 1000.0


class RealtimeCollector:
    def __init__(self):
        self.running = False
        self.last_error: Optional[str] = None
        self.last_sample: Optional[Dict[str, Any]] = None
        self.poll_interval_s = float(os.getenv("RT_POLL_INTERVAL_S", "1.0"))
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """
        Start the collector loop and return the running task.
        """
        if self.running and self._task:
            return self._task
        self.running = True
        self._task = asyncio.create_task(self._loop())
        return self._task

    async def stop(self):
        self.running = False
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=2.0)
            except asyncio.TimeoutError:
                self._task.cancel()
                try:
                    await asyncio.wait_for(self._task, timeout=2.0)
                except Exception:
                    pass
            except asyncio.CancelledError:
                pass
            except Exception:
                # keep shutdown resilient
                pass
        self._task = None
        try:
            await modbus_source.disconnect()
        except Exception:
            pass

    async def _loop(self):
        logger.info("📡 RealtimeCollector loop started (Modbus TCP)")
        while self.running:
            ts = time.time()
            try:
                try:
                    cfg = get_config()
                    self.poll_interval_s = float(cfg.get("poll_interval_s") or self.poll_interval_s)
                except Exception:
                    pass

                if not modbus_source.is_configured:
                    self.last_error = "MODBUS_HOST not configured"
                    await asyncio.sleep(self.poll_interval_s)
                    continue

                point = await modbus_source.read_point()
                point["power_kw"] = _calc_power_kw(point)
                point["power"] = point.get("power_kw")

                self.last_sample = {"timestamp": ts, **point}
                self.last_error = None

                save_sample(ts, point)

                for ev in realtime_rules.evaluate(point, ts):
                    save_event(ts, ev.event_type, ev.message, ev.details)

            except Exception as e:
                self.last_error = str(e)
                logger.warning(f"RealtimeCollector read error: {e}")

            await asyncio.sleep(self.poll_interval_s)

    def get_status(self) -> Dict[str, Any]:
        latest = self.last_sample or get_latest_sample()
        return {
            "connected": bool(modbus_source.is_connected),
            "configured": bool(modbus_source.is_configured),
            "last_error": self.last_error,
            "last_sample": latest,
            "poll_interval_s": self.poll_interval_s,
        }


collector = RealtimeCollector()

