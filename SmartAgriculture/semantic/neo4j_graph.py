"""
Neo4j Graph Manager
Manages semantic knowledge graph in Neo4j database
"""
from typing import Dict, Any, List, Optional
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
import logging

from semantic.ontology import EX, SOSA, AGRI, get_sensor_class, get_property_uri

logger = logging.getLogger(__name__)


class Neo4jGraphManager:
    """Manages Neo4j knowledge graph for semantic data"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", 
                 user: str = "neo4j", 
                 password: str = "password"):
        """
        Initialize Neo4j graph manager
        
        Args:
            uri: Neo4j database URI
            user: Username
            password: Password
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        
    def connect(self) -> bool:
        """
        Connect to Neo4j database
        
        Returns:
            True if connected successfully
        """
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            
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
    
    def close(self):
        """Close database connection"""
        try:
            if self.driver:
                self.driver.close()
                logger.info("✓ Neo4j connection closed")
        except Exception as e:
            logger.error(f"Error closing Neo4j connection: {e}")
    
    def ensure_constraints(self):
        """Ensure necessary constraints and indexes exist"""
        try:
            with self.driver.session() as session:
                # Sensor constraints
                session.run("""
                    CREATE CONSTRAINT sensor_id_unique IF NOT EXISTS
                    FOR (s:Sensor) REQUIRE s.id IS UNIQUE
                """)
                
                # Observation constraints
                session.run("""
                    CREATE CONSTRAINT observation_id_unique IF NOT EXISTS
                    FOR (o:Observation) REQUIRE o.id IS UNIQUE
                """)
                
                # Property constraints
                session.run("""
                    CREATE CONSTRAINT property_name_unique IF NOT EXISTS
                    FOR (p:Property) REQUIRE p.name IS UNIQUE
                """)
                
                # Indexes
                session.run("""
                    CREATE INDEX sensor_type_index IF NOT EXISTS
                    FOR (s:Sensor) ON (s.type)
                """)
                
                session.run("""
                    CREATE INDEX observation_timestamp_index IF NOT EXISTS
                    FOR (o:Observation) ON (o.timestamp)
                """)
                
                logger.debug("✓ Neo4j constraints and indexes ensured")
                return True
                
        except Exception as e:
            logger.error(f"✗ Failed to create constraints: {e}")
            return False
    
    def insert_semantic_data(self, data: Dict[str, Any]) -> bool:
        """
        Insert semantic data into Neo4j knowledge graph
        
        Args:
            data: Sensor data with semantic mappings
            
        Returns:
            True if inserted successfully
        """
        try:
            if not self.driver:
                if not self.connect():
                    return False
            
            # Ensure constraints exist
            self.ensure_constraints()
            
            sensor_id = data.get('sensor_id')
            sensor_type = data.get('sensor_type')
            timestamp = data.get('timestamp')
            value = data.get('value')
            semantic_label = data.get('semantic_label', 'Unknown')
            
            with self.driver.session() as session:
                # Create/Merge Sensor node
                session.run("""
                    MERGE (s:Sensor {id: $sensor_id})
                    ON CREATE SET 
                        s.type = $sensor_type,
                        s.semantic_type = $semantic_label,
                        s.created_at = datetime()
                    ON MATCH SET 
                        s.last_seen = datetime(),
                        s.update_count = coalesce(s.update_count, 0) + 1
                    RETURN s
                """, {
                    'sensor_id': sensor_id,
                    'sensor_type': sensor_type,
                    'semantic_label': semantic_label
                })
                
                # Create Observation node
                obs_id = f"obs_{sensor_id}_{timestamp}"
                if isinstance(timestamp, str):
                    obs_id = f"obs_{sensor_id}_{timestamp.replace(':', '-').replace('.', '-')}"
                
                session.run("""
                    CREATE (o:Observation {
                        id: $obs_id,
                        timestamp: $timestamp,
                        value: $value,
                        sensor_id: $sensor_id
                    })
                    WITH o
                    MATCH (s:Sensor {id: $sensor_id})
                    CREATE (s)-[:MADE]->(o)
                    RETURN o
                """, {
                    'obs_id': obs_id,
                    'timestamp': timestamp,
                    'value': value,
                    'sensor_id': sensor_id
                })
                
                # Create Property node and relationship
                session.run("""
                    MATCH (o:Observation {id: $obs_id})
                    MERGE (p:Property {name: $property_name})
                    CREATE (o)-[:OBSERVES]->(p)
                """, {
                    'obs_id': obs_id,
                    'property_name': semantic_label
                })
                
                # Add sensor-specific relationships
                self._add_sensor_specific_relationships(session, data, sensor_id)
                
                logger.debug(f"✓ Inserted semantic data for {sensor_id}")
                return True
                
        except Exception as e:
            logger.error(f"✗ Failed to insert semantic data: {e}")
            return False
    
    def _add_sensor_specific_relationships(self, session, data: Dict[str, Any], sensor_id: str):
        """Add sensor-specific relationships to the graph"""
        
        sensor_type = data.get('sensor_type')
        
        # GPS sensor - add location
        if sensor_type == 'gps':
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            if latitude and longitude:
                session.run("""
                    MATCH (s:Sensor {id: $sensor_id})
                    MERGE (l:Location {
                        latitude: $latitude,
                        longitude: $longitude
                    })
                    CREATE (s)-[:LOCATED_AT]->(l)
                """, {
                    'sensor_id': sensor_id,
                    'latitude': latitude,
                    'longitude': longitude
                })
        
        # Animal sensor - add animal relationship
        elif sensor_type == 'animal':
            animal_id = data.get('animal_id')
            
            if animal_id:
                session.run("""
                    MATCH (s:Sensor {id: $sensor_id})
                    MERGE (a:Animal {id: $animal_id})
                    CREATE (s)-[:MONITORS]->(a)
                """, {
                    'sensor_id': sensor_id,
                    'animal_id': animal_id
                })
        
        # Farm zone relationship
        location_zone = data.get('location_zone')
        if location_zone:
            session.run("""
                MATCH (s:Sensor {id: $sensor_id})
                MERGE (z:Zone {name: $zone})
                CREATE (s)-[:IN_ZONE]->(z)
            """, {
                'sensor_id': sensor_id,
                'zone': location_zone
            })
    
    def insert_batch(self, data_list: List[Dict[str, Any]]) -> bool:
        """
        Insert batch of semantic data
        
        Args:
            data_list: List of sensor data with semantic mappings
            
        Returns:
            True if all inserted successfully
        """
        success = True
        
        for data in data_list:
            if not self.insert_semantic_data(data):
                success = False
        
        return success
    
    def query_sensor_observations(self, sensor_id: str, limit: int = 100) -> List[Dict]:
        """
        Query observations for a sensor
        
        Args:
            sensor_id: Sensor ID
            limit: Maximum number of results
            
        Returns:
            List of observations
        """
        try:
            if not self.driver:
                if not self.connect():
                    return []
            
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (s:Sensor {id: $sensor_id})-[:MADE]->(o:Observation)
                    RETURN o
                    ORDER BY o.timestamp DESC
                    LIMIT $limit
                """, {
                    'sensor_id': sensor_id,
                    'limit': limit
                })
                
                return [dict(record['o']) for record in result]
                
        except Exception as e:
            logger.error(f"Failed to query observations: {e}")
            return []
    
    def query_sensors_by_type(self, sensor_type: str) -> List[Dict]:
        """
        Query sensors by type
        
        Args:
            sensor_type: Type of sensor
            
        Returns:
            List of sensors
        """
        try:
            if not self.driver:
                if not self.connect():
                    return []
            
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (s:Sensor {type: $sensor_type})
                    RETURN s
                    ORDER BY s.last_seen DESC
                """, {
                    'sensor_type': sensor_type
                })
                
                return [dict(record['s']) for record in result]
                
        except Exception as e:
            logger.error(f"Failed to query sensors: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get graph statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            if not self.driver:
                if not self.connect():
                    return {}
            
            with self.driver.session() as session:
                # Count nodes
                sensor_count = session.run("MATCH (s:Sensor) RETURN count(s) AS count").single()['count']
                obs_count = session.run("MATCH (o:Observation) RETURN count(o) AS count").single()['count']
                prop_count = session.run("MATCH (p:Property) RETURN count(p) AS count").single()['count']
                
                # Count relationships
                rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()['count']
                
                return {
                    'sensors': sensor_count,
                    'observations': obs_count,
                    'properties': prop_count,
                    'relationships': rel_count
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def clear_graph(self) -> bool:
        """
        Clear all data from the graph (use with caution!)
        
        Returns:
            True if cleared successfully
        """
        try:
            if not self.driver:
                if not self.connect():
                    return False
            
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
                logger.warning("⚠ Graph cleared!")
                return True
                
        except Exception as e:
            logger.error(f"Failed to clear graph: {e}")
            return False


def insert_semantic_data(data: Dict[str, Any]) -> bool:
    """
    Convenience function to insert semantic data
    
    Args:
        data: Sensor data with semantic mappings
        
    Returns:
        True if inserted successfully
    """
    manager = Neo4jGraphManager()
    return manager.insert_semantic_data(data)


def get_graph_statistics() -> Dict[str, Any]:
    """
    Convenience function to get graph statistics
    
    Returns:
        Statistics dictionary
    """
    manager = Neo4jGraphManager()
    return manager.get_statistics()