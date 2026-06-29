import time
import random
from sensors.publisher import SensorPublisher

class TemperatureSensor:
    """Temperature sensor for agriculture monitoring"""
    
    def __init__(self, sensor_id=None):
        self.sensor_id = sensor_id or f"temp_sensor_{random.randint(1000, 9999)}"
        self.publisher = SensorPublisher('temperature')
        self.min_temp = 15.0
        self.max_temp = 40.0
    
    def read_temperature(self):
        """Simulate reading temperature from sensor"""
        # Simulate realistic temperature variation
        base_temp = random.uniform(20, 35)
        variation = random.uniform(-2, 2)
        temperature = round(base_temp + variation, 2)
        
        return {
            'sensor_id': self.sensor_id,
            'temperature': temperature,
            'unit': 'celsius'
        }
    
    def run(self, interval=5):
        """Run the sensor continuously"""
        print(f"Starting Temperature Sensor {self.sensor_id}...")
        
        try:
            while True:
                data = self.read_temperature()
                self.publisher.publish(data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\nStopping Temperature Sensor {self.sensor_id}...")
            self.publisher.stop()

if __name__ == "__main__":
    sensor = TemperatureSensor()
    sensor.run()