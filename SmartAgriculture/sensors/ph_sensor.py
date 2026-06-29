import time
import random
from sensors.publisher import SensorPublisher

class PHSensor:
    """pH sensor for agriculture monitoring"""
    
    def __init__(self, sensor_id=None):
        self.sensor_id = sensor_id or f"ph_sensor_{random.randint(1000, 9999)}"
        self.publisher = SensorPublisher('ph')
        self.min_ph = 5.5
        self.max_ph = 7.5
    
    def read_ph(self):
        """Simulate reading pH from sensor"""
        # Simulate realistic pH variation (slightly acidic to neutral for most crops)
        base_ph = random.uniform(6.0, 7.0)
        variation = random.uniform(-0.3, 0.3)
        ph = round(base_ph + variation, 2)
        
        return {
            'sensor_id': self.sensor_id,
            'ph': ph,
            'unit': 'pH'
        }
    
    def run(self, interval=5):
        """Run the sensor continuously"""
        print(f"Starting pH Sensor {self.sensor_id}...")
        
        try:
            while True:
                data = self.read_ph()
                self.publisher.publish(data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\nStopping pH Sensor {self.sensor_id}...")
            self.publisher.stop()

if __name__ == "__main__":
    sensor = PHSensor()
    sensor.run()