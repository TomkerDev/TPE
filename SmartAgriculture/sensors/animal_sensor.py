import time
import random
from sensors.publisher import SensorPublisher

class AnimalSensor:
    """Animal sensor for agriculture monitoring (livestock tracking)"""
    
    def __init__(self, sensor_id=None):
        self.sensor_id = sensor_id or f"animal_sensor_{random.randint(1000, 9999)}"
        self.publisher = SensorPublisher('animal')
        self.animal_ids = [f"LIVESTOCK_{i:03d}" for i in range(1, 21)]  # 20 animals
    
    def read_animal_data(self):
        """Simulate reading animal sensor data"""
        # Simulate realistic animal monitoring data
        animal_id = random.choice(self.animal_ids)
        
        # Activity level: 0-100 (0=resting, 100=very active)
        activity_level = round(random.uniform(20, 80), 2)
        
        # Body temperature: 37-40°C for cattle
        body_temperature = round(random.uniform(37.5, 39.5), 2)
        
        # Heart rate: 40-80 bpm for cattle
        heart_rate = round(random.uniform(40, 80), 2)
        
        # Location (could be linked to GPS)
        location_zone = random.choice(['Zone_A', 'Zone_B', 'Zone_C', 'Zone_D'])
        
        # Health status
        health_status = random.choice(['healthy', 'healthy', 'healthy', 'attention', 'critical'])
        
        return {
            'sensor_id': self.sensor_id,
            'animal_id': animal_id,
            'activity_level': activity_level,
            'body_temperature': body_temperature,
            'heart_rate': heart_rate,
            'location_zone': location_zone,
            'health_status': health_status,
            'unit_temperature': 'celsius',
            'unit_heart_rate': 'bpm'
        }
    
    def run(self, interval=5):
        """Run the sensor continuously"""
        print(f"Starting Animal Sensor {self.sensor_id}...")
        
        try:
            while True:
                data = self.read_animal_data()
                self.publisher.publish(data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\nStopping Animal Sensor {self.sensor_id}...")
            self.publisher.stop()

if __name__ == "__main__":
    sensor = AnimalSensor()
    sensor.run()