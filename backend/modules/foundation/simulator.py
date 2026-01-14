import random
import time
from datetime import datetime
import pandas as pd

class PLCSimulator:
    def __init__(self):
        self.state = "STOP" # RUN, STOP, FAULT
        self.last_state_change = time.time()
        self.total_produced = 0
        self.total_scarp = 0
        self.current_recipe = "Recipe_A"
        self.speed = 0 # pieces per minute
        self.energy_counter_kwh = 12500.0 # Starting offset
        self.current_power_kw = 0.0
        
        # Module 2: Anomaly Signals
        self.temperature = 45.0 # Celsius
        self.vibration = 0.5 # mm/s
        self.anomaly_drift = 0.0 # Simulated wear factor (0.0 to 1.0)
        self.active_alerts = []
        
        # Simulation parameters
        self.recipes = {
            "Recipe_A": {"target_speed": 120, "power_base": 45.0},
            "Recipe_B": {"target_speed": 80, "power_base": 60.0},
            "Recipe_C": {"target_speed": 150, "power_base": 30.0},
        }
        
        # History for OEE and charts
        self.history = []
        self.alarms_history = []
        
        # Fault reasons
        self.fault_reasons = [
            "Emergency Stop", "Motor Overload", "feeder_jam", "quality_check_fail"
        ]
        
    def _transition_logic(self):
        now = time.time()
        time_in_state = now - self.last_state_change
        
        # Simple Markov-like chain
        if self.state == "RUN":
            # high chance to stay in RUN
            if random.random() < 0.05 and time_in_state > 10: 
                # Trigger a stop or fault
                if random.random() < 0.7:
                    self.state = "STOP"
                else:
                    self.state = "FAULT"
                    # Log alarm
                    self.alarms_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "reason": random.choice(self.fault_reasons),
                        "duration": 0 # to be updated
                    })
                self.last_state_change = now
                
        elif self.state == "STOP":
            # IDLE state, operator logic
            if time_in_state > random.randint(5, 20):
                self.state = "RUN"
                self.last_state_change = now
                
        elif self.state == "FAULT":
            # Time to fix fault
            if time_in_state > random.randint(10, 40):
                self.state = "RUN"
                # Close the alarm entry logic would go here ideally
                self.last_state_change = now

    def update(self):
        self._transition_logic()
        
        # Simulation values based on state
        if self.state == "RUN":
            target = self.recipes[self.current_recipe]
            # Add some noise
            self.speed = target["target_speed"] * random.uniform(0.9, 1.05)
            self.current_power_kw = target["power_base"] * random.uniform(0.95, 1.1)
            
            # Add production (assuming update called every 1s)
            pieces_generated = (self.speed / 60.0) 
            # 2% scrap rate
            if random.random() < 0.02:
                self.total_scarp += pieces_generated
            else:
                self.total_produced += pieces_generated
                
        elif self.state == "STOP":
            self.speed = 0
            self.current_power_kw = 5.0 # Idle power
            
        elif self.state == "FAULT":
            self.speed = 0
            self.current_power_kw = 2.0 # Standby usually lower or higher depending on fault
            
        # Accumulate Energy
        # Power (kW) * time (h). Update is 1 sec approx -> 1/3600 h.
        self.energy_counter_kwh += self.current_power_kw / 3600.0
        
        # --- Module 2: Anomaly Simulation ---
        # Simulate drift (wear & tear)
        if self.state == "RUN" and random.random() < 0.05:
            self.anomaly_drift += 0.01 # Wear increases
            
        # Reset drift on Maintenance (simulated by Long Stop or Fault fixed)
        if self.state == "FAULT" and random.random() < 0.05:
             self.anomaly_drift = 0.0

        # Physics simulation
        # Temp increases with power and drift
        target_temp = 45.0 + (self.current_power_kw * 0.4) + (self.anomaly_drift * 40.0)
        # Simple smoothing
        self.temperature += (target_temp - self.temperature) * 0.1 + random.uniform(-0.5, 0.5)
        
        # Vibration increases with speed and drift
        target_vib = (self.speed / 100.0) + (self.anomaly_drift * 8.0)
        self.vibration = target_vib + random.uniform(0, 0.3)
        
        self._check_anomalies()
        # ------------------------------------
        
        # Log metrics (limit history size)
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "state": self.state,
            "speed": round(self.speed, 1),
            "power": round(self.current_power_kw, 2),
            "temperature": round(self.temperature, 1),
            "vibration": round(self.vibration, 2),
            "produced": int(self.total_produced),
            "scrap": int(self.total_scarp)
        }
        self.history.append(snapshot)
        if len(self.history) > 3600: # keep last hour roughly
            self.history.pop(0)
            
    def _check_anomalies(self):
        self.active_alerts = []
        
        # Rule-based Anomaly Detection (POC)
        # In Module 2, we simulate this interception before failure
        if self.temperature > 95.0:
            self.active_alerts.append({"type": "critical", "message": "CRITICAL: Overheating Detect", "value": f"{round(self.temperature, 1)}°C"})
        elif self.temperature > 80.0:
             self.active_alerts.append({"type": "warning", "message": "Warning: High Temp Drift", "value": f"{round(self.temperature, 1)}°C"})
             
        if self.vibration > 8.0:
             self.active_alerts.append({"type": "critical", "message": "CRITICAL: Motor Imbalance", "value": f"{round(self.vibration, 2)}mm/s"})
        elif self.vibration > 4.0:
             self.active_alerts.append({"type": "warning", "message": "Early Warning: Vibration", "value": f"{round(self.vibration, 2)}mm/s"})

    def get_status(self):
        return {
            "state": self.state,
            "recipe": self.current_recipe,
            "speed": round(self.speed, 1),
            "power": round(self.current_power_kw, 2),
            "temperature": round(self.temperature, 1),
            "vibration": round(self.vibration, 2),
            "alerts": self.active_alerts,
            "energy_kwh": round(self.energy_counter_kwh, 2),
            "produced": int(self.total_produced),
            "scrap": int(self.total_scarp),
            "oee_percent": self._calculate_realtime_oee(),
            "timestamp": datetime.now().isoformat()
        }
        
    def _calculate_realtime_oee(self):
        # Very simplified OEE for realtime display
        # Availability implies time running vs total time (simplified here)
        # Performance is speed / target speed
        # Quality is good / total
        
        if self.total_produced + self.total_scarp == 0:
            return 0
            
        quality = self.total_produced / (self.total_produced + self.total_scarp)
        
        # Performance (instant)
        target = self.recipes[self.current_recipe]["target_speed"]
        performance = 0 
        if self.state == "RUN":
             performance = min(self.speed / target, 1.0)
             
        # Availability (windowed over history) or instant state
        # Usually availability is calculated over a shift. Here we use instant state for visual flair 'proxy'
        # But a correct OEE is historical. Let's do a "Shift OEE" approximation
        availability = 0.85 # default dummy
        if len(self.history) > 0:
            run_count = sum(1 for h in self.history if h['state'] == 'RUN')
            availability = run_count / len(self.history)
            
        oee = availability * performance * quality
        return round(oee * 100, 1)

    def get_pareto_data(self):
        # Fake aggregation if history is too short
        if not self.alarms_history:
             return [
                 {"reason": "Emergency Stop", "count": 5, "duration_min": 45},
                 {"reason": "feeder_jam", "count": 12, "duration_min": 30},
                 {"reason": "Motor Overload", "count": 2, "duration_min": 20},
                 {"reason": "quality_check_fail", "count": 8, "duration_min": 15},
             ]
        # Real aggregation logic could go here
        return [
             {"reason": "Emergency Stop", "count": 5, "duration_min": 45},
             {"reason": "feeder_jam", "count": 12, "duration_min": 30},
             {"reason": "Motor Overload", "count": 2, "duration_min": 20},
             {"reason": "quality_check_fail", "count": 8, "duration_min": 15},
         ]

# Singleton Instance
simulator = PLCSimulator()
