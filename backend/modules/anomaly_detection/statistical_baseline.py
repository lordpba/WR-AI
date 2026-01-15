"""
Statistical Baseline Monitor - Real-time lightweight anomaly detection
Uses rolling statistics (mean, std, min, max) to detect anomalies without ML overhead.
"""
import numpy as np
from collections import deque
from typing import Dict, List, Tuple, Optional
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
        
        # Separate buffers for each signal
        self.temperature_buffer = deque(maxlen=window_size)
        self.vibration_buffer = deque(maxlen=window_size)
        self.power_buffer = deque(maxlen=window_size)
        
        # Statistics cache
        self.stats = {
            'temperature': {},
            'vibration': {},
            'power': {}
        }
        
        self.is_calibrated = False
        self.min_samples_for_calibration = 30  # Need at least 30 samples for meaningful stats
        
    def add_data_point(self, temperature: float, vibration: float, power: float) -> Dict:
        """
        Add a new data point and compute statistics.
        
        Returns:
            Dict with status, risk_score, and detailed stats for each signal
        """
        # Add to buffers
        self.temperature_buffer.append(temperature)
        self.vibration_buffer.append(vibration)
        self.power_buffer.append(power)
        
        # Check if calibrated
        if not self.is_calibrated and len(self.temperature_buffer) >= self.min_samples_for_calibration:
            self.is_calibrated = True
            logger.info(f"Statistical baseline calibrated with {len(self.temperature_buffer)} samples")
        
        # Compute statistics
        self.stats['temperature'] = self._compute_stats(list(self.temperature_buffer))
        self.stats['vibration'] = self._compute_stats(list(self.vibration_buffer))
        self.stats['power'] = self._compute_stats(list(self.power_buffer))
        
        # Detect anomalies
        if self.is_calibrated:
            anomalies = self._detect_anomalies(temperature, vibration, power)
            status, risk_score = self._compute_status(anomalies)
        else:
            anomalies = {}
            status = "calibrating"
            risk_score = 0.0
        
        return {
            'status': status,
            'risk_score': risk_score,
            'is_calibrated': self.is_calibrated,
            'stats': self.stats,
            'anomalies': anomalies,
            'current_values': {
                'temperature': temperature,
                'vibration': vibration,
                'power': power
            }
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
    
    def _detect_anomalies(self, temperature: float, vibration: float, power: float) -> Dict:
        """
        Check if current values are anomalous based on statistical bounds.
        
        Returns:
            Dict with anomaly flags and deviation levels for each signal
        """
        anomalies = {}
        
        # Check temperature
        temp_stats = self.stats['temperature']
        if temperature > temp_stats['upper_bound']:
            deviation = (temperature - temp_stats['mean']) / temp_stats['std'] if temp_stats['std'] > 0 else 0
            anomalies['temperature'] = {
                'type': 'high',
                'value': temperature,
                'deviation_sigma': deviation,
                'threshold': temp_stats['upper_bound']
            }
        elif temperature < temp_stats['lower_bound']:
            deviation = (temp_stats['mean'] - temperature) / temp_stats['std'] if temp_stats['std'] > 0 else 0
            anomalies['temperature'] = {
                'type': 'low',
                'value': temperature,
                'deviation_sigma': deviation,
                'threshold': temp_stats['lower_bound']
            }
        
        # Check vibration
        vib_stats = self.stats['vibration']
        if vibration > vib_stats['upper_bound']:
            deviation = (vibration - vib_stats['mean']) / vib_stats['std'] if vib_stats['std'] > 0 else 0
            anomalies['vibration'] = {
                'type': 'high',
                'value': vibration,
                'deviation_sigma': deviation,
                'threshold': vib_stats['upper_bound']
            }
        elif vibration < vib_stats['lower_bound']:
            deviation = (vib_stats['mean'] - vibration) / vib_stats['std'] if vib_stats['std'] > 0 else 0
            anomalies['vibration'] = {
                'type': 'low',
                'value': vibration,
                'deviation_sigma': deviation,
                'threshold': vib_stats['lower_bound']
            }
        
        # Check power
        power_stats = self.stats['power']
        if power > power_stats['upper_bound']:
            deviation = (power - power_stats['mean']) / power_stats['std'] if power_stats['std'] > 0 else 0
            anomalies['power'] = {
                'type': 'high',
                'value': power,
                'deviation_sigma': deviation,
                'threshold': power_stats['upper_bound']
            }
        elif power < power_stats['lower_bound']:
            deviation = (power_stats['mean'] - power) / power_stats['std'] if power_stats['std'] > 0 else 0
            anomalies['power'] = {
                'type': 'low',
                'value': power,
                'deviation_sigma': deviation,
                'threshold': power_stats['lower_bound']
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
            'sample_count': len(self.temperature_buffer),
            'stats': self.stats
        }


# Global instance
statistical_baseline = StatisticalBaseline()
