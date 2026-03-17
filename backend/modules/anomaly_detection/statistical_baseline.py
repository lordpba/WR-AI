"""
Statistical Baseline Monitor - Real-time lightweight anomaly detection
Uses rolling statistics (mean, std, min, max) to detect anomalies without ML overhead.
"""
import numpy as np
from collections import deque
from typing import Any, Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class StatisticalBaseline:
    """
    Maintains rolling statistics for each signal and detects statistical anomalies.
    Much lighter than ML models, suitable for real-time continuous monitoring.
    """
    
    def __init__(self, window_size: int = 300, sigma_threshold: float = 2.5):
        """
        Args:
            window_size: Number of recent samples to keep for statistics (default 300 = 5 min at 1Hz)
            sigma_threshold: Number of standard deviations for anomaly threshold (default 2.5)
        """
        self.window_size = window_size
        self.sigma_threshold = sigma_threshold
        
        # Rolling buffers per signal name (dynamic)
        self.buffers: Dict[str, deque] = {}
        self.stats: Dict[str, Dict[str, Any]] = {}
        
        self.is_calibrated = False
        self.min_samples_for_calibration = 30  # Need at least 30 samples for meaningful stats
        
    def add_data_point(self, temperature: float, vibration: float, power: float) -> Dict:
        """
        Add a new data point and compute statistics.
        
        Returns:
            Dict with status, risk_score, and detailed stats for each signal
        """
        return self.add_signals(
            {
                "temperature": temperature,
                "vibration": vibration,
                "power": power,
            }
        )

    def add_signals(self, signals: Dict[str, Any]) -> Dict:
        """
        Add a set of named signals (dynamic) and compute statistics/anomalies.

        Args:
            signals: dict of signal_name -> numeric value (non-numeric are ignored)
        """
        numeric_signals: Dict[str, float] = {}
        for k, v in (signals or {}).items():
            if v is None:
                continue
            try:
                fv = float(v)
            except Exception:
                continue
            if not np.isfinite(fv):
                continue
            numeric_signals[k] = fv

        # Add to buffers
        for name, value in numeric_signals.items():
            if name not in self.buffers:
                self.buffers[name] = deque(maxlen=self.window_size)
            self.buffers[name].append(value)

        # Determine sample count for calibration (use max buffer length)
        sample_count = max((len(b) for b in self.buffers.values()), default=0)
        if not self.is_calibrated and sample_count >= self.min_samples_for_calibration:
            self.is_calibrated = True
            logger.info(f"Statistical baseline calibrated with {sample_count} samples")

        # Compute statistics
        for name, buf in self.buffers.items():
            self.stats[name] = self._compute_stats(list(buf))

        # Detect anomalies
        if self.is_calibrated:
            anomalies = self._detect_anomalies_dynamic(numeric_signals)
            status, risk_score = self._compute_status(anomalies)
        else:
            anomalies = {}
            status = "calibrating"
            risk_score = 0.0

        return {
            "status": status,
            "risk_score": risk_score,
            "is_calibrated": self.is_calibrated,
            "stats": self.stats,
            "anomalies": anomalies,
            "current_values": numeric_signals,
        }
    
    def _compute_stats(self, data: List[float]) -> Dict:
        """Compute rolling statistics for a signal"""
        if len(data) == 0:
            return {
                'mean': 0, 'std': 0, 'min': 0, 'max': 0,
                'upper_bound': 0, 'lower_bound': 0
            }
        
        arr = np.array(data)
        mean = float(np.mean(arr))
        std = float(np.std(arr))
        
        return {
            'mean': mean,
            'std': std,
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'upper_bound': mean + self.sigma_threshold * std,
            'lower_bound': mean - self.sigma_threshold * std,
            'sample_count': len(data)
        }
    
    def _detect_anomalies_dynamic(self, signals: Dict[str, float]) -> Dict:
        anomalies: Dict[str, Dict[str, Any]] = {}
        for name, value in (signals or {}).items():
            s = self.stats.get(name)
            if not s:
                continue
            upper = s.get("upper_bound")
            lower = s.get("lower_bound")
            mean = s.get("mean", 0.0)
            std = s.get("std", 0.0) or 0.0
            if upper is None or lower is None:
                continue

            if value > upper:
                deviation = (value - mean) / std if std > 0 else 0.0
                anomalies[name] = {
                    "type": "high",
                    "value": value,
                    "deviation_sigma": deviation,
                    "threshold": upper,
                }
            elif value < lower:
                deviation = (mean - value) / std if std > 0 else 0.0
                anomalies[name] = {
                    "type": "low",
                    "value": value,
                    "deviation_sigma": deviation,
                    "threshold": lower,
                }
        return anomalies
    
    def _compute_status(self, anomalies: Dict) -> Tuple[str, float]:
        """
        Compute overall status and risk score based on detected anomalies.
        
        Returns:
            Tuple of (status, risk_score)
            - status: "ok", "warning", "critical"
            - risk_score: 0-100
        """
        if not anomalies:
            return "ok", 0.0
        
        # Count anomalies and get max deviation
        num_anomalies = len(anomalies)
        max_deviation = max(anomaly['deviation_sigma'] for anomaly in anomalies.values())
        
        # Determine severity
        # > 3.5 sigma = critical (very rare event)
        # > 2.5 sigma = warning (anomalous but not extreme)
        
        if max_deviation > 3.5 or num_anomalies >= 3:
            status = "critical"
            risk_score = min(100, 70 + max_deviation * 10)
        elif max_deviation > self.sigma_threshold or num_anomalies >= 2:
            status = "warning"
            risk_score = min(70, 40 + max_deviation * 10)
        else:
            status = "ok"
            risk_score = max_deviation * 10
        
        return status, float(risk_score)
    
    def get_current_stats(self) -> Dict:
        """Get current statistics for all signals"""
        return {
            'is_calibrated': self.is_calibrated,
            'window_size': self.window_size,
            'sigma_threshold': self.sigma_threshold,
            'sample_count': max((len(b) for b in self.buffers.values()), default=0),
            'stats': self.stats
        }


# Global instance
statistical_baseline = StatisticalBaseline()
