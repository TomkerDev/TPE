"""
TimescaleDB Loader - Loads time-series sensor data into TimescaleDB
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


class TimescaleDBLoader:
    """TimescaleDB data loader for time-series sensor data"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        
        # Database configuration
        self.host = os.getenv('TIMESCALE_HOST', 'localhost')
        self.port = os.getenv('TIMESCALE_PORT', '5433')
        self.database = os.getenv('TIMESCALE_DB', 'agriculture_ts')
        self.user = os.getenv('POSTGRES_USER', 'admin')
        self.password = os.getenv('POSTGRES_PASSWORD', 'admin123')
        
    def connect(self):
        """Connect to TimescaleDB database"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor(cursor_factory=DictCursor)
            
            # Enable TimescaleDB extension if not already enabled
            self.cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
            self.connection.commit()
            
            logger.info(f"✓ Connected to TimescaleDB: {self.host}:{self.port}/{self.database}")
            return True
        except OperationalError as e:
            logger.error(f"✗ Failed to connect to TimescaleDB: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ TimescaleDB connection error: {e}")
            return False
    
    def ensure_hypertable_exists(self, sensor_type: str):
        """Ensure the hypertable for a sensor type exists"""
        try:
            # Create hypertable if not exists
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {sensor_type}_metrics (
                time TIMESTAMP NOT NULL,
                sensor_id VARCHAR(255) NOT NULL,
                value FLOAT,
                unit VARCHAR(50),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Create hypertable
            SELECT create_hypertable('{sensor_type}_metrics', 'time', if_not_exists => TRUE);
            
            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_{sensor_type}_sensor_id 
            ON {sensor_type}_metrics(sensor_id);
            
            CREATE INDEX IF NOT EXISTS idx_{sensor_type}_time 
            ON {sensor_type}_metrics(time DESC);
            """
            
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logger.debug(f"✓ Hypertable '{sensor_type}_metrics' ready")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to create hypertable: {e}")
            self.connection.rollback()
            return False
    
    def load(self, data: Dict[str, Any]) -> bool:
        """Load data to TimescaleDB"""
        try:
            # Connect if not connected
            if not self.connection:
                if not self.connect():
                    return False
            
            sensor_type = data.get('sensor_type', 'unknown')
            
            # Ensure hypertable exists
            if not self.ensure_hypertable_exists(sensor_type):
                return False
            
            # Prepare timestamp
            timestamp = data.get('timestamp')
            if isinstance(timestamp, datetime):
                timestamp = timestamp
            else:
                timestamp = datetime.utcnow()
            
            # Prepare metadata (store all additional data as JSON)
            metadata = {
                'sensor_id': data.get('sensor_id'),
                'sensor_type': sensor_type,
                'processed_at': data.get('processed_at').isoformat() if isinstance(data.get('processed_at'), datetime) else data.get('processed_at'),
                'data_quality': data.get('data_quality', 1.0),
                'metric': data.get('metric')
            }
            
            # Add sensor-specific fields to metadata
            for key, value in data.items():
                if key not in ['timestamp', 'sensor_id', 'sensor_type', 'processed_at', 'data_quality', 'metric']:
                    metadata[key] = value
            
            # Insert data
            insert_query = f"""
            INSERT INTO {sensor_type}_metrics 
            (time, sensor_id, value, unit, metadata)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(insert_query, (
                timestamp,
                data.get('sensor_id'),
                data.get('value'),
                data.get('unit'),
                json.dumps(metadata)
            ))
            
            self.connection.commit()
            
            logger.debug(f"✓ Loaded {sensor_type} time-series data to TimescaleDB")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to load data to TimescaleDB: {e}")
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
            logger.info("✓ TimescaleDB connection closed")
        except Exception as e:
            logger.error(f"Error closing TimescaleDB connection: {e}")
    
    def get_stats(self):
        """Get statistics from database"""
        try:
            if not self.connection:
                if not self.connect():
                    return None
            
            # Get list of hypertables
            self.cursor.execute("""
                SELECT hypertable_name 
                FROM timescaledb_information.hypertables 
                WHERE hypertable_name LIKE '%_metrics'
            """)
            
            hypertables = [row[0] for row in self.cursor.fetchall()]
            
            stats = []
            for table in hypertables:
                sensor_type = table.replace('_metrics', '')
                self.cursor.execute(f"""
                    SELECT 
                        COUNT(*) as count,
                        MIN(time) as earliest,
                        MAX(time) as latest
                    FROM {table}
                """)
                result = self.cursor.fetchone()
                if result:
                    stats.append({
                        'sensor_type': sensor_type,
                        'count': result[0],
                        'earliest': result[1],
                        'latest': result[2]
                    })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return None


def main():
    """Main function for testing"""
    loader = TimescaleDBLoader()
    
    # Test connection
    if not loader.connect():
        print("Failed to connect to TimescaleDB")
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
    
    print("\nTesting TimescaleDB Loader...")
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