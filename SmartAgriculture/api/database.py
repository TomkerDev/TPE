"""
Database Connection Module for Smart Agriculture API
"""
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
import logging
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        """Initialize database connections"""
        self.postgres_engine = None
        self.timescale_engine = None
        self.mongo_client = None
        self.neo4j_driver = None
        self._connect()
        
    def _connect(self):
        """Establish database connections"""
        try:
            # PostgreSQL connection
            postgres_url = os.getenv(
                'POSTGRES_URL',
                f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:"
                f"{os.getenv('POSTGRES_PASSWORD', 'admin123')}@"
                f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
                f"{os.getenv('POSTGRES_PORT', '5432')}/"
                f"{os.getenv('POSTGRES_DB', 'agriculture')}"
            )
            
            self.postgres_engine = create_engine(
                postgres_url,
                poolclass=StaticPool,
                pool_size=10,
                max_overflow=20
            )
            
            logger.info("✓ Connected to PostgreSQL")
            
            # TimescaleDB connection (same as PostgreSQL but different database)
            timescale_url = os.getenv(
                'TIMESCALE_URL',
                f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:"
                f"{os.getenv('POSTGRES_PASSWORD', 'admin123')}@"
                f"{os.getenv('TIMESCALE_HOST', 'localhost')}:"
                f"{os.getenv('TIMESCALE_PORT', '5433')}/"
                f"{os.getenv('TIMESCALE_DB', 'agriculture_ts')}"
            )
            
            self.timescale_engine = create_engine(
                timescale_url,
                poolclass=StaticPool,
                pool_size=10,
                max_overflow=20
            )
            
            logger.info("✓ Connected to TimescaleDB")
            
            # MongoDB connection (optional)
            try:
                from pymongo import MongoClient
                
                mongo_host = os.getenv('MONGO_HOST', 'localhost')
                mongo_port = int(os.getenv('MONGO_PORT', 27017))
                
                self.mongo_client = MongoClient(
                    host=mongo_host,
                    port=mongo_port,
                    serverSelectionTimeoutMS=5000
                )
                
                # Test connection
                self.mongo_client.server_info()
                logger.info("✓ Connected to MongoDB")
                
            except Exception as e:
                logger.warning(f"MongoDB connection failed: {e}")
                self.mongo_client = None
            
            # Neo4j connection (optional)
            try:
                from neo4j import GraphDatabase
                
                neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
                neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
                neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
                
                self.neo4j_driver = GraphDatabase.driver(
                    neo4j_uri,
                    auth=(neo4j_user, neo4j_password)
                )
                
                # Test connection
                with self.neo4j_driver.session() as session:
                    session.run("RETURN 1")
                
                logger.info("✓ Connected to Neo4j")
                
            except Exception as e:
                logger.warning(f"Neo4j connection failed: {e}")
                self.neo4j_driver = None
                
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def get_postgres_connection(self):
        """Get PostgreSQL connection"""
        return self.postgres_engine.connect()
    
    def get_timescale_connection(self):
        """Get TimescaleDB connection"""
        return self.timescale_engine.connect()
    
    def get_mongo_client(self):
        """Get MongoDB client"""
        return self.mongo_client
    
    def get_neo4j_driver(self):
        """Get Neo4j driver"""
        return self.neo4j_driver
    
    def execute_query(self, query: str, params: dict = None, 
                     database: str = 'postgres') -> list:
        """
        Execute SQL query
        
        Args:
            query: SQL query
            params: Query parameters
            database: 'postgres' or 'timescale'
            
        Returns:
            List of results
        """
        try:
            engine = self.postgres_engine if database == 'postgres' else self.timescale_engine
            
            with engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                return [dict(row._mapping) for row in result]
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []
    
    def close(self):
        """Close all database connections"""
        try:
            if self.postgres_engine:
                self.postgres_engine.dispose()
                logger.info("✓ PostgreSQL connection closed")
            
            if self.timescale_engine:
                self.timescale_engine.dispose()
                logger.info("✓ TimescaleDB connection closed")
            
            if self.mongo_client:
                self.mongo_client.close()
                logger.info("✓ MongoDB connection closed")
            
            if self.neo4j_driver:
                self.neo4j_driver.close()
                logger.info("✓ Neo4j connection closed")
                
        except Exception as e:
            logger.error(f"Error closing connections: {e}")


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> DatabaseManager:
    """Get database manager instance"""
    return db_manager


# Convenience functions
def execute_query(query: str, params: dict = None, 
                 database: str = 'postgres') -> list:
    """Execute SQL query"""
    return db_manager.execute_query(query, params, database)


def get_sensors() -> list:
    """Get all sensors"""
    query = "SELECT * FROM sensors ORDER BY sensor_id"
    return execute_query(query)


def get_observations(limit: int = 100) -> list:
    """Get latest observations"""
    query = """
    SELECT * FROM sensor_data 
    ORDER BY timestamp DESC 
    LIMIT :limit
    """
    return execute_query(query, {'limit': limit})


def get_sensor_data(sensor_type: str = None, 
                   start_time: str = None,
                   end_time: str = None,
                   limit: int = 1000) -> list:
    """
    Get sensor data with filters
    
    Args:
        sensor_type: Filter by sensor type
        start_time: Start timestamp
        end_time: End timestamp
        limit: Maximum number of records
        
    Returns:
        List of sensor data records
    """
    query = "SELECT * FROM sensor_data WHERE 1=1"
    params = {}
    
    if sensor_type:
        query += " AND sensor_type = :sensor_type"
        params['sensor_type'] = sensor_type
    
    if start_time:
        query += " AND timestamp >= :start_time"
        params['start_time'] = start_time
    
    if end_time:
        query += " AND timestamp <= :end_time"
        params['end_time'] = end_time
    
    query += " ORDER BY timestamp DESC LIMIT :limit"
    params['limit'] = limit
    
    return execute_query(query, params)


def get_latest_readings() -> list:
    """Get latest reading for each sensor"""
    query = """
    SELECT DISTINCT ON (sensor_id) 
        sensor_id, sensor_type, value, unit, timestamp, location
    FROM sensor_data
    ORDER BY sensor_id, timestamp DESC
    """
    return execute_query(query)


if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")
    
    try:
        db = get_db()
        
        # Test PostgreSQL
        print("\n1. Testing PostgreSQL...")
        sensors = get_sensors()
        print(f"Found {len(sensors)} sensors")
        
        # Test TimescaleDB
        print("\n2. Testing TimescaleDB...")
        observations = get_observations(limit=10)
        print(f"Found {len(observations)} recent observations")
        
        # Test latest readings
        print("\n3. Testing latest readings...")
        latest = get_latest_readings()
        print(f"Found {len(latest)} latest readings")
        
        if latest:
            print("\nSample reading:")
            print(latest[0])
        
        print("\n✓ Database connection test successful!")
        
    except Exception as e:
        print(f"✗ Database connection test failed: {e}")
    finally:
        db.close()