import os
from dotenv import load_dotenv

load_dotenv()

class SensorConfig:
    """Configuration class for sensors"""
    
    # MQTT Configuration
    MQTT_HOST = os.getenv('MQTT_HOST', 'localhost')
    MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
    
    # Kafka Configuration
    KAFKA_HOST = os.getenv('KAFKA_HOST', 'localhost:9092')
    
    # PostgreSQL Configuration
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'agriculture')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'admin123')
    
    # MongoDB Configuration
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    
    # Neo4j Configuration
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')
    
    # Sensor Topics
    TOPICS = {
        'temperature': 'agriculture/sensors/temperature',
        'humidity': 'agriculture/sensors/humidity',
        'soil_moisture': 'agriculture/sensors/soil_moisture',
        'ph': 'agriculture/sensors/ph',
        'rainfall': 'agriculture/sensors/rainfall',
        'light': 'agriculture/sensors/light',
        'wind': 'agriculture/sensors/wind',
        'water_quality': 'agriculture/sensors/water_quality',
        'gps': 'agriculture/sensors/gps',
        'animal': 'agriculture/sensors/animal'
    }
    
    # Kafka Topics
    KAFKA_TOPICS = {
        'temperature': 'agriculture.temperature',
        'humidity': 'agriculture.humidity',
        'soil_moisture': 'agriculture.soil_moisture',
        'ph': 'agriculture.ph',
        'rainfall': 'agriculture.rainfall',
        'light': 'agriculture.light',
        'wind': 'agriculture.wind',
        'water_quality': 'agriculture.water_quality',
        'gps': 'agriculture.gps',
        'animal': 'agriculture.animal'
    }