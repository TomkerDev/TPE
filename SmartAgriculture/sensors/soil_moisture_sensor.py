import time
import random
from sensors.publisher import SensorPublisher

class SoilMoistureSensor:
    """Soil moisture sensor for agriculture monitoring"""
    
    def __init__(self, sensor_id=None):
        self.sensor_id = sensor_id or f"soil_sensor_{random.randint(1000, 9999)}"
        self.publisher = SensorPublisher('soil_moisture')
        self.min_moisture = 20.0
        self.max_moisture = 80.0
    
    def read_soil_moisture(self):
        """Simulate reading soil moisture from sensor"""
        # Simulate realistic soil moisture variation
        base_moisture = random.uniform(40, 70)
        variation = random.uniform(-3, 3)
        moisture = round(base_moisture + variation, 2)
        
        return {
            'sensor_id': self.sensor_id,
            'soil_moisture': moisture,
            'unit': 'percent'
        }
    
    def run(self, interval=5):
        """Run the sensor continuously"""
        print(f"Starting Soil Moisture Sensor {self.sensor_id}...")
        
        try:
            while True:
                data = self.read_soil_moisture()
                self.publisher.publish(data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\nStopping Soil Moisture Sensor {self.sensor_id}...")
            self.publisher.stop()

if __name__ == "__main__":
    sensor = SoilMoistureSensor()
    sensor.run()