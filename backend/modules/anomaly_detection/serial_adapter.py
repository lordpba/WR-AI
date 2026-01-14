import time
import random
# In a real scenario, this would import serial library
# from serial import Serial
from ..foundation.simulator import simulator

class SerialAdapter:
    """
    Simulates a Serial Port connection to a PLC or Sensor Box.
    In production, this class would wrap `pyserial`.
    Proto: CSV text "TIMESTAMP,TEMP,VIBRATION,POWER,SPEED"
    """
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.connected = True 
        print(f"🔌 Serial Port {port} opened at {baudrate} baud.")
        
    def read_data(self):
        """
        Reads a single 'line' of data from the machine.
        Returns mapped dictionary or None if empty.
        """
        if not self.connected:
            return None
            
        # Get ground truth from physics simulator
        # We add sensor noise to make it realistic for the ML model
        raw_temp = simulator.temperature + random.uniform(-0.2, 0.2)
        raw_vib = simulator.vibration + random.uniform(-0.05, 0.05)
        raw_power = simulator.current_power_kw + random.uniform(-0.5, 0.5)
        
        # Simulate occasional serial glitch/noise
        if random.random() < 0.01:
            raw_vib += 5.0 # Spike
            
        return {
            "timestamp": time.time(),
            "temperature": round(raw_temp, 2),
            "vibration": round(raw_vib, 3),
            "power": round(raw_power, 2),
            "speed": simulator.speed
        }

# Singleton instance to be used by the app
serial_source = SerialAdapter()
