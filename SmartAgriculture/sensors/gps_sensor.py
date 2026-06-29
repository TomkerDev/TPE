import time
import random
from sensors.publisher import SensorPublisher

class GPSSensor:
    """GPS sensor for agriculture monitoring"""
    
    def __init__(self, sensor_id=None):
        self.sensor_id = sensor_id or f"gps_sensor_{random.randint(1000, 9999)}"
        self.publisher = SensorPublisher('gps')
        # Base location (can be set to farm coordinates)
        self.base_latitude = 36.7538  # Example: Tunisia coordinates
        self.base_longitude = 10.2922
    
    def read_gps(self):
        """Simulate reading GPS coordinates"""
        # Simulate small variations in GPS coordinates
        latitude = round(self.base_latitude + random.uniform(-0.001, 0.001), 6)
        longitude = round(self.base_longitude + random.uniform(-0.001, 0.001), 6)
        altitude = round(random.uniform(50, 200), 2)  # meters above sea level
        speed = round(random.uniform(0, 5), 2)  # km/h (for moving equipment)
        
        return {
            'sensor_id': self.sensor_id,
            'latitude': latitude,
            'longitude': longitude,
            'altitude': altitude,
            'speed': speed,
            'unit_altitude': 'meters',
            'unit_speed': 'km/h'
        }
    
    def run(self, interval=5):
        """Run the sensor continuously"""
        print(f"Starting GPS Sensor {self.sensor_id}...")
        
        try:
            while True:
                data = self.read_gps()
                self.publisher.publish(data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\nStopping GPS Sensor {self.sensor_id}...")
            self.publisher.stop()

if __name__ == "__main__":
    sensor = GPSSensor()
    sensor.run()