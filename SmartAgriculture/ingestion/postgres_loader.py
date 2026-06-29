"""
PostgreSQL Loader - Loads sensor data into PostgreSQL
"""
import os
import json
import logging
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv

import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import DictCursor

from ingestion.utils import enrich_data

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PostgresLoader:
    """PostgreSQL data loader for sensor data"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        
        # Database configuration
        self.host = os.getenv('POSTGRES_HOST', 'localhost')
        self.port = os.getenv('POSTGRES_PORT', '5432')
        self.database = os.getenv('POSTGRES_DB', 'agriculture')
        self.user = os.getenv('POSTGRES_USER', 'admin')
        self.password = os.getenv('POSTGRES_PASSWORD', 'admin123')
        
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor(cursor_factory=DictCursor)
            logger.info(f"✓ Connected to PostgreSQL: {self.host}:{self.port}/{self.database}")
            return True
        except OperationalError as e:
            logger.error(f"✗ Failed to connect to PostgreSQL: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ PostgreSQL connection error: {e}")
            return False
    
    def ensure_table_exists(self, sensor_type: str):
        """Ensure the table for a sensor type exists"""
        try:
            # Create table if not exists (generic sensor data table)
            create_table_query = """
            CREATE TABLE IF NOT EXISTS sensor_data (
                id SERIAL PRIMARY KEY,
                sensor_id VARCHAR(255) NOT NULL,
                sensor_type VARCHAR(100) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                processed_at TIMESTAMP,
                metric VARCHAR(100),
                value FLOAT,
                unit VARCHAR(50),
                data_quality FLOAT DEFAULT 1.0,
                raw_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_sensor_data_sensor_id 
            ON sensor_data(sensor_id);
            
            CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp 
            ON sensor_data(timestamp);
            
            CREATE INDEX IF NOT EXISTS idx_sensor_data_type 
            ON sensor_data(sensor_type);
            """
            
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logger.debug(f"✓ Table 'sensor_data' ready")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to create table: {e}")
            self.connection.rollback()
            return False
    
    def load(self, data: Dict[str, Any]) -> bool:
        """Load data to PostgreSQL"""
        try:
            # Connect if not connected
            if not self.connection:
                if not self.connect():
                    return False
            
            # Ensure table exists
            sensor_type = data.get('sensor_type', 'unknown')
            if not self.ensure_table_exists(sensor_type):
                return False
            
            # Prepare data for insertion
            timestamp = data.get('timestamp')
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()
            
            # Build the data dictionary based on sensor type
            insert_data = {
                'sensor_id': data.get('sensor_id'),
                'sensor_type': data.get('sensor_type'),
                'timestamp': timestamp,
                'processed_at': data.get('processed_at'),
                'metric': data.get('metric'),
                'value': data.get('value'),
                'unit': data.get('unit'),
                'data_quality': data.get('data_quality', 1.0),
                'raw_data': json.dumps(data)
            }
            
            # Insert query
            insert_query = """
            INSERT INTO sensor_data 
            (sensor_id, sensor_type, timestamp, processed_at, metric, value, unit, data_quality, raw_data)
            VALUES (%(sensor_id)s, %(sensor_type)s, %(timestamp)s, %(processed_at)s, 
                    %(metric)s, %(value)s, %(unit)s, %(data_quality)s, %(raw_data)s)
            """
            
            self.cursor.execute(insert_query, insert_data)
            self.connection.commit()
            
            logger.debug(f"✓ Loaded {sensor_type} data to PostgreSQL")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to load data to PostgreSQL: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def close(self):
        """Close database connection"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            logger.info("✓ PostgreSQL connection closed")
        except Exception as e:
            logger.error(f"Error closing PostgreSQL connection: {e}")
    
    def get_stats(self):
        """Get statistics from database"""
        try:
            if not self.connection:
                if not self.connect():
                    return None
            
            self.cursor.execute("""
                SELECT 
                    sensor_type,
                    COUNT(*) as count,
                    MIN(timestamp) as earliest,
                    MAX(timestamp) as latest
                FROM sensor_data
                GROUP BY sensor_type
                ORDER BY count DESC
            """)
            
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return None


def main():
    """Main function for testing"""
    loader = PostgresLoader()
    
    # Test connection
    if not loader.connect():
        print("Failed to connect to PostgreSQL")
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
    
    print("\nTesting PostgreSQL Loader...")
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