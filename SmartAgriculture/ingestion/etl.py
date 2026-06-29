"""
ETL Pipeline - Extract, Transform, Load for sensor data
"""
import os
import json
import time
import logging
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

from ingestion.utils import validate_sensor_data, enrich_data, format_timestamp

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """ETL Pipeline for processing sensor data"""
    
    def __init__(self):
        self.running = False
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'by_sensor_type': {}
        }
        
    def extract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from Kafka message"""
        try:
            # Validate data
            if not validate_sensor_data(data):
                logger.warning("Invalid data received, skipping extraction")
                return None
            
            # Parse timestamp
            timestamp = format_timestamp(data.get('timestamp'))
            
            extracted = {
                'sensor_id': data.get('sensor_id'),
                'sensor_type': data.get('sensor_type'),
                'timestamp': timestamp,
                'raw_data': data
            }
            
            logger.debug(f"Extracted data from sensor: {extracted['sensor_id']}")
            return extracted
            
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            return None
    
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform and normalize data"""
        try:
            if not data:
                return None
            
            sensor_type = data['sensor_type']
            raw_data = data['raw_data']
            
            # Create base transformed record
            transformed = {
                'sensor_id': data['sensor_id'],
                'sensor_type': sensor_type,
                'timestamp': data['timestamp'],
                'processed_at': datetime.utcnow()
            }
            
            # Transform based on sensor type
            if sensor_type == 'temperature':
                transformed['value'] = raw_data.get('temperature')
                transformed['unit'] = raw_data.get('unit', 'celsius')
                transformed['metric'] = 'temperature'
                
            elif sensor_type == 'humidity':
                transformed['value'] = raw_data.get('humidity')
                transformed['unit'] = raw_data.get('unit', 'percent')
                transformed['metric'] = 'humidity'
                
            elif sensor_type == 'soil_moisture':
                transformed['value'] = raw_data.get('soil_moisture')
                transformed['unit'] = raw_data.get('unit', 'percent')
                transformed['metric'] = 'soil_moisture'
                
            elif sensor_type == 'ph':
                transformed['value'] = raw_data.get('ph')
                transformed['unit'] = raw_data.get('unit', 'pH')
                transformed['metric'] = 'ph'
                
            elif sensor_type == 'rainfall':
                transformed['value'] = raw_data.get('rainfall')
                transformed['unit'] = raw_data.get('unit', 'mm')
                transformed['metric'] = 'rainfall'
                transformed['period'] = raw_data.get('period', 'last_hour')
                
            elif sensor_type == 'light':
                transformed['value'] = raw_data.get('light_intensity')
                transformed['unit'] = raw_data.get('unit', 'lux')
                transformed['metric'] = 'light_intensity'
                transformed['hour'] = raw_data.get('hour')
                
            elif sensor_type == 'wind':
                transformed['wind_speed'] = raw_data.get('wind_speed')
                transformed['wind_direction'] = raw_data.get('wind_direction')
                transformed['unit_speed'] = raw_data.get('unit_speed', 'km/h')
                transformed['unit_direction'] = raw_data.get('unit_direction', 'degrees')
                transformed['metric'] = 'wind'
                
            elif sensor_type == 'water_quality':
                transformed['ph'] = raw_data.get('ph')
                transformed['dissolved_oxygen'] = raw_data.get('dissolved_oxygen')
                transformed['turbidity'] = raw_data.get('turbidity')
                transformed['conductivity'] = raw_data.get('conductivity')
                transformed['metric'] = 'water_quality'
                
            elif sensor_type == 'gps':
                transformed['latitude'] = raw_data.get('latitude')
                transformed['longitude'] = raw_data.get('longitude')
                transformed['altitude'] = raw_data.get('altitude')
                transformed['speed'] = raw_data.get('speed')
                transformed['metric'] = 'gps'
                
            elif sensor_type == 'animal':
                transformed['animal_id'] = raw_data.get('animal_id')
                transformed['activity_level'] = raw_data.get('activity_level')
                transformed['body_temperature'] = raw_data.get('body_temperature')
                transformed['heart_rate'] = raw_data.get('heart_rate')
                transformed['location_zone'] = raw_data.get('location_zone')
                transformed['health_status'] = raw_data.get('health_status')
                transformed['metric'] = 'animal'
            
            else:
                # Generic transformation for unknown sensor types
                transformed['data'] = raw_data
                transformed['metric'] = sensor_type
            
            # Add data quality score
            transformed['data_quality'] = raw_data.get('data_quality', 1.0)
            
            logger.debug(f"Transformed data for sensor: {transformed['sensor_id']}")
            return transformed
            
        except Exception as e:
            logger.error(f"Transformation error: {e}")
            return None
    
    def load(self, data: Dict[str, Any], loaders: List) -> bool:
        """Load data to all configured databases"""
        try:
            if not data:
                return False
            
            success = True
            
            # Load to each database
            for loader in loaders:
                try:
                    result = loader.load(data)
                    if not result:
                        logger.warning(f"Failed to load data to {loader.__class__.__name__}")
                        success = False
                    else:
                        logger.debug(f"Successfully loaded to {loader.__class__.__name__}")
                except Exception as e:
                    logger.error(f"Error loading to {loader.__class__.__name__}: {e}")
                    success = False
            
            return success
            
        except Exception as e:
            logger.error(f"Load error: {e}")
            return False
    
    def process(self, data: Dict[str, Any], loaders: List) -> bool:
        """Complete ETL process: Extract, Transform, Load"""
        try:
            # Extract
            extracted = self.extract(data)
            if not extracted:
                self.stats['failed'] += 1
                return False
            
            # Transform
            transformed = self.transform(extracted)
            if not transformed:
                self.stats['failed'] += 1
                return False
            
            # Load
            success = self.load(transformed, loaders)
            
            # Update statistics
            self.stats['total_processed'] += 1
            sensor_type = transformed['sensor_type']
            
            if success:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1
            
            # Update sensor type stats
            if sensor_type not in self.stats['by_sensor_type']:
                self.stats['by_sensor_type'][sensor_type] = 0
            self.stats['by_sensor_type'][sensor_type] += 1
            
            logger.info(f"✓ Processed {sensor_type} data from sensor {transformed['sensor_id']}")
            return success
            
        except Exception as e:
            logger.error(f"ETL processing error: {e}")
            self.stats['failed'] += 1
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'by_sensor_type': {}
        }


def main():
    """Main function for testing ETL pipeline"""
    # Create ETL pipeline
    etl = ETLPipeline()
    
    # Test data
    test_data = {
        'sensor_type': 'temperature',
        'sensor_id': 'test_sensor_001',
        'temperature': 25.5,
        'unit': 'celsius',
        'timestamp': '2024-01-01T12:00:00',
        'data_quality': 1.0
    }
    
    print("Testing ETL Pipeline...")
    print(f"Input data: {test_data}\n")
    
    # Test extraction
    extracted = etl.extract(test_data)
    print(f"Extracted: {extracted}\n")
    
    # Test transformation
    transformed = etl.transform(extracted)
    print(f"Transformed: {transformed}\n")
    
    # Show statistics
    stats = etl.get_stats()
    print(f"Statistics: {stats}")


if __name__ == "__main__":
    main()