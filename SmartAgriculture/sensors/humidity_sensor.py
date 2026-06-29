import time
import random
from sensors.publisher import SensorPublisher

class HumiditySensor:
    """Humidity sensor for agriculture monitoring"""
    
    def __init__(self, sensor_id=None):
        self.sensor_id = sensor_id or f"humidity_sensor_{random.randint(1000, 9999)}"
        self.publisher = SensorPublisher('humidity')
        self.min_humidity = 30.0
        self.max_humidity = 90.0
    
    def read_humidity(self):
        """Simulate reading humidity from sensor"""
        # Simulate realistic humidity variation
        base_humidity = random.uniform(50, 80)
        variation = random.uniform(-5, 5)
        humidity = round(base_humidity + variation, 2)
        
        return {
            'sensor_id': self.sensor_id,
            'humidity': humidity,
            'unit': 'percent'
        }
    
    def run(self, interval=5):
        """Run the sensor continuously"""
        print(f"Starting Humidity Sensor {self.sensor_id}...")
        
        try:
            while True:
                data = self.read_humidity()
                self.publisher.publish(data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\nStopping Humidity Sensor {self.sensor_id}...")
            self.publisher.stop()

if __name__ == "__main__":
    sensor = HumiditySensor()
    sensor.run()