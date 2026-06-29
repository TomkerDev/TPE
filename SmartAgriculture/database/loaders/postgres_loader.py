"""
PostgreSQL Loader
Loads data into PostgreSQL relational database
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


class PostgresLoader:
    """PostgreSQL data loader for relational data"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        
        # Database configuration
        self.host = os.getenv('POSTGRES_HOST', 'localhost')
        self.port = os.getenv('POSTGRES_PORT', '5432')
        self.database = os.getenv('POSTGRES_DB', 'agriculture')
        self.user = os.getenv('POSTGRES_USER', 'admin')
        self.password = os.getenv('POSTGRES_PASSWORD', 'admin123')
        
    def connect(self) -> bool:
        """
        Connect to PostgreSQL database
        
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
            
            logger.info(f"✓ Connected to PostgreSQL: {self.host}:{self.port}/{self.database}")
            return True
            
        except OperationalError as e:
            logger.error(f"✗ Failed to connect to PostgreSQL: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ PostgreSQL connection error: {e}")
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
    
    def insert_sensor(self, sensor_data: Dict[str, Any]) -> bool:
        """
        Insert or update sensor information
        
        Args:
            sensor_data: Sensor data dictionary
            
        Returns:
            True if inserted successfully
        """
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            query = """
            INSERT INTO sensors (
                sensor_id, type, manufacturer, protocol, 
                latitude, longitude, installation_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (sensor_id) 
            DO UPDATE SET
                type = EXCLUDED.type,
                manufacturer = EXCLUDED.manufacturer,
                protocol = EXCLUDED.protocol,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                updated_at = CURRENT_TIMESTAMP
            """
            
            self.cursor.execute(query, (
                sensor_data.get('sensor_id'),
                sensor_data.get('type'),
                sensor_data.get('manufacturer'),
                sensor_data.get('protocol'),
                sensor_data.get('latitude'),
                sensor_data.get('longitude'),
                sensor_data.get('installation_date')
            ))
            
            self.connection.commit()
            logger.debug(f"✓ Inserted sensor: {sensor_data.get('sensor_id')}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to insert sensor: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def insert_sensor_reading(self, reading_data: Dict[str, Any]) -> bool:
        """
        Insert sensor reading
        
        Args:
            reading_data: Reading data dictionary
            
        Returns:
            True if inserted successfully
        """
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            query = """
            INSERT INTO sensor_readings (
                sensor_id, sensor_type, value, unit, timestamp, quality, is_outlier
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(query, (
                reading_data.get('sensor_id'),
                reading_data.get('sensor_type'),
                reading_data.get('value'),
                reading_data.get('unit'),
                reading_data.get('timestamp'),
                reading_data.get('quality', 100),
                reading_data.get('is_outlier', False)
            ))
            
            self.connection.commit()
            logger.debug(f"✓ Inserted reading for: {reading_data.get('sensor_id')}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to insert reading: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def insert_user(self, user_data: Dict[str, Any]) -> bool:
        """
        Insert user information
        
        Args:
            user_data: User data dictionary
            
        Returns:
            True if inserted successfully
        """
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            query = """
            INSERT INTO users (fullname, email, role)
            VALUES (%s, %s, %s)
            ON CONFLICT (email) 
            DO UPDATE SET
                fullname = EXCLUDED.fullname,
                role = EXCLUDED.role,
                updated_at = CURRENT_TIMESTAMP
            """
            
            self.cursor.execute(query, (
                user_data.get('fullname'),
                user_data.get('email'),
                user_data.get('role', 'viewer')
            ))
            
            self.connection.commit()
            logger.debug(f"✓ Inserted user: {user_data.get('email')}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to insert user: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def insert_field(self, field_data: Dict[str, Any]) -> bool:
        """
        Insert field information
        
        Args:
            field_data: Field data dictionary
            
        Returns:
            True if inserted successfully
        """
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            query = """
            INSERT INTO fields (field_name, area, crop, location)
            VALUES (%s, %s, %s, %s)
            """
            
            self.cursor.execute(query, (
                field_data.get('field_name'),
                field_data.get('area'),
                field_data.get('crop'),
                field_data.get('location')
            ))
            
            self.connection.commit()
            logger.debug(f"✓ Inserted field: {field_data.get('field_name')}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to insert field: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def link_sensor_to_field(self, sensor_id: str, field_id: int, 
                            installation_date: Optional[datetime] = None) -> bool:
        """
        Link sensor to field
        
        Args:
            sensor_id: Sensor ID
            field_id: Field ID
            installation_date: Installation date
            
        Returns:
            True if linked successfully
        """
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            query = """
            INSERT INTO sensor_metadata (sensor_id, field_id, installation_date, status)
            VALUES (%s, %s, %s, %s)
            """
            
            self.cursor.execute(query, (
                sensor_id,
                field_id,
                installation_date or datetime.now().date(),
                'active'
            ))
            
            self.connection.commit()
            logger.debug(f"✓ Linked sensor {sensor_id} to field {field_id}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to link sensor to field: {e}")
            if self.connection:
                self.connection.rollback()
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
            if not self.connection:
                if not self.connect():
                    return False
            
            query = """
            INSERT INTO alerts (sensor_id, alert_type, severity, message)
            VALUES (%s, %s, %s, %s)
            """
            
            self.cursor.execute(query, (
                alert_data.get('sensor_id'),
                alert_data.get('alert_type'),
                alert_data.get('severity'),
                alert_data.get('message')
            ))
            
            self.connection.commit()
            logger.debug(f"✓ Inserted alert for: {alert_data.get('sensor_id')}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to insert alert: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_sensor_latest_reading(self, sensor_id: str) -> Optional[Dict]:
        """
        Get latest reading for a sensor
        
        Args:
            sensor_id: Sensor ID
            
        Returns:
            Latest reading dictionary or None
        """
        try:
            if not self.connection:
                if not self.connect():
                    return None
            
            query = """
            SELECT * FROM sensor_readings
            WHERE sensor_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
            """
            
            self.cursor.execute(query, (sensor_id,))
            result = self.cursor.fetchone()
            
            if result:
                return dict(result)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest reading: {e}")
            return None
    
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
                MIN(timestamp) as first_reading,
                MAX(timestamp) as last_reading,
                AVG(quality) as avg_quality
            FROM sensor_readings
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
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall database statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            if not self.connection:
                if not self.connect():
                    return {}
            
            stats = {}
            
            # Count sensors
            self.cursor.execute("SELECT COUNT(*) FROM sensors")
            stats['sensors'] = self.cursor.fetchone()[0]
            
            # Count readings
            self.cursor.execute("SELECT COUNT(*) FROM sensor_readings")
            stats['readings'] = self.cursor.fetchone()[0]
            
            # Count users
            self.cursor.execute("SELECT COUNT(*) FROM users")
            stats['users'] = self.cursor.fetchone()[0]
            
            # Count fields
            self.cursor.execute("SELECT COUNT(*) FROM fields")
            stats['fields'] = self.cursor.fetchone()[0]
            
            # Count alerts
            self.cursor.execute("SELECT COUNT(*) FROM alerts WHERE resolved = FALSE")
            stats['active_alerts'] = self.cursor.fetchone()[0]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}


def insert_sensor_data(data: Dict[str, Any]) -> bool:
    """
    Convenience function to insert sensor data
    
    Args:
        data: Sensor data dictionary
        
    Returns:
        True if inserted successfully
    """
    loader = PostgresLoader()
    loader.connect()
    result = loader.insert_sensor(data)
    loader.close()
    return result


def insert_reading_data(data: Dict[str, Any]) -> bool:
    """
    Convenience function to insert reading data
    
    Args:
        data: Reading data dictionary
        
    Returns:
        True if inserted successfully
    """
    loader = PostgresLoader()
    loader.connect()
    result = loader.insert_sensor_reading(data)
    loader.close()
    return result