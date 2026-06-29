import time
import random
from sensors.publisher import SensorPublisher

class WaterQualitySensor:
    """Water quality sensor for agriculture monitoring"""
    
    def __init__(self, sensor_id=None):
        self.sensor_id = sensor_id or f"water_quality_sensor_{random.randint(1000, 9999)}"
        self.publisher = SensorPublisher('water_quality')
    
    def read_water_quality(self):
        """Simulate reading water quality parameters"""
        # Simulate realistic water quality parameters
        ph = round(random.uniform(6.5, 8.5), 2)
        dissolved_oxygen = round(random.uniform(6.0, 12.0), 2)  # mg/L
        turbidity = round(random.uniform(0, 10), 2)  # NTU
        conductivity = round(random.uniform(200, 1500), 2)  # µS/cm
        
        return {
            'sensor_id': self.sensor_id,
            'ph': ph,
            'dissolved_oxygen': dissolved_oxygen,
            'turbidity': turbidity,
            'conductivity': conductivity,
            'unit_ph': 'pH',
            'unit_do': 'mg/L',
            'unit_turbidity': 'NTU',
            'unit_conductivity': 'µS/cm'
        }
    
    def run(self, interval=5):
        """Run the sensor continuously"""
        print(f"Starting Water Quality Sensor {self.sensor_id}...")
        
        try:
            while True:
                data = self.read_water_quality()
                self.publisher.publish(data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\nStopping Water Quality Sensor {self.sensor_id}...")
            self.publisher.stop()

if __name__ == "__main__":
    sensor = WaterQualitySensor()
    sensor.run()