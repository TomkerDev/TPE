"""
TimescaleDB Loader
Loads time-series data into TimescaleDB
"""
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import DictCursor

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TimescaleLoader:
    """TimescaleDB data loader for time-series data"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        
        # Database configuration
        self.host = os.getenv('TIMESCALE_HOST', 'localhost')
        self.port = os.getenv('TIMESCALE_PORT', '5433')
        self.database = os.getenv('TIMESCALE_DB', 'agriculture_ts')
        self.user = os.getenv('POSTGRES_USER', 'admin')
        self.password = os.getenv('POSTGRES_PASSWORD', 'admin123')
        
    def connect(self) -> bool:
        """
        Connect to TimescaleDB database
        
        Returns:
            True if connected successfully
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor(cursor_factory=DictCursor)
            
            # Enable TimescaleDB extension
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
    
    def insert_observation(self, observation_data: Dict[str, Any]) -> bool:
        """
        Insert time-series observation
        
        Args:
            observation_data: Observation data dictionary
            
        Returns:
            True if inserted successfully
        """
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            query = """
            INSERT INTO observations (
                sensor_id, sensor_type, value, unit, timestamp, quality, outlier, metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(query, (
                observation_data.get('sensor_id'),
                observation_data.get('sensor_type'),
                observation_data.get('value'),
                observation_data.get('unit'),
                observation_data.get('timestamp'),
                observation_data.get('quality', 100),
                observation_data.get('outlier', False),
                psycopg2.extras.Json(observation_data.get('metadata', {}))
            ))
            
            self.connection.commit()
            logger.debug(f"✓ Inserted observation for: {observation_data.get('sensor_id')}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to insert observation: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def insert_batch_observations(self, observations: List[Dict[str, Any]]) -> bool:
        """
        Insert batch of observations
        
        Args:
            observations: List of observation dictionaries
            
        Returns:
            True if all inserted successfully
        """
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            query = """
            INSERT INTO observations (
                sensor_id, sensor_type, value, unit, timestamp, quality, outlier, metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            data_tuples = [
                (
                    obs.get('sensor_id'),
                    obs.get('sensor_type'),
                    obs.get('value'),
                    obs.get('unit'),
                    obs.get('timestamp'),
                    obs.get('quality', 100),
                    obs.get('outlier', False),
                    psycopg2.extras.Json(obs.get('metadata', {}))
                )
                for obs in observations
            ]
            
            self.cursor.executemany(query, data_tuples)
            self.connection.commit()
            
            logger.debug(f"✓ Inserted {len(observations)} observations")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to insert batch observations: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_sensor_readings(self, sensor_id: str, 
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           limit: int = 1000) -> List[Dict]:
        """
        Get readings for a sensor
        
        Args:
            sensor_id: Sensor ID
            start_time: Start timestamp
            end_time: End timestamp
            limit: Maximum number of results
            
        Returns:
            List of reading dictionaries
        """
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            query = """
            SELECT * FROM observations
            WHERE sensor_id = %s
            """
            
            params = [sensor_id]
            
            if start_time:
                query += " AND timestamp >= %s"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= %s"
                params.append(end_time)
            
            query += " ORDER BY timestamp DESC LIMIT %s"
            params.append(limit)
            
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to get sensor readings: {e}")
            return []
    
    def get_sensor_statistics(self, sensor_id: str) -> Optional[Dict]:
        """
        Get statistics for a sensor
        
        Args:
            sensor_id: Sensor ID
            
        Returns:
            Statistics dictionary or None
        """
        try:
            if not self.connection:
                if not self.connect():
                    return None
            
            query = """
            SELECT 
                COUNT(*) as total_readings,
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value,
                STDDEV(value) as stddev_value,
                MIN(timestamp) as first_reading,
                MAX(timestamp) as last_reading,
                AVG(quality) as avg_quality,
                SUM(CASE WHEN outlier THEN 1 ELSE 0 END) as outlier_count
            FROM observations
            WHERE sensor_id = %s
            """
            
            self.cursor.execute(query, (sensor_id,))
            result = self.cursor.fetchone()
            
            if result:
                return dict(result)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return None
    
    def get_hourly_averages(self, sensor_id: str, 
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> List[Dict]:
        """
        Get hourly averages for a sensor
        
        Args:
            sensor_id: Sensor ID
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            List of hourly average dictionaries
        """
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            query = """
            SELECT 
                bucket,
                sensor_id,
                avg_value,
                min_value,
                max_value,
                stddev_value,
                reading_count,
                avg_quality,
                outlier_count
            FROM observations_hourly
            WHERE sensor_id = %s
            """
            
            params = [sensor_id]
            
            if start_time:
                query += " AND bucket >= %s"
                params.append(start_time)
            
            if end_time:
                query += " AND bucket <= %s"
                params.append(end_time)
            
            query += " ORDER BY bucket DESC"
            
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to get hourly averages: {e}")
            return []
    
    def get_daily_summary(self, sensor_type: str = None) -> List[Dict]:
        """
        Get daily summary
        
        Args:
            sensor_type: Optional sensor type filter
            
        Returns:
            List of daily summary dictionaries
        """
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            query = """
            SELECT 
                bucket,
                sensor_type,
                avg_value,
                min_value,
                max_value,
                unique_sensors,
                total_readings,
                avg_quality
            FROM observations_daily
            """
            
            params = []
            
            if sensor_type:
                query += " WHERE sensor_type = %s"
                params.append(sensor_type)
            
            query += " ORDER BY bucket DESC LIMIT 30"
            
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to get daily summary: {e}")
            return []
    
    def compress_chunks(self) -> bool:
        """
        Manually compress old chunks
        
        Returns:
            True if compression successful
        """
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            self.cursor.execute("""
                SELECT compress_chunk(i)
                FROM show_chunks('observations', older_than => INTERVAL '30 days') i
            """)
            
            self.connection.commit()
            logger.info("✓ Chunks compressed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to compress chunks: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            if not self.connection:
                if not self.connect():
                    return {}
            
            stats = {}
            
            # Total observations
            self.cursor.execute("SELECT COUNT(*) FROM observations")
            stats['total_observations'] = self.cursor.fetchone()[0]
            
            # Total sensors
            self.cursor.execute("SELECT COUNT(DISTINCT sensor_id) FROM observations")
            stats['total_sensors'] = self.cursor.fetchone()[0]
            
            # Total sensor types
            self.cursor.execute("SELECT COUNT(DISTINCT sensor_type) FROM observations")
            stats['total_sensor_types'] = self.cursor.fetchone()[0]
            
            # Date range
            self.cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM observations")
            result = self.cursor.fetchone()
            stats['earliest_reading'] = result[0]
            stats['latest_reading'] = result[1]
            
            # Hypertable info
            self.cursor.execute("""
                SELECT 
                    hypertable_name,
                    num_chunks,
                    total_size
                FROM timescaledb_information.hypertables
                WHERE hypertable_name = 'observations'
            """)
            result = self.cursor.fetchone()
            if result:
                stats['hypertable_name'] = result[0]
                stats['num_chunks'] = result[1]
                stats['total_size'] = result[2]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}


def insert_observation(data: Dict[str, Any]) -> bool:
    """
    Convenience function to insert observation
    
    Args:
        data: Observation data dictionary
        
    Returns:
        True if inserted successfully
    """
    loader = TimescaleLoader()
    loader.connect()
    result = loader.insert_observation(data)
    loader.close()
    return result


def get_sensor_readings(sensor_id: str, limit: int = 1000) -> List[Dict]:
    """
    Convenience function to get sensor readings
    
    Args:
        sensor_id: Sensor ID
        limit: Maximum number of results
        
    Returns:
        List of reading dictionaries
    """
    loader = TimescaleLoader()
    loader.connect()
    results = loader.get_sensor_readings(sensor_id, limit=limit)
    loader.close()
    return results