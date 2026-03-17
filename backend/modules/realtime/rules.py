from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


def _f(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return float(default)


@dataclass(frozen=True)
class RuleEvent:
    event_type: str  # WARNING | CRITICAL | INFO
    message: str
    details: Dict[str, Any]


class RealtimeRules:
    """
    Deterministic realtime alerts: out-of-range, low PF, high current, stuck value.
    Tuned via env vars.
    """

    def __init__(self):
        self.v_min = _f("RT_VOLTAGE_MIN", 180.0)
        self.v_max = _f("RT_VOLTAGE_MAX", 260.0)
        self.i_warn = _f("RT_CURRENT_WARN", 80.0)
        self.i_crit = _f("RT_CURRENT_CRIT", 120.0)
        self.pf_warn = _f("RT_PF_WARN", 0.70)
        self.pf_crit = _f("RT_PF_CRIT", 0.50)

        self.stuck_seconds = _f("RT_STUCK_SECONDS", 30.0)
        self._last_values: Dict[str, Tuple[float, float]] = {}  # name -> (value, ts)

    def evaluate(self, point: Dict[str, Any], timestamp: float) -> List[RuleEvent]:
        events: List[RuleEvent] = []

        v = point.get("voltage_v")
        if isinstance(v, (int, float)):
            if v < self.v_min or v > self.v_max:
                events.append(
                    RuleEvent(
                        event_type="WARNING",
                        message="Voltage out of expected range",
                        details={"voltage_v": v, "min": self.v_min, "max": self.v_max},
                    )
                )

        i = point.get("current_a")
        if isinstance(i, (int, float)):
            if i >= self.i_crit:
                events.append(RuleEvent("CRITICAL", "Current too high", {"current_a": i, "crit": self.i_crit}))
            elif i >= self.i_warn:
                events.append(RuleEvent("WARNING", "Current high", {"current_a": i, "warn": self.i_warn}))

        pf = point.get("power_factor")
        if isinstance(pf, (int, float)):
            if pf <= self.pf_crit:
                events.append(RuleEvent("CRITICAL", "Power factor very low", {"power_factor": pf, "crit": self.pf_crit}))
            elif pf <= self.pf_warn:
                events.append(RuleEvent("WARNING", "Power factor low", {"power_factor": pf, "warn": self.pf_warn}))

        # Stuck detection on selected keys
        for key in ("current_a", "voltage_v", "power_factor"):
            val = point.get(key)
            if not isinstance(val, (int, float)):
                continue
            last = self._last_values.get(key)
            if last:
                last_val, last_ts = last
                if float(val) == float(last_val) and (timestamp - last_ts) >= self.stuck_seconds:
                    events.append(
                        RuleEvent(
                            "INFO",
                            f"{key} appears stuck (unchanged)",
                            {"signal": key, "value": val, "seconds": timestamp - last_ts},
                        )
                    )
            self._last_values[key] = (float(val), float(timestamp))

        return events


realtime_rules = RealtimeRules()

