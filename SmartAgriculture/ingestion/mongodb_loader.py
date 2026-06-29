"""
MongoDB Loader - Loads sensor data into MongoDB
"""
import os
import json
import logging
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

from ingestion.utils import enrich_data

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MongoDBLoader:
    """MongoDB data loader for sensor data"""
    
    def __init__(self):
        self.client = None
        self.db = None
        
        # Database configuration
        self.host = os.getenv('MONGO_HOST', 'localhost')
        self.port = int(os.getenv('MONGO_PORT', 27017))
        self.database_name = os.getenv('MONGO_DB', 'agriculture')
        
    def connect(self):
        """Connect to MongoDB database"""
        try:
            # Create MongoDB client
            self.client = MongoClient(
                f'mongodb://{self.host}:{self.port}/',
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database
            self.db = self.client[self.database_name]
            
            logger.info(f"✓ Connected to MongoDB: {self.host}:{self.port}/{self.database_name}")
            return True
        except ConnectionFailure as e:
            logger.error(f"✗ Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ MongoDB connection error: {e}")
            return False
    
    def ensure_collection_exists(self, sensor_type: str):
        """Ensure the collection for a sensor type exists"""
        try:
            # Get or create collection
            collection_name = f"sensor_{sensor_type}"
            
            if collection_name not in self.db.list_collection_names():
                # Create collection with indexes
                collection = self.db.create_collection(collection_name)
                
                # Create indexes
                collection.create_index("sensor_id")
                collection.create_index("timestamp")
                collection.create_index([("timestamp", -1)])
                collection.create_index("sensor_type")
                
                logger.debug(f"✓ Collection '{collection_name}' created with indexes")
            else:
                logger.debug(f"✓ Collection '{collection_name}' exists")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to create collection: {e}")
            return False
    
    def load(self, data: Dict[str, Any]) -> bool:
        """Load data to MongoDB"""
        try:
            # Connect if not connected
            if not self.client:
                if not self.connect():
                    return False
            
            sensor_type = data.get('sensor_type', 'unknown')
            
            # Ensure collection exists
            if not self.ensure_collection_exists(sensor_type):
                return False
            
            # Get collection
            collection = self.db[f"sensor_{sensor_type}"]
            
            # Prepare document
            document = data.copy()
            
            # Convert datetime objects to ISO format strings for MongoDB
            for key, value in document.items():
                if isinstance(value, datetime):
                    document[key] = value.isoformat()
            
            # Insert document
            result = collection.insert_one(document)
            
            logger.debug(f"✓ Loaded {sensor_type} data to MongoDB (ID: {result.inserted_id})")
            return True
            
        except PyMongoError as e:
            logger.error(f"✗ Failed to load data to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ MongoDB error: {e}")
            return False
    
    def load_batch(self, data_list: list) -> bool:
        """Load multiple documents in batch"""
        try:
            if not self.client:
                if not self.connect():
                    return False
            
            if not data_list:
                return True
            
            # Group by sensor type
            from collections import defaultdict
            grouped = defaultdict(list)
            
            for data in data_list:
                sensor_type = data.get('sensor_type', 'unknown')
                
                # Prepare document
                document = data.copy()
                for key, value in document.items():
                    if isinstance(value, datetime):
                        document[key] = value.isoformat()
                
                grouped[sensor_type].append(document)
            
            # Insert each group
            success = True
            for sensor_type, documents in grouped.items():
                try:
                    collection = self.db[f"sensor_{sensor_type}"]
                    result = collection.insert_many(documents)
                    logger.debug(f"✓ Inserted {len(result.inserted_ids)} documents to {sensor_type}")
                except Exception as e:
                    logger.error(f"✗ Failed to insert batch for {sensor_type}: {e}")
                    success = False
            
            return success
            
        except Exception as e:
            logger.error(f"✗ Batch insert error: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        try:
            if self.client:
                self.client.close()
                logger.info("✓ MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")
    
    def get_stats(self):
        """Get statistics from database"""
        try:
            if not self.client:
                if not self.connect():
                    return None
            
            stats = []
            for collection_name in self.db.list_collection_names():
                if collection_name.startswith('sensor_'):
                    sensor_type = collection_name.replace('sensor_', '')
                    count = self.db[collection_name].count_documents({})
                    
                    # Get earliest and latest timestamps
                    earliest = self.db[collection_name].find_one(
                        {}, 
                        sort=[("timestamp", 1)]
                    )
                    latest = self.db[collection_name].find_one(
                        {}, 
                        sort=[("timestamp", -1)]
                    )
                    
                    stats.append({
                        'sensor_type': sensor_type,
                        'count': count,
                        'earliest': earliest.get('timestamp') if earliest else None,
                        'latest': latest.get('timestamp') if latest else None
                    })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return None


def main():
    """Main function for testing"""
    loader = MongoDBLoader()
    
    # Test connection
    if not loader.connect():
        print("Failed to connect to MongoDB")
        return
    
    # Test data
    test_data = {
        'sensor_type': 'temperature',
        'sensor_id': 'test_sensor_001',
        'timestamp': datetime.utcnow(),
        'processed_at': datetime.utcnow(),
        'metric': 'temperature',
        'value': 25.5,
        'unit': 'celsius',
        'data_quality': 1.0
    }
    
    print("\nTesting MongoDB Loader...")
    print(f"Test data: {test_data}\n")
    
    # Test loading
    result = loader.load(test_data)
    print(f"Load result: {'Success' if result else 'Failed'}\n")
    
    # Get stats
    stats = loader.get_stats()
    if stats:
        print("Database statistics:")
        for stat in stats:
            print(f"  {stat['sensor_type']}: {stat['count']} records")
    
    # Close connection
    loader.close()


if __name__ == "__main__":
    main()