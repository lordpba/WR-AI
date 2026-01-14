import numpy as np
import threading
import time
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        # We use Isolation Forest: efficient, unsupervised, good for high-dim data
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.02, # Expected outlier rate
            random_state=42
        )
        self.is_trained = False
        self.training_buffer = []
        self.TRAIN_SIZE = 60 # Train after collecting 60 samples (simulated seconds)
        self.lock = threading.Lock()
        
    def add_data_point(self, features):
        """
        features: [temperature, vibration, power]
        """
        with self.lock:
            # If not yet trained, collect data
            if not self.is_trained:
                self.training_buffer.append(features)
                if len(self.training_buffer) >= self.TRAIN_SIZE:
                    self.train_model()
                return 0.0, "calibrating" # Score 0 means unknown/neutral

            # Predict
            # IsolationForest predict: 1 (normal), -1 (anomaly)
            # decision_function: <0 (anomaly), >0 (normal)
            score = self.model.decision_function([features])[0]
            
            # Normalize for UI: 
            # We want 0-100% risk score.
            # decision function usually ranges -0.5 to 0.5 approx for these datasets
            # Let's invert and map.
            # safe ~ 0.2, risk ~ -0.2
            
            risk_score = 0
            status = "ok"

            if score < -0.15:
                status = "critical"
                risk_score = 90
            elif score < 0:
                status = "warning"
                risk_score = 60
            else:
                status = "ok"
                risk_score = max(0, 10 - (score * 50))

            return risk_score, status

    def train_model(self):
        print("🧠 Training Anomaly Detection Model...")
        X = np.array(self.training_buffer)
        self.model.fit(X)
        self.is_trained = True
        print(f"✅ Training Complete on {len(X)} samples.")
        
# Singleton
anomaly_model = AnomalyDetector()
