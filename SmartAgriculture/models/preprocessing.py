"""
Preprocessing Module for Machine Learning
Handles data preprocessing, scaling, and encoding
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Preprocesses data for machine learning"""
    
    def __init__(self):
        self.scaler = None
        self.label_encoders = {}
        self.imputer = None
        self.column_transformer = None
        self.preprocessing_pipeline = None
        
    def handle_missing_values(self, df: pd.DataFrame, 
                             strategy: str = 'mean',
                             columns: List[str] = None) -> pd.DataFrame:
        """
        Handle missing values
        
        Args:
            df: DataFrame with data
            strategy: Imputation strategy ('mean', 'median', 'most_frequent', 'constant')
            columns: Columns to impute (if None, all numeric columns)
            
        Returns:
            DataFrame with imputed values
        """
        try:
            df = df.copy()
            
            if columns is None:
                columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            self.imputer = SimpleImputer(strategy=strategy)
            df[columns] = self.imputer.fit_transform(df[columns])
            
            logger.info(f"✓ Imputed missing values using {strategy} strategy")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to handle missing values: {e}")
            return df
    
    def scale_features(self, X_train: np.ndarray, X_test: np.ndarray,
                      method: str = 'standard') -> Tuple[np.ndarray, np.ndarray]:
        """
        Scale features
        
        Args:
            X_train: Training features
            X_test: Test features
            method: Scaling method ('standard', 'minmax')
            
        Returns:
            Tuple of (X_train_scaled, X_test_scaled)
        """
        try:
            if method == 'standard':
                self.scaler = StandardScaler()
            elif method == 'minmax':
                self.scaler = MinMaxScaler()
            else:
                logger.error(f"Unknown scaling method: {method}")
                return X_train, X_test
            
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            logger.info(f"✓ Scaled features using {method} scaling")
            
            return X_train_scaled, X_test_scaled
            
        except Exception as e:
            logger.error(f"Failed to scale features: {e}")
            return X_train, X_test
    
    def encode_categorical(self, df: pd.DataFrame, 
                          columns: List[str] = None,
                          method: str = 'label') -> pd.DataFrame:
        """
        Encode categorical variables
        
        Args:
            df: DataFrame with data
            columns: Columns to encode (if None, all object columns)
            method: Encoding method ('label', 'onehot')
            
        Returns:
            DataFrame with encoded variables
        """
        try:
            df = df.copy()
            
            if columns is None:
                columns = df.select_dtypes(include=['object']).columns.tolist()
            
            if method == 'label':
                for col in columns:
                    if col not in self.label_encoders:
                        self.label_encoders[col] = LabelEncoder()
                    df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
                    
            elif method == 'onehot':
                for col in columns:
                    dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
                    df = pd.concat([df, dummies], axis=1)
                    df = df.drop(columns=[col])
            
            logger.info(f"✓ Encoded {len(columns)} categorical columns using {method} encoding")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to encode categorical variables: {e}")
            return df
    
    def create_preprocessing_pipeline(self, numeric_features: List[str],
                                     categorical_features: List[str] = None,
                                     scale: bool = True) -> Pipeline:
        """
        Create preprocessing pipeline
        
        Args:
            numeric_features: List of numeric feature names
            categorical_features: List of categorical feature names
            scale: Whether to scale numeric features
            
        Returns:
            Sklearn Pipeline
        """
        try:
            transformers = []
            
            # Numeric features pipeline
            numeric_steps = [('imputer', SimpleImputer(strategy='mean'))]
            
            if scale:
                numeric_steps.append(('scaler', StandardScaler()))
            
            numeric_pipeline = Pipeline(steps=numeric_steps)
            
            if numeric_features:
                transformers.append(('num', numeric_pipeline, numeric_features))
            
            # Categorical features pipeline
            if categorical_features:
                categorical_pipeline = Pipeline(steps=[
                    ('imputer', SimpleImputer(strategy='most_frequent')),
                    ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
                ])
                transformers.append(('cat', categorical_pipeline, categorical_features))
            
            # Create column transformer
            self.column_transformer = ColumnTransformer(
                transformers=transformers,
                remainder='passthrough'
            )
            
            # Create full pipeline
            self.preprocessing_pipeline = Pipeline(steps=[
                ('preprocessor', self.column_transformer)
            ])
            
            logger.info("✓ Created preprocessing pipeline")
            
            return self.preprocessing_pipeline
            
        except Exception as e:
            logger.error(f"Failed to create preprocessing pipeline: {e}")
            return None
    
    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Fit and transform data
        
        Args:
            X: Features DataFrame
            
        Returns:
            Transformed features array
        """
        try:
            if self.preprocessing_pipeline is None:
                logger.error("Preprocessing pipeline not created")
                return X.values
            
            X_transformed = self.preprocessing_pipeline.fit_transform(X)
            logger.info("✓ Fit and transformed data")
            
            return X_transformed
            
        except Exception as e:
            logger.error(f"Failed to fit transform: {e}")
            return X.values
    
    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Transform data using fitted pipeline
        
        Args:
            X: Features DataFrame
            
        Returns:
            Transformed features array
        """
        try:
            if self.preprocessing_pipeline is None:
                logger.error("Preprocessing pipeline not created")
                return X.values
            
            X_transformed = self.preprocessing_pipeline.transform(X)
            logger.info("✓ Transformed data")
            
            return X_transformed
            
        except Exception as e:
            logger.error(f"Failed to transform: {e}")
            return X.values
    
    def save_preprocessor(self, filepath: str = 'models/preprocessor.pkl'):
        """
        Save preprocessor to file
        
        Args:
            filepath: Path to save preprocessor
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            preprocessor_data = {
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'imputer': self.imputer,
                'column_transformer': self.column_transformer,
                'preprocessing_pipeline': self.preprocessing_pipeline
            }
            
            joblib.dump(preprocessor_data, filepath)
            logger.info(f"✓ Saved preprocessor to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save preprocessor: {e}")
    
    def load_preprocessor(self, filepath: str = 'models/preprocessor.pkl'):
        """
        Load preprocessor from file
        
        Args:
            filepath: Path to load preprocessor from
        """
        try:
            if not os.path.exists(filepath):
                logger.error(f"Preprocessor file not found: {filepath}")
                return
            
            preprocessor_data = joblib.load(filepath)
            
            self.scaler = preprocessor_data.get('scaler')
            self.label_encoders = preprocessor_data.get('label_encoders', {})
            self.imputer = preprocessor_data.get('imputer')
            self.column_transformer = preprocessor_data.get('column_transformer')
            self.preprocessing_pipeline = preprocessor_data.get('preprocessing_pipeline')
            
            logger.info(f"✓ Loaded preprocessor from {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load preprocessor: {e}")


def preprocess_data(X_train: pd.DataFrame, X_test: pd.DataFrame,
                   numeric_features: List[str] = None,
                   categorical_features: List[str] = None,
                   scale: bool = True) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convenience function to preprocess data
    
    Args:
        X_train: Training features
        X_test: Test features
        numeric_features: List of numeric feature names
        categorical_features: List of categorical feature names
        scale: Whether to scale features
        
    Returns:
        Tuple of (X_train_processed, X_test_processed)
    """
    preprocessor = DataPreprocessor()
    
    # Auto-detect feature types if not provided
    if numeric_features is None:
        numeric_features = X_train.select_dtypes(include=[np.number]).columns.tolist()
    
    if categorical_features is None:
        categorical_features = X_train.select_dtypes(include=['object']).columns.tolist()
    
    # Create pipeline
    preprocessor.create_preprocessing_pipeline(numeric_features, categorical_features, scale)
    
    # Fit and transform
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    return X_train_processed, X_test_processed


if __name__ == "__main__":
    # Test preprocessing
    from analytics.load_data import load_sample_data
    
    print("Loading sample data...")
    df = load_sample_data()
    
    # Separate features and target
    X = df.drop(['sensor_type', 'sensor_id', 'timestamp'], axis=1, errors='ignore')
    y = df['sensor_type']
    
    # Split data
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"\nTrain shape: {X_train.shape}")
    print(f"Test shape: {X_test.shape}")
    
    # Preprocess
    print("\nPreprocessing data...")
    X_train_processed, X_test_processed = preprocess_data(X_train, X_test)
    
    print(f"\nProcessed train shape: {X_train_processed.shape}")
    print(f"Processed test shape: {X_test_processed.shape}")
    print(f"First row: {X_train_processed[0]}")