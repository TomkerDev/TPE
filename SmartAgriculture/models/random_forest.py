"""
Random Forest Classification Model
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report
import joblib
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RandomForestModel:
    """Random Forest classifier"""
    
    def __init__(self, n_estimators: int = 300, max_depth: int = 20, 
                 random_state: int = 42):
        """
        Initialize Random Forest model
        
        Args:
            n_estimators: Number of trees
            max_depth: Maximum depth of trees
            random_state: Random seed
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.model = None
        self.feature_importance = None
        
    def build_model(self) -> RandomForestClassifier:
        """
        Build Random Forest model
        
        Returns:
            RandomForestClassifier instance
        """
        try:
            self.model = RandomForestClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                random_state=self.random_state,
                n_jobs=-1
            )
            
            logger.info(f"✓ Built Random Forest model: {self.n_estimators} trees, max_depth={self.max_depth}")
            
            return self.model
            
        except Exception as e:
            logger.error(f"Failed to build Random Forest model: {e}")
            return None
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> bool:
        """
        Train the model
        
        Args:
            X_train: Training features
            y_train: Training target
            
        Returns:
            True if training successful
        """
        try:
            if self.model is None:
                self.build_model()
            
            self.model.fit(X_train, y_train)
            
            # Get feature importance
            if hasattr(self.model, 'feature_importances_'):
                self.feature_importance = self.model.feature_importances_
            
            logger.info("✓ Random Forest model trained successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to train Random Forest model: {e}")
            return False
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Features
            
        Returns:
            Predictions
        """
        try:
            if self.model is None:
                logger.error("Model not trained")
                return np.array([])
            
            return self.model.predict(X)
            
        except Exception as e:
            logger.error(f"Failed to make predictions: {e}")
            return np.array([])
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict probabilities
        
        Args:
            X: Features
            
        Returns:
            Prediction probabilities
        """
        try:
            if self.model is None:
                logger.error("Model not trained")
                return np.array([])
            
            return self.model.predict_proba(X)
            
        except Exception as e:
            logger.error(f"Failed to predict probabilities: {e}")
            return np.array([])
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """
        Evaluate model performance
        
        Args:
            X_test: Test features
            y_test: Test target
            
        Returns:
            Dictionary with evaluation metrics
        """
        try:
            if self.model is None:
                logger.error("Model not trained")
                return {}
            
            # Make predictions
            y_pred = self.predict(X_test)
            
            # Compute metrics
            metrics = {
                'accuracy': float(accuracy_score(y_test, y_pred)),
                'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
                'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
                'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
                'classification_report': classification_report(y_test, y_pred, zero_division=0)
            }
            
            logger.info(f"✓ Model evaluation: Accuracy={metrics['accuracy']:.4f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to evaluate model: {e}")
            return {}
    
    def get_feature_importance(self, feature_names: list = None) -> pd.DataFrame:
        """
        Get feature importance
        
        Args:
            feature_names: List of feature names
            
        Returns:
            DataFrame with feature importance
        """
        try:
            if self.feature_importance is None:
                logger.warning("Feature importance not available")
                return pd.DataFrame()
            
            if feature_names is None:
                feature_names = [f'feature_{i}' for i in range(len(self.feature_importance))]
            
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': self.feature_importance
            }).sort_values('importance', ascending=False)
            
            return importance_df
            
        except Exception as e:
            logger.error(f"Failed to get feature importance: {e}")
            return pd.DataFrame()
    
    def save_model(self, filepath: str = 'models/random_forest.pkl'):
        """
        Save model to file
        
        Args:
            filepath: Path to save model
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'feature_importance': self.feature_importance,
                'n_estimators': self.n_estimators,
                'max_depth': self.max_depth,
                'random_state': self.random_state
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"✓ Saved Random Forest model to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self, filepath: str = 'models/random_forest.pkl'):
        """
        Load model from file
        
        Args:
            filepath: Path to load model from
        """
        try:
            if not os.path.exists(filepath):
                logger.error(f"Model file not found: {filepath}")
                return False
            
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.feature_importance = model_data.get('feature_importance')
            self.n_estimators = model_data.get('n_estimators', 300)
            self.max_depth = model_data.get('max_depth', 20)
            self.random_state = model_data.get('random_state', 42)
            
            logger.info(f"✓ Loaded Random Forest model from {filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


def train_random_forest(X_train: np.ndarray, y_train: np.ndarray,
                       n_estimators: int = 300, max_depth: int = 20) -> RandomForestModel:
    """
    Convenience function to train Random Forest
    
    Args:
        X_train: Training features
        y_train: Training target
        n_estimators: Number of trees
        max_depth: Maximum depth
        
    Returns:
        Trained RandomForestModel
    """
    model = RandomForestModel(n_estimators, max_depth)
    model.build_model()
    model.train(X_train, y_train)
    return model


if __name__ == "__main__":
    # Test Random Forest
    from analytics.load_data import load_sample_data
    from models.dataset import Dataset
    from models.preprocessing import preprocess_data
    
    print("Loading and preparing data...")
    df = load_sample_data()
    
    # Prepare features
    X = df.drop(['sensor_type', 'sensor_id', 'timestamp'], axis=1, errors='ignore')
    y = df['sensor_type']
    
    # Split
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Preprocess
    X_train_processed, X_test_processed = preprocess_data(X_train, X_test)
    
    print(f"\nTrain shape: {X_train_processed.shape}")
    print(f"Test shape: {X_test_processed.shape}")
    
    # Train model
    print("\nTraining Random Forest...")
    rf_model = RandomForestModel(n_estimators=100, max_depth=15)
    rf_model.build_model()
    rf_model.train(X_train_processed, y_train)
    
    # Evaluate
    print("\nEvaluating model...")
    metrics = rf_model.evaluate(X_test_processed, y_test)
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"F1 Score: {metrics['f1_score']:.4f}")
    
    # Feature importance
    feature_names = X_train.columns.tolist()
    importance = rf_model.get_feature_importance(feature_names)
    print(f"\nTop 5 important features:")
    print(importance.head())
    
    # Save model
    rf_model.save_model('models/random_forest_test.pkl')