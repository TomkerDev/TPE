"""
Data Loading Module
Loads data from various sources (PostgreSQL, TimescaleDB, MongoDB, CSV)
"""
import os
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dotenv import load_dotenv

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Try to import database loaders
try:
    from database.loaders.postgres_loader import PostgresLoader
    from database.loaders.timescale_loader import TimescaleLoader
    from database.loaders.mongo_loader import MongoLoader
    DB_LOADERS_AVAILABLE = True
except ImportError:
    DB_LOADERS_AVAILABLE = False

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataLoader:
    """Unified data loader for multiple sources"""
    
    def __init__(self):
        self.engines = {}
        self.loaders = {}
        
    def connect_postgres(self) -> bool:
        """Connect to PostgreSQL"""
        try:
            db_url = f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:{os.getenv('POSTGRES_PASSWORD', 'admin123')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'agriculture')}"
            self.engines['postgres'] = create_engine(db_url)
            logger.info("✓ Connected to PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to PostgreSQL: {e}")
            return False
    
    def connect_timescale(self) -> bool:
        """Connect to TimescaleDB"""
        try:
            db_url = f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:{os.getenv('POSTGRES_PASSWORD', 'admin123')}@{os.getenv('TIMESCALE_HOST', 'localhost')}:{os.getenv('TIMESCALE_PORT', '5433')}/{os.getenv('TIMESCALE_DB', 'agriculture_ts')}"
            self.engines['timescale'] = create_engine(db_url)
            logger.info("✓ Connected to TimescaleDB")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to TimescaleDB: {e}")
            return False
    
    def load_from_postgres(self, query: str = None) -> pd.DataFrame:
        """
        Load data from PostgreSQL
        
        Args:
            query: SQL query (if None, loads all sensor readings)
            
        Returns:
            DataFrame with data
        """
        try:
            if 'postgres' not in self.engines:
                if not self.connect_postgres():
                    return pd.DataFrame()
            
            if query is None:
                query = """
                SELECT 
                    sr.sensor_id,
                    s.type as sensor_type,
                    sr.value,
                    sr.unit,
                    sr.timestamp,
                    sr.quality,
                    sr.is_outlier
                FROM sensor_readings sr
                JOIN sensors s ON sr.sensor_id = s.sensor_id
                ORDER BY sr.timestamp DESC
                """
            
            df = pd.read_sql(query, self.engines['postgres'])
            logger.info(f"✓ Loaded {len(df)} rows from PostgreSQL")
            return df
            
        except Exception as e:
            logger.error(f"✗ Failed to load from PostgreSQL: {e}")
            return pd.DataFrame()
    
    def load_from_timescale(self, query: str = None, 
                           sensor_id: str = None,
                           start_time: datetime = None,
                           end_time: datetime = None,
                           limit: int = 10000) -> pd.DataFrame:
        """
        Load data from TimescaleDB
        
        Args:
            query: SQL query (if None, builds query from parameters)
            sensor_id: Optional sensor ID filter
            start_time: Optional start timestamp
            end_time: Optional end timestamp
            limit: Maximum rows to load
            
        Returns:
            DataFrame with data
        """
        try:
            if 'timescale' not in self.engines:
                if not self.connect_timescale():
                    return pd.DataFrame()
            
            if query is None:
                query = "SELECT * FROM observations WHERE 1=1"
                params = {}
                
                if sensor_id:
                    query += " AND sensor_id = :sensor_id"
                    params['sensor_id'] = sensor_id
                
                if start_time:
                    query += " AND timestamp >= :start_time"
                    params['start_time'] = start_time
                
                if end_time:
                    query += " AND timestamp <= :end_time"
                    params['end_time'] = end_time
                
                query += f" ORDER BY timestamp DESC LIMIT {limit}"
                
                df = pd.read_sql(query, self.engines['timescale'], params=params)
            else:
                df = pd.read_sql(query, self.engines['timescale'])
            
            logger.info(f"✓ Loaded {len(df)} rows from TimescaleDB")
            return df
            
        except Exception as e:
            logger.error(f"✗ Failed to load from TimescaleDB: {e}")
            return pd.DataFrame()
    
    def load_from_mongodb(self, collection: str = 'raw_data',
                         query: Dict = None,
                         limit: int = 10000) -> pd.DataFrame:
        """
        Load data from MongoDB
        
        Args:
            collection: Collection name
            query: MongoDB query filter
            limit: Maximum documents to load
            
        Returns:
            DataFrame with data
        """
        try:
            if not DB_LOADERS_AVAILABLE:
                logger.error("MongoDB loaders not available")
                return pd.DataFrame()
            
            if 'mongo' not in self.loaders:
                loader = MongoLoader()
                if not loader.connect():
                    return pd.DataFrame()
                self.loaders['mongo'] = loader
            
            collection_obj = self.loaders['mongo'].get_collection(collection)
            if not collection_obj:
                return pd.DataFrame()
            
            # Build query
            mongo_query = query or {}
            cursor = collection_obj.find(mongo_query).limit(limit)
            
            # Convert to DataFrame
            df = pd.DataFrame(list(cursor))
            
            # Remove MongoDB _id column
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)
            
            logger.info(f"✓ Loaded {len(df)} rows from MongoDB ({collection})")
            return df
            
        except Exception as e:
            logger.error(f"✗ Failed to load from MongoDB: {e}")
            return pd.DataFrame()
    
    def load_from_csv(self, filepath: str, **kwargs) -> pd.DataFrame:
        """
        Load data from CSV file
        
        Args:
            filepath: Path to CSV file
            **kwargs: Additional arguments for pd.read_csv
            
        Returns:
            DataFrame with data
        """
        try:
            df = pd.read_csv(filepath, **kwargs)
            logger.info(f"✓ Loaded {len(df)} rows from {filepath}")
            return df
        except Exception as e:
            logger.error(f"✗ Failed to load CSV: {e}")
            return pd.DataFrame()
    
    def load_all_sensor_data(self, days: int = 30) -> pd.DataFrame:
        """
        Load all sensor data from multiple sources
        
        Args:
            days: Number of days to load (for time filtering)
            
        Returns:
            Combined DataFrame
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Load from TimescaleDB (primary source for time-series)
        df_ts = self.load_from_timescale(
            start_time=start_time,
            end_time=end_time,
            limit=100000
        )
        
        if df_ts.empty:
            # Fallback to PostgreSQL
            df_ts = self.load_from_postgres()
        
        return df_ts
    
    def get_sensor_types(self, df: pd.DataFrame) -> List[str]:
        """Get unique sensor types from DataFrame"""
        if 'sensor_type' in df.columns:
            return df['sensor_type'].unique().tolist()
        return []
    
    def get_sensors_by_type(self, df: pd.DataFrame, sensor_type: str) -> pd.DataFrame:
        """Filter DataFrame by sensor type"""
        if 'sensor_type' in df.columns:
            return df[df['sensor_type'] == sensor_type]
        return pd.DataFrame()
    
    def get_sensor_data(self, df: pd.DataFrame, sensor_id: str) -> pd.DataFrame:
        """Filter DataFrame by sensor ID"""
        if 'sensor_id' in df.columns:
            return df[df['sensor_id'] == sensor_id]
        return pd.DataFrame()
    
    def close_all(self):
        """Close all connections"""
        # Close SQLAlchemy engines
        for name, engine in self.engines.items():
            try:
                engine.dispose()
                logger.debug(f"Closed {name} engine")
            except:
                pass
        
        # Close MongoDB loaders
        for name, loader in self.loaders.items():
            try:
                loader.close()
                logger.debug(f"Closed {name} loader")
            except:
                pass


def load_sample_data() -> pd.DataFrame:
    """
    Load sample data for testing
    
    Returns:
        Sample DataFrame
    """
    # Generate sample data
    np.random.seed(42)
    
    n_samples = 1000
    sensor_types = ['temperature', 'humidity', 'soil_moisture', 'ph', 'rainfall', 'light', 'wind']
    
    data = {
        'sensor_id': [f'sensor_{i:03d}' for i in np.random.randint(0, 50, n_samples)],
        'sensor_type': np.random.choice(sensor_types, n_samples),
        'value': np.random.randn(n_samples) * 10 + 25,
        'unit': np.random.choice(['°C', '%', 'pH', 'mm', 'Lux', 'km/h'], n_samples),
        'timestamp': pd.date_range('2024-01-01', periods=n_samples, freq='1min'),
        'quality': np.random.randint(80, 100, n_samples),
        'is_outlier': np.random.choice([True, False], n_samples, p=[0.05, 0.95])
    }
    
    df = pd.DataFrame(data)
    
    # Adjust values based on sensor type
    for sensor_type in sensor_types:
        mask = df['sensor_type'] == sensor_type
        if sensor_type == 'temperature':
            df.loc[mask, 'value'] = np.random.randn(mask.sum()) * 5 + 25
            df.loc[mask, 'unit'] = '°C'
        elif sensor_type == 'humidity':
            df.loc[mask, 'value'] = np.random.randn(mask.sum()) * 10 + 60
            df.loc[mask, 'unit'] = '%'
        elif sensor_type == 'soil_moisture':
            df.loc[mask, 'value'] = np.random.randn(mask.sum()) * 15 + 40
            df.loc[mask, 'unit'] = '%'
        elif sensor_type == 'ph':
            df.loc[mask, 'value'] = np.random.randn(mask.sum()) * 1 + 6.5
            df.loc[mask, 'unit'] = 'pH'
        elif sensor_type == 'rainfall':
            df.loc[mask, 'value'] = np.random.randn(mask.sum()) * 2 + 1
            df.loc[mask, 'unit'] = 'mm'
        elif sensor_type == 'light':
            df.loc[mask, 'value'] = np.random.randn(mask.sum()) * 5000 + 50000
            df.loc[mask, 'unit'] = 'Lux'
        elif sensor_type == 'wind':
            df.loc[mask, 'value'] = np.random.randn(mask.sum()) * 5 + 15
            df.loc[mask, 'unit'] = 'km/h'
    
    logger.info(f"✓ Generated {len(df)} sample data rows")
    return df


# Convenience functions
def load_data(source: str = 'timescale', **kwargs) -> pd.DataFrame:
    """
    Convenience function to load data
    
    Args:
        source: Data source ('timescale', 'postgres', 'mongodb', 'csv', 'sample')
        **kwargs: Additional arguments for specific loaders
        
    Returns:
        DataFrame with data
    """
    loader = DataLoader()
    
    if source == 'timescale':
        return loader.load_from_timescale(**kwargs)
    elif source == 'postgres':
        return loader.load_from_postgres(**kwargs)
    elif source == 'mongodb':
        return loader.load_from_mongodb(**kwargs)
    elif source == 'csv':
        filepath = kwargs.get('filepath')
        if not filepath:
            logger.error("filepath required for CSV loading")
            return pd.DataFrame()
        return loader.load_from_csv(filepath, **kwargs)
    elif source == 'sample':
        return load_sample_data()
    else:
        logger.error(f"Unknown source: {source}")
        return pd.DataFrame()


if __name__ == "__main__":
    # Test data loading
    print("Loading sample data...")
    df = load_sample_data()
    print(f"Loaded {len(df)} rows")
    print(df.head())
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nSensor types: {df['sensor_type'].unique()}")