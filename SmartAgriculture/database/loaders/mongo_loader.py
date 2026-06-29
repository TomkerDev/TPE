"""
MongoDB Loader
Loads semi-structured data into MongoDB
"""
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from bson import ObjectId

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MongoLoader:
    """MongoDB data loader for semi-structured data"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collections = {}
        
        # Database configuration
        self.host = os.getenv('MONGO_HOST', 'localhost')
        self.port = int(os.getenv('MONGO_PORT', '27017'))
        self.database_name = os.getenv('MONGO_DB', 'agriculture')
        
    def connect(self) -> bool:
        """
        Connect to MongoDB database
        
        Returns:
            True if connected successfully
        """
        try:
            self.client = MongoClient(
                host=self.host,
                port=self.port,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            self.client.server_info()
            
            self.db = self.client[self.database_name]
            
            # Initialize collections
            from database.mongodb.collections import MongoDBCollections
            collections_manager = MongoDBCollections(self.db)
            collections_manager.create_all_collections()
            self.collections = collections_manager.collections
            
            logger.info(f"✓ Connected to MongoDB: {self.host}:{self.port}/{self.database_name}")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"✗ Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ MongoDB connection error: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        try:
            if self.client:
                self.client.close()
                logger.info("✓ MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")
    
    def get_collection(self, name: str):
        """
        Get a collection
        
        Args:
            name: Collection name
            
        Returns:
            MongoDB collection object
        """
        if not self.db:
            if not self.connect():
                return None
        return self.db[name]
    
    def insert_raw_data(self, data: Dict[str, Any]) -> bool:
        """
        Insert raw sensor data
        
        Args:
            data: Raw data dictionary
            
        Returns:
            True if inserted successfully
        """
        try:
            collection = self.get_collection('raw_data')
            if not collection:
                return False
            
            # Add metadata
            data['created_at'] = datetime.utcnow()
            data['processed'] = False
            
            result = collection.insert_one(data)
            logger.debug(f"✓ Inserted raw data: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to insert raw data: {e}")
            return False
    
    def insert_image(self, image_data: Dict[str, Any]) -> bool:
        """
        Insert image metadata
        
        Args:
            image_data: Image data dictionary
            
        Returns:
            True if inserted successfully
        """
        try:
            collection = self.get_collection('images')
            if not collection:
                return False
            
            # Add metadata
            image_data['created_at'] = datetime.utcnow()
            
            result = collection.insert_one(image_data)
            logger.debug(f"✓ Inserted image: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to insert image: {e}")
            return False
    
    def insert_weather(self, weather_data: Dict[str, Any]) -> bool:
        """
        Insert weather data
        
        Args:
            weather_data: Weather data dictionary
            
        Returns:
            True if inserted successfully
        """
        try:
            collection = self.get_collection('weather')
            if not collection:
                return False
            
            # Add metadata
            weather_data['created_at'] = datetime.utcnow()
            
            result = collection.insert_one(weather_data)
            logger.debug(f"✓ Inserted weather data: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to insert weather data: {e}")
            return False
    
    def insert_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Insert flexible metadata
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            True if inserted successfully
        """
        try:
            collection = self.get_collection('metadata')
            if not collection:
                return False
            
            # Add metadata
            metadata['created_at'] = datetime.utcnow()
            
            result = collection.insert_one(metadata)
            logger.debug(f"✓ Inserted metadata: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to insert metadata: {e}")
            return False
    
    def insert_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Insert alert
        
        Args:
            alert_data: Alert data dictionary
            
        Returns:
            True if inserted successfully
        """
        try:
            collection = self.get_collection('alerts')
            if not collection:
                return False
            
            # Add metadata
            alert_data['created_at'] = datetime.utcnow()
            alert_data['resolved'] = False
            
            result = collection.insert_one(alert_data)
            logger.debug(f"✓ Inserted alert: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to insert alert: {e}")
            return False
    
    def insert_batch_raw_data(self, data_list: List[Dict[str, Any]]) -> bool:
        """
        Insert batch of raw data
        
        Args:
            data_list: List of data dictionaries
            
        Returns:
            True if all inserted successfully
        """
        try:
            collection = self.get_collection('raw_data')
            if not collection:
                return False
            
            # Add metadata to all
            for data in data_list:
                data['created_at'] = datetime.utcnow()
                data['processed'] = False
            
            result = collection.insert_many(data_list)
            logger.debug(f"✓ Inserted {len(result.inserted_ids)} raw data items")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to insert batch raw data: {e}")
            return False
    
    def update_processed_status(self, document_id: str, processed: bool = True) -> bool:
        """
        Update processed status of raw data
        
        Args:
            document_id: MongoDB document ID
            processed: Processing status
            
        Returns:
            True if updated successfully
        """
        try:
            collection = self.get_collection('raw_data')
            if not collection:
                return False
            
            from bson import ObjectId
            result = collection.update_one(
                {'_id': ObjectId(document_id)},
                {'$set': {'processed': processed}}
            )
            
            logger.debug(f"✓ Updated processed status: {document_id}")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"✗ Failed to update processed status: {e}")
            return False
    
    def get_unprocessed_data(self, limit: int = 100) -> List[Dict]:
        """
        Get unprocessed raw data
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of unprocessed data dictionaries
        """
        try:
            collection = self.get_collection('raw_data')
            if not collection:
                return []
            
            results = collection.find({'processed': False}).limit(limit)
            return [dict(doc) for doc in results]
            
        except Exception as e:
            logger.error(f"Failed to get unprocessed data: {e}")
            return []
    
    def get_sensor_data(self, sensor_id: str, limit: int = 100) -> List[Dict]:
        """
        Get data for a specific sensor
        
        Args:
            sensor_id: Sensor ID
            limit: Maximum number of results
            
        Returns:
            List of data dictionaries
        """
        try:
            collection = self.get_collection('raw_data')
            if not collection:
                return []
            
            results = collection.find({'sensor_id': sensor_id}).sort('timestamp', DESCENDING).limit(limit)
            return [dict(doc) for doc in results]
            
        except Exception as e:
            logger.error(f"Failed to get sensor data: {e}")
            return []
    
    def get_images_by_sensor(self, sensor_id: str, limit: int = 50) -> List[Dict]:
        """
        Get images by sensor
        
        Args:
            sensor_id: Sensor ID
            limit: Maximum number of results
            
        Returns:
            List of image dictionaries
        """
        try:
            collection = self.get_collection('images')
            if not collection:
                return []
            
            results = collection.find({'sensor': sensor_id}).sort('date', DESCENDING).limit(limit)
            return [dict(doc) for doc in results]
            
        except Exception as e:
            logger.error(f"Failed to get images: {e}")
            return []
    
    def get_weather_by_location(self, location: str, 
                                start_time: Optional[datetime] = None,
                                end_time: Optional[datetime] = None,
                                limit: int = 100) -> List[Dict]:
        """
        Get weather data by location
        
        Args:
            location: Location identifier
            start_time: Start timestamp
            end_time: End timestamp
            limit: Maximum number of results
            
        Returns:
            List of weather dictionaries
        """
        try:
            collection = self.get_collection('weather')
            if not collection:
                return []
            
            query = {'location': location}
            
            if start_time or end_time:
                time_filter = {}
                if start_time:
                    time_filter['$gte'] = start_time
                if end_time:
                    time_filter['$lte'] = end_time
                query['timestamp'] = time_filter
            
            results = collection.find(query).sort('timestamp', DESCENDING).limit(limit)
            return [dict(doc) for doc in results]
            
        except Exception as e:
            logger.error(f"Failed to get weather data: {e}")
            return []
    
    def get_metadata_by_sensor(self, sensor_id: str, category: str = None) -> List[Dict]:
        """
        Get metadata by sensor
        
        Args:
            sensor_id: Sensor ID
            category: Optional category filter
            
        Returns:
            List of metadata dictionaries
        """
        try:
            collection = self.get_collection('metadata')
            if not collection:
                return []
            
            query = {'sensor_id': sensor_id}
            if category:
                query['category'] = category
            
            results = collection.find(query)
            return [dict(doc) for doc in results]
            
        except Exception as e:
            logger.error(f"Failed to get metadata: {e}")
            return []
    
    def get_active_alerts(self, limit: int = 50) -> List[Dict]:
        """
        Get active (unresolved) alerts
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of alert dictionaries
        """
        try:
            collection = self.get_collection('alerts')
            if not collection:
                return []
            
            results = collection.find({'resolved': False}).sort('created_at', DESCENDING).limit(limit)
            return [dict(doc) for doc in results]
            
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        Mark alert as resolved
        
        Args:
            alert_id: Alert document ID
            
        Returns:
            True if updated successfully
        """
        try:
            collection = self.get_collection('alerts')
            if not collection:
                return False
            
            from bson import ObjectId
            result = collection.update_one(
                {'_id': ObjectId(alert_id)},
                {'$set': {'resolved': True, 'resolved_at': datetime.utcnow()}}
            )
            
            logger.debug(f"✓ Resolved alert: {alert_id}")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"✗ Failed to resolve alert: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            if not self.db:
                if not self.connect():
                    return {}
            
            stats = {}
            
            # Count documents in each collection
            for name in ['sensors', 'raw_data', 'images', 'weather', 'metadata', 'alerts']:
                collection = self.db[name]
                count = collection.count_documents({})
                stats[name] = count
            
            # Database stats
            db_stats = self.db.command('dbStats')
            stats['database_size_mb'] = db_stats.get('dataSize', 0) / (1024 * 1024)
            stats['storage_size_mb'] = db_stats.get('storageSize', 0) / (1024 * 1024)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}


def insert_raw_data(data: Dict[str, Any]) -> bool:
    """
    Convenience function to insert raw data
    
    Args:
        data: Raw data dictionary
        
    Returns:
        True if inserted successfully
    """
    loader = MongoLoader()
    loader.connect()
    result = loader.insert_raw_data(data)
    loader.close()
    return result


def insert_image_data(data: Dict[str, Any]) -> bool:
    """
    Convenience function to insert image data
    
    Args:
        data: Image data dictionary
        
    Returns:
        True if inserted successfully
    """
    loader = MongoLoader()
    loader.connect()
    result = loader.insert_image(data)
    loader.close()
    return result