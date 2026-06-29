import time
import random
from sensors.publisher import SensorPublisher

class RainfallSensor:
    """Rainfall sensor for agriculture monitoring"""
    
    def __init__(self, sensor_id=None):
        self.sensor_id = sensor_id or f"rainfall_sensor_{random.randint(1000, 9999)}"
        self.publisher = SensorPublisher('rainfall')
    
    def read_rainfall(self):
        """Simulate reading rainfall from sensor"""
        # Simulate realistic rainfall (mm in last hour)
        # Most of the time no rain, occasionally light to moderate rain
        if random.random() < 0.7:  # 70% chance of no rain
            rainfall = 0.0
        else:
            rainfall = round(random.uniform(0.5, 15.0), 2)
        
        return {
            'sensor_id': self.sensor_id,
            'rainfall': rainfall,
            'unit': 'mm',
            'period': 'last_hour'
        }
    
    def run(self, interval=5):
        """Run the sensor continuously"""
        print(f"Starting Rainfall Sensor {self.sensor_id}...")
        
        try:
            while True:
                data = self.read_rainfall()
                self.publisher.publish(data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\nStopping Rainfall Sensor {self.sensor_id}...")
            self.publisher.stop()

if __name__ == "__main__":
    sensor = RainfallSensor()
    sensor.run()