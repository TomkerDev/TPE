import time
import random
from sensors.publisher import SensorPublisher

class LightSensor:
    """Light sensor for agriculture monitoring"""
    
    def __init__(self, sensor_id=None):
        self.sensor_id = sensor_id or f"light_sensor_{random.randint(1000, 9999)}"
        self.publisher = SensorPublisher('light')
    
    def read_light(self):
        """Simulate reading light intensity from sensor"""
        # Simulate realistic light intensity (lux)
        # Daytime: 10000-100000 lux, Night: 0-100 lux
        hour = random.randint(0, 23)
        
        if 6 <= hour <= 18:  # Daytime
            base_light = random.uniform(20000, 80000)
        else:  # Nighttime
            base_light = random.uniform(0, 50)
        
        variation = random.uniform(-1000, 1000)
        light_intensity = round(max(0, base_light + variation), 2)
        
        return {
            'sensor_id': self.sensor_id,
            'light_intensity': light_intensity,
            'unit': 'lux',
            'hour': hour
        }
    
    def run(self, interval=5):
        """Run the sensor continuously"""
        print(f"Starting Light Sensor {self.sensor_id}...")
        
        try:
            while True:
                data = self.read_light()
                self.publisher.publish(data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\nStopping Light Sensor {self.sensor_id}...")
            self.publisher.stop()

if __name__ == "__main__":
    sensor = LightSensor()
    sensor.run()