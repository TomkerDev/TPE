"""
Neo4j Loader - Loads sensor data into Neo4j graph database
"""
import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

from ingestion.utils import enrich_data

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Neo4jLoader:
    """Neo4j data loader for sensor data (graph database)"""
    
    def __init__(self):
        self.driver = None
        
        # Database configuration
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'password')
        
    def connect(self):
        """Connect to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1 AS test")
            
            logger.info(f"✓ Connected to Neo4j: {self.uri}")
            return True
        except AuthError as e:
            logger.error(f"✗ Neo4j authentication failed: {e}")
            return False
        except ServiceUnavailable as e:
            logger.error(f"✗ Neo4j service unavailable: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Neo4j connection error: {e}")
            return False
    
    def ensure_constraints_exist(self):
        """Ensure necessary constraints and indexes exist"""
        try:
            with self.driver.session() as session:
                # Create constraint for Sensor nodes
                session.run("""
                    CREATE CONSTRAINT sensor_id_unique IF NOT EXISTS
                    FOR (s:Sensor) REQUIRE s.sensor_id IS UNIQUE
                """)
                
                # Create constraint for Reading nodes
                session.run("""
                    CREATE CONSTRAINT reading_id_unique IF NOT EXISTS
                    FOR (r:Reading) REQUIRE r.id IS UNIQUE
                """)
                
                # Create indexes
                session.run("""
                    CREATE INDEX sensor_type_index IF NOT EXISTS
                    FOR (s:Sensor) ON (s.sensor_type)
                """)
                
                session.run("""
                    CREATE INDEX reading_timestamp_index IF NOT EXISTS
                    FOR (r:Reading) ON (r.timestamp)
                """)
                
                logger.debug("✓ Neo4j constraints and indexes ready")
                return True
                
        except Exception as e:
            logger.error(f"✗ Failed to create constraints: {e}")
            return False
    
    def load(self, data: Dict[str, Any]) -> bool:
        """Load data to Neo4j"""
        try:
            # Connect if not connected
            if not self.driver:
                if not self.connect():
                    return False
            
            # Ensure constraints exist
            if not self.ensure_constraints_exist():
                return False
            
            sensor_id = data.get('sensor_id')
            sensor_type = data.get('sensor_type')
            timestamp = data.get('timestamp')
            
            # Convert timestamp to string if it's a datetime object
            if isinstance(timestamp, datetime):
                timestamp_str = timestamp.isoformat()
            else:
                timestamp_str = str(timestamp)
            
            with self.driver.session() as session:
                # Create or update Sensor node
                session.run("""
                    MERGE (s:Sensor {sensor_id: $sensor_id})
                    ON CREATE SET 
                        s.sensor_type = $sensor_type,
                        s.created_at = datetime(),
                        s.first_reading = $timestamp
                    ON MATCH SET 
                        s.last_reading = $timestamp,
                        s.reading_count = coalesce(s.reading_count, 0) + 1
                    RETURN s
                """, {
                    'sensor_id': sensor_id,
                    'sensor_type': sensor_type,
                    'timestamp': timestamp_str
                })
                
                # Create Reading node with properties based on sensor type
                reading_properties = self._build_reading_properties(data)
                
                session.run("""
                    CREATE (r:Reading $properties)
                    WITH r
                    MATCH (s:Sensor {sensor_id: $sensor_id})
                    CREATE (s)-[:HAS_READING]->(r)
                    RETURN r
                """, {
                    'sensor_id': sensor_id,
                    'properties': reading_properties
                })
                
                # Create relationships between sensors of the same type
                session.run("""
                    MATCH (s1:Sensor {sensor_id: $sensor_id})
                    MATCH (s2:Sensor {sensor_type: $sensor_type})
                    WHERE s1 <> s2
                    MERGE (s1)-[:SAME_TYPE]->(s2)
                """, {
                    'sensor_id': sensor_id,
                    'sensor_type': sensor_type
                })
                
                logger.debug(f"✓ Loaded {sensor_type} data to Neo4j")
                return True
                
        except Exception as e:
            logger.error(f"✗ Failed to load data to Neo4j: {e}")
            return False
    
    def _build_reading_properties(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build properties for Reading node based on sensor type"""
        properties = {
            'id': f"{data.get('sensor_id')}_{data.get('timestamp')}",
            'sensor_id': data.get('sensor_id'),
            'sensor_type': data.get('sensor_type'),
            'timestamp': data.get('timestamp').isoformat() if isinstance(data.get('timestamp'), datetime) else str(data.get('timestamp')),
            'processed_at': data.get('processed_at').isoformat() if isinstance(data.get('processed_at'), datetime) else str(data.get('processed_at')),
            'data_quality': data.get('data_quality', 1.0),
            'metric': data.get('metric')
        }
        
        # Add sensor-specific properties
        sensor_type = data.get('sensor_type')
        
        if sensor_type == 'temperature':
            properties['value'] = data.get('temperature')
            properties['unit'] = data.get('unit', 'celsius')
            
        elif sensor_type == 'humidity':
            properties['value'] = data.get('humidity')
            properties['unit'] = data.get('unit', 'percent')
            
        elif sensor_type == 'soil_moisture':
            properties['value'] = data.get('soil_moisture')
            properties['unit'] = data.get('unit', 'percent')
            
        elif sensor_type == 'ph':
            properties['value'] = data.get('ph')
            properties['unit'] = data.get('unit', 'pH')
            
        elif sensor_type == 'rainfall':
            properties['value'] = data.get('rainfall')
            properties['unit'] = data.get('unit', 'mm')
            properties['period'] = data.get('period', 'last_hour')
            
        elif sensor_type == 'light':
            properties['value'] = data.get('light_intensity')
            properties['unit'] = data.get('unit', 'lux')
            properties['hour'] = data.get('hour')
            
        elif sensor_type == 'wind':
            properties['wind_speed'] = data.get('wind_speed')
            properties['wind_direction'] = data.get('wind_direction')
            properties['unit_speed'] = data.get('unit_speed', 'km/h')
            properties['unit_direction'] = data.get('unit_direction', 'degrees')
            
        elif sensor_type == 'water_quality':
            properties['ph'] = data.get('ph')
            properties['dissolved_oxygen'] = data.get('dissolved_oxygen')
            properties['turbidity'] = data.get('turbidity')
            properties['conductivity'] = data.get('conductivity')
            
        elif sensor_type == 'gps':
            properties['latitude'] = data.get('latitude')
            properties['longitude'] = data.get('longitude')
            properties['altitude'] = data.get('altitude')
            properties['speed'] = data.get('speed')
            
        elif sensor_type == 'animal':
            properties['animal_id'] = data.get('animal_id')
            properties['activity_level'] = data.get('activity_level')
            properties['body_temperature'] = data.get('body_temperature')
            properties['heart_rate'] = data.get('heart_rate')
            properties['location_zone'] = data.get('location_zone')
            properties['health_status'] = data.get('health_status')
        
        return properties
    
    def load_batch(self, data_list: List[Dict[str, Any]]) -> bool:
        """Load multiple readings in batch"""
        try:
            if not self.driver:
                if not self.connect():
                    return False
            
            with self.driver.session() as session:
                for data in data_list:
                    try:
                        # Create/update Sensor node
                        session.run("""
                            MERGE (s:Sensor {sensor_id: $sensor_id})
                            ON CREATE SET 
                                s.sensor_type = $sensor_type,
                                s.created_at = datetime(),
                                s.first_reading = $timestamp
                            ON MATCH SET 
                                s.last_reading = $timestamp,
                                s.reading_count = coalesce(s.reading_count, 0) + 1
                        """, {
                            'sensor_id': data.get('sensor_id'),
                            'sensor_type': data.get('sensor_type'),
                            'timestamp': data.get('timestamp').isoformat() if isinstance(data.get('timestamp'), datetime) else str(data.get('timestamp'))
                        })
                        
                        # Create Reading node
                        reading_props = self._build_reading_properties(data)
                        session.run("""
                            CREATE (r:Reading $properties)
                            WITH r
                            MATCH (s:Sensor {sensor_id: $sensor_id})
                            CREATE (s)-[:HAS_READING]->(r)
                        """, {
                            'sensor_id': data.get('sensor_id'),
                            'properties': reading_props
                        })
                        
                    except Exception as e:
                        logger.error(f"Error in batch insert: {e}")
                        continue
                
                logger.debug(f"✓ Batch loaded {len(data_list)} readings to Neo4j")
                return True
                
        except Exception as e:
            logger.error(f"✗ Batch load error: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        try:
            if self.driver:
                self.driver.close()
                logger.info("✓ Neo4j connection closed")
        except Exception as e:
            logger.error(f"Error closing Neo4j connection: {e}")
    
    def get_stats(self):
        """Get statistics from database"""
        try:
            if not self.driver:
                if not self.connect():
                    return None
            
            with self.driver.session() as session:
                # Count sensors
                sensor_count = session.run("MATCH (s:Sensor) RETURN count(s) AS count").single()['count']
                
                # Count readings
                reading_count = session.run("MATCH (r:Reading) RETURN count(r) AS count").single()['count']
                
                # Get sensor types
                sensor_types = session.run("""
                    MATCH (s:Sensor) 
                    RETURN s.sensor_type AS type, count(s) AS count 
                    ORDER BY count DESC
                """).data()
                
                return {
                    'total_sensors': sensor_count,
                    'total_readings': reading_count,
                    'sensor_types': sensor_types
                }
                
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return None
    
    def query_sensor_readings(self, sensor_id: str, limit: int = 100):
        """Query readings for a specific sensor"""
        try:
            if not self.driver:
                if not self.connect():
                    return None
            
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (s:Sensor {sensor_id: $sensor_id})-[:HAS_READING]->(r:Reading)
                    RETURN r
                    ORDER BY r.timestamp DESC
                    LIMIT $limit
                """, {
                    'sensor_id': sensor_id,
                    'limit': limit
                })
                
                readings = [dict(record['r']) for record in result]
                return readings
                
        except Exception as e:
            logger.error(f"Failed to query readings: {e}")
            return None


def main():
    """Main function for testing"""
    loader = Neo4jLoader()
    
    # Test connection
    if not loader.connect():
        print("Failed to connect to Neo4j")
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
    
    print("\nTesting Neo4j Loader...")
    print(f"Test data: {test_data}\n")
    
    # Test loading
    result = loader.load(test_data)
    print(f"Load result: {'Success' if result else 'Failed'}\n")
    
    # Get stats
    stats = loader.get_stats()
    if stats:
        print("Database statistics:")
        print(f"  Total sensors: {stats['total_sensors']}")
        print(f"  Total readings: {stats['total_readings']}")
        print(f"  Sensor types:")
        for st in stats['sensor_types']:
            print(f"    {st['type']}: {st['count']} sensors")
    
    # Close connection
    loader.close()


if __name__ == "__main__":
    main()