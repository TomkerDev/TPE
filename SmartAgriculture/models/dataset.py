"""
Dataset Module
Loads and prepares datasets for machine learning
"""
import os
import logging
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Dataset:
    """Dataset loader and preparer for ML models"""
    
    def __init__(self, data_path: str = None):
        """
        Initialize dataset
        
        Args:
            data_path: Path to data file (CSV or database query)
        """
        self.data_path = data_path
        self.df = None
        self.X = None
        self.y = None
        self.feature_names = []
        self.target_name = ''
        
    def load_from_csv(self, filepath: str = None) -> pd.DataFrame:
        """
        Load dataset from CSV file
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame with data
        """
        try:
            path = filepath or self.data_path
            if not path:
                logger.error("No filepath provided")
                return pd.DataFrame()
            
            self.df = pd.read_csv(path)
            logger.info(f"✓ Loaded dataset from {path}: {len(self.df)} rows, {len(self.df.columns)} columns")
            
            return self.df
            
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            return pd.DataFrame()
    
    def load_from_database(self, query: str = None) -> pd.DataFrame:
        """
        Load dataset from database
        
        Args:
            query: SQL query
            
        Returns:
            DataFrame with data
        """
        try:
            from sqlalchemy import create_engine
            
            db_url = f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:{os.getenv('POSTGRES_PASSWORD', 'admin123')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'agriculture')}"
            engine = create_engine(db_url)
            
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
                """
            
            self.df = pd.read_sql(query, engine)
            logger.info(f"✓ Loaded dataset from database: {len(self.df)} rows")
            
            return self.df
            
        except Exception as e:
            logger.error(f"Failed to load from database: {e}")
            return pd.DataFrame()
    
    def prepare_features_target(self, target_column: str, 
                                drop_columns: List[str] = None) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features (X) and target (y)
        
        Args:
            target_column: Name of target column
            drop_columns: List of columns to drop
            
        Returns:
            Tuple of (X, y)
        """
        try:
            if self.df is None:
                logger.error("No dataset loaded")
                return pd.DataFrame(), pd.Series()
            
            if target_column not in self.df.columns:
                logger.error(f"Target column '{target_column}' not found")
                return pd.DataFrame(), pd.Series()
            
            # Default columns to drop
            if drop_columns is None:
                drop_columns = ['timestamp', 'sensor_id']
            
            # Separate features and target
            self.y = self.df[target_column]
            self.X = self.df.drop(columns=[target_column] + drop_columns, errors='ignore')
            
            # Store feature names
            self.feature_names = self.X.columns.tolist()
            self.target_name = target_column
            
            logger.info(f"✓ Prepared features: {len(self.X.columns)} features, {len(self.X)} samples")
            
            return self.X, self.y
            
        except Exception as e:
            logger.error(f"Failed to prepare features: {e}")
            return pd.DataFrame(), pd.Series()
    
    def get_feature_names(self) -> List[str]:
        """Get feature names"""
        return self.feature_names
    
    def get_target_name(self) -> str:
        """Get target name"""
        return self.target_name
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get dataset summary
        
        Returns:
            Dictionary with dataset information
        """
        if self.df is None:
            return {}
        
        summary = {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'columns': self.df.columns.tolist(),
            'dtypes': self.df.dtypes.astype(str).to_dict(),
            'missing_values': self.df.isnull().sum().to_dict(),
            'numeric_columns': self.df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': self.df.select_dtypes(include=['object']).columns.tolist()
        }
        
        if self.X is not None:
            summary['features'] = {
                'count': len(self.X.columns),
                'names': self.X.columns.tolist()
            }
        
        if self.y is not None:
            summary['target'] = {
                'name': self.target_name,
                'type': 'classification' if self.y.dtype == 'object' or self.y.nunique() < 20 else 'regression',
                'unique_values': self.y.nunique() if self.y.dtype == 'object' or self.y.nunique() < 20 else None
            }
        
        return summary


def load_dataset(filepath: str = None, target_column: str = 'target') -> Tuple[pd.DataFrame, pd.Series]:
    """
    Convenience function to load and prepare dataset
    
    Args:
        filepath: Path to data file
        target_column: Name of target column
        
    Returns:
        Tuple of (X, y)
    """
    dataset = Dataset(filepath)
    
    # Try to load from CSV
    if filepath and os.path.exists(filepath):
        dataset.load_from_csv(filepath)
    else:
        # Load sample data
        logger.info("Loading sample data...")
        from analytics.load_data import load_sample_data
        dataset.df = load_sample_data()
        target_column = 'sensor_type'
    
    # Prepare features and target
    X, y = dataset.prepare_features_target(target_column)
    
    return X, y


if __name__ == "__main__":
    # Test dataset loading
    print("Loading dataset...")
    
    # Try to load from database
    dataset = Dataset()
    df = dataset.load_from_database()
    
    if df.empty:
        # Load sample data
        from analytics.load_data import load_sample_data
        df = load_sample_data()
    
    print(f"\nDataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nFirst few rows:")
    print(df.head())
    
    # Prepare features
    X, y = dataset.prepare_features_target('sensor_type')
    print(f"\nFeatures shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    print(f"Feature names: {dataset.get_feature_names()}")
    
    # Get summary
    summary = dataset.get_summary()
    print(f"\nDataset summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")