"""
Utility functions for the ingestion layer
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def parse_sensor_data(raw_data: str) -> Dict[str, Any]:
    """Parse raw sensor data from JSON string"""
    try:
        data = json.loads(raw_data)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse sensor data: {e}")
        return {}


def validate_sensor_data(data: Dict[str, Any]) -> bool:
    """Validate sensor data structure"""
    required_fields = ['sensor_type', 'timestamp', 'sensor_id']
    
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return False
    
    return True


def enrich_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich sensor data with additional metadata"""
    enriched = data.copy()
    
    # Add processing timestamp
    enriched['processed_at'] = datetime.utcnow().isoformat()
    
    # Add data quality score (simplified)
    enriched['data_quality'] = 1.0  # 1.0 = good quality
    
    return enriched


def get_sensor_topic(sensor_type: str) -> str:
    """Get MQTT topic for a sensor type"""
    topics = {
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
    return topics.get(sensor_type, f'agriculture/sensors/{sensor_type}')


def get_kafka_topic(sensor_type: str) -> str:
    """Get Kafka topic for a sensor type"""
    topics = {
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
    return topics.get(sensor_type, f'agriculture.{sensor_type}')


def format_timestamp(timestamp_str: str) -> datetime:
    """Convert ISO timestamp string to datetime object"""
    try:
        return datetime.fromisoformat(timestamp_str)
    except (ValueError, AttributeError):
        return datetime.utcnow()