import time
import random
from sensors.publisher import SensorPublisher

class WindSensor:
    """Wind sensor for agriculture monitoring"""
    
    def __init__(self, sensor_id=None):
        self.sensor_id = sensor_id or f"wind_sensor_{random.randint(1000, 9999)}"
        self.publisher = SensorPublisher('wind')
    
    def read_wind(self):
        """Simulate reading wind data from sensor"""
        # Simulate realistic wind speed and direction
        wind_speed = round(random.uniform(0, 25), 2)  # km/h
        wind_direction = round(random.uniform(0, 360), 2)  # degrees
        
        return {
            'sensor_id': self.sensor_id,
            'wind_speed': wind_speed,
            'wind_direction': wind_direction,
            'unit_speed': 'km/h',
            'unit_direction': 'degrees'
        }
    
    def run(self, interval=5):
        """Run the sensor continuously"""
        print(f"Starting Wind Sensor {self.sensor_id}...")
        
        try:
            while True:
                data = self.read_wind()
                self.publisher.publish(data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\nStopping Wind Sensor {self.sensor_id}...")
            self.publisher.stop()

if __name__ == "__main__":
    sensor = WindSensor()
    sensor.run()