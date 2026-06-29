"""
MongoDB Collections and Indexes for Smart Agriculture System
Defines collections, indexes, and data models for MongoDB
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MongoDBCollections:
    """Manages MongoDB collections and indexes"""
    
    def __init__(self, db):
        """
        Initialize MongoDB collections manager
        
        Args:
            db: MongoDB database object
        """
        self.db = db
        self.collections = {}
        
    def create_all_collections(self):
        """Create all required collections with indexes"""
        try:
            self.create_sensors_collection()
            self.create_raw_data_collection()
            self.create_images_collection()
            self.create_weather_collection()
            self.create_metadata_collection()
            self.create_alerts_collection()
            
            logger.info("✓ All MongoDB collections created")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to create collections: {e}")
            return False
    
    def create_sensors_collection(self):
        """Create sensors collection"""
        collection = self.db.sensors
        
        # Create indexes
        collection.create_index("sensor_id", unique=True)
        collection.create_index("type")
        collection.create_index("protocol")
        collection.create_index("status")
        collection.create_index([("location", "2dsphere")])  # Geospatial index
        
        self.collections['sensors'] = collection
        logger.debug("✓ Collection 'sensors' created")
    
    def create_raw_data_collection(self):
        """Create raw_data collection for unprocessed sensor data"""
        collection = self.db.raw_data
        
        # Create indexes
        collection.create_index("sensor_id")
        collection.create_index("timestamp")
        collection.create_index("sensor_type")
        collection.create_index([("sensor_id", 1), ("timestamp", -1)])
        collection.create_index("processed")
        
        self.collections['raw_data'] = collection
        logger.debug("✓ Collection 'raw_data' created")
    
    def create_images_collection(self):
        """Create images collection for drone/field images"""
        collection = self.db.images
        
        # Create indexes
        collection.create_index("sensor")
        collection.create_index("date")
        collection.create_index("type")
        collection.create_index([("sensor", 1), ("date", -1)])
        
        self.collections['images'] = collection
        logger.debug("✓ Collection 'images' created")
    
    def create_weather_collection(self):
        """Create weather collection for weather data"""
        collection = self.db.weather
        
        # Create indexes
        collection.create_index("timestamp")
        collection.create_index("location")
        collection.create_index([("location", 1), ("timestamp", -1)])
        
        self.collections['weather'] = collection
        logger.debug("✓ Collection 'weather' created")
    
    def create_metadata_collection(self):
        """Create metadata collection for flexible metadata storage"""
        collection = self.db.metadata
        
        # Create indexes
        collection.create_index("sensor_id")
        collection.create_index("field_id")
        collection.create_index("category")
        collection.create_index([("sensor_id", 1), ("category", 1)])
        
        self.collections['metadata'] = collection
        logger.debug("✓ Collection 'metadata' created")
    
    def create_alerts_collection(self):
        """Create alerts collection for system alerts"""
        collection = self.db.alerts
        
        # Create indexes
        collection.create_index("sensor_id")
        collection.create_index("severity")
        collection.create_index("resolved")
        collection.create_index("created_at")
        collection.create_index([("sensor_id", 1), ("resolved", 1), ("created_at", -1)])
        
        self.collections['alerts'] = collection
        logger.debug("✓ Collection 'alerts' created")
    
    def get_collection(self, name: str):
        """
        Get a collection by name
        
        Args:
            name: Collection name
            
        Returns:
            MongoDB collection object
        """
        return self.collections.get(name)
    
    def drop_all_collections(self):
        """Drop all collections (use with caution!)"""
        try:
            for name, collection in self.collections.items():
                collection.drop()
                logger.warning(f"⚠ Dropped collection: {name}")
            
            self.collections = {}
            return True
            
        except Exception as e:
            logger.error(f"Failed to drop collections: {e}")
            return False


# Schema definitions for documentation
SCHEMA_DEFINITIONS = {
    'sensors': {
        'description': 'Sensor registry and metadata',
        'fields': {
            'sensor_id': 'string (unique) - Primary identifier',
            'type': 'string - Sensor type (temperature, humidity, etc.)',
            'manufacturer': 'string - Sensor manufacturer',
            'protocol': 'string - Communication protocol (MQTT, LoRaWAN, etc.)',
            'latitude': 'float - GPS latitude',
            'longitude': 'float - GPS longitude',
            'installation_date': 'date - Installation date',
            'status': 'string - Sensor status (active, inactive, maintenance)',
            'location': 'GeoJSON - Geospatial location',
            'field_id': 'integer - Associated field ID',
            'created_at': 'datetime - Creation timestamp',
            'updated_at': 'datetime - Last update timestamp'
        },
        'indexes': [
            {'field': 'sensor_id', 'unique': True},
            {'field': 'type'},
            {'field': 'protocol'},
            {'field': 'location', 'type': '2dsphere'}
        ]
    },
    
    'raw_data': {
        'description': 'Raw unprocessed sensor data',
        'fields': {
            'sensor_id': 'string - Sensor identifier',
            'sensor_type': 'string - Type of sensor',
            'timestamp': 'datetime - Reading timestamp',
            'value': 'float - Sensor value',
            'unit': 'string - Unit of measurement',
            'data': 'object - Complete raw data payload',
            'processed': 'boolean - Processing status',
            'created_at': 'datetime - Insertion timestamp'
        },
        'indexes': [
            {'field': 'sensor_id'},
            {'field': 'timestamp'},
            {'field': [('sensor_id', 1), ('timestamp', -1)]}
        ]
    },
    
    'images': {
        'description': 'Drone and field images',
        'fields': {
            'sensor': 'string - Drone/camera sensor ID',
            'date': 'string - Capture date',
            'path': 'string - File path/URL',
            'type': 'string - Image type (RGB, IR, etc.)',
            'size': 'integer - File size in bytes',
            'resolution': 'string - Image resolution',
            'metadata': 'object - EXIF and other metadata',
            'created_at': 'datetime - Upload timestamp'
        },
        'indexes': [
            {'field': 'sensor'},
            {'field': 'date'},
            {'field': [('sensor', 1), ('date', -1)]}
        ]
    },
    
    'weather': {
        'description': 'Weather data from external sources',
        'fields': {
            'location': 'string - Location identifier',
            'timestamp': 'datetime - Reading timestamp',
            'temperature': 'float - Temperature in °C',
            'humidity': 'float - Humidity percentage',
            'wind': 'float - Wind speed km/h',
            'rain': 'float - Rainfall mm',
            'pressure': 'float - Atmospheric pressure hPa',
            'source': 'string - Data source',
            'created_at': 'datetime - Insertion timestamp'
        },
        'indexes': [
            {'field': 'timestamp'},
            {'field': 'location'},
            {'field': [('location', 1), ('timestamp', -1)]}
        ]
    },
    
    'metadata': {
        'description': 'Flexible metadata storage',
        'fields': {
            'sensor_id': 'string - Associated sensor',
            'field_id': 'integer - Associated field',
            'category': 'string - Metadata category',
            'key': 'string - Metadata key',
            'value': 'mixed - Metadata value',
            'data': 'object - Complete metadata object',
            'created_at': 'datetime - Creation timestamp'
        },
        'indexes': [
            {'field': 'sensor_id'},
            {'field': 'field_id'},
            {'field': 'category'},
            {'field': [('sensor_id', 1), ('category', 1)]}
        ]
    },
    
    'alerts': {
        'description': 'System alerts and notifications',
        'fields': {
            'sensor_id': 'string - Related sensor',
            'alert_type': 'string - Type of alert',
            'severity': 'string - Severity (low, medium, high, critical)',
            'message': 'string - Alert message',
            'resolved': 'boolean - Resolution status',
            'resolved_at': 'datetime - Resolution timestamp',
            'created_at': 'datetime - Creation timestamp'
        },
        'indexes': [
            {'field': 'sensor_id'},
            {'field': 'severity'},
            {'field': 'resolved'},
            {'field': 'created_at'},
            {'field': [('sensor_id', 1), ('resolved', 1), ('created_at', -1)]}
        ]
    }
}


def get_collection_schema(collection_name: str) -> Dict[str, Any]:
    """
    Get schema definition for a collection
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Schema definition dictionary
    """
    return SCHEMA_DEFINITIONS.get(collection_name)


def get_all_schemas() -> Dict[str, Dict[str, Any]]:
    """Get all collection schemas"""
    return SCHEMA_DEFINITIONS.copy()


def initialize_collections(db) -> MongoDBCollections:
    """
    Initialize all MongoDB collections
    
    Args:
        db: MongoDB database object
        
    Returns:
        MongoDBCollections manager
    """
    manager = MongoDBCollections(db)
    manager.create_all_collections()
    return manager