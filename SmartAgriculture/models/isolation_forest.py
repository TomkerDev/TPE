"""
Isolation Forest Anomaly Detection Model
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IsolationForestModel:
    """Isolation Forest for anomaly detection"""
    
    def __init__(self, n_estimators: int = 200, contamination: float = 0.1,
                 random_state: int = 42):
        """
        Initialize Isolation Forest model
        
        Args:
            n_estimators: Number of trees
            contamination: Expected proportion of anomalies
            random_state: Random seed
        """
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.model = None
        
    def build_model(self) -> IsolationForest:
        """Build Isolation Forest model"""
        try:
            self.model = IsolationForest(
                n_estimators=self.n_estimators,
                contamination=self.contamination,
                random_state=self.random_state,
                n_jobs=-1
            )
            
            logger.info(f"✓ Built Isolation Forest model: {self.n_estimators} trees")
            
            return self.model
            
        except Exception as e:
            logger.error(f"Failed to build Isolation Forest model: {e}")
            return None
    
    def train(self, X_train: np.ndarray) -> bool:
        """
        Train the model
        
        Args:
            X_train: Training features (no labels needed for anomaly detection)
            
        Returns:
            True if training successful
        """
        try:
            if self.model is None:
                self.build_model()
            
            self.model.fit(X_train)
            
            logger.info("✓ Isolation Forest model trained successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to train Isolation Forest model: {e}")
            return False
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions (1 for normal, -1 for anomaly)
        
        Args:
            X: Features
            
        Returns:
            Predictions (1 = normal, -1 = anomaly)
        """
        try:
            if self.model is None:
                logger.error("Model not trained")
                return np.array([])
            
            return self.model.predict(X)
            
        except Exception as e:
            logger.error(f"Failed to make predictions: {e}")
            return np.array([])
    
    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """
        Get anomaly scores (lower = more anomalous)
        
        Args:
            X: Features
            
        Returns:
            Anomaly scores
        """
        try:
            if self.model is None:
                logger.error("Model not trained")
                return np.array([])
            
            return self.model.decision_function(X)
            
        except Exception as e:
            logger.error(f"Failed to get anomaly scores: {e}")
            return np.array([])
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """
        Evaluate model performance
        
        Args:
            X_test: Test features
            y_test: Test target (0 = normal, 1 = anomaly)
            
        Returns:
            Dictionary with evaluation metrics
        """
        try:
            if self.model is None:
                logger.error("Model not trained")
                return {}
            
            # Make predictions
            y_pred = self.predict(X_test)
            
            # Convert predictions: -1 (anomaly) -> 1, 1 (normal) -> 0
            y_pred_binary = np.where(y_pred == -1, 1, 0)
            
            # Compute metrics
            metrics = {
                'accuracy': float((y_pred_binary == y_test).mean()),
                'anomalies_detected': int((y_pred_binary == 1).sum()),
                'normal_detected': int((y_pred_binary == 0).sum()),
                'total_samples': len(y_test),
                'classification_report': classification_report(y_test, y_pred_binary, zero_division=0),
                'confusion_matrix': confusion_matrix(y_test, y_pred_binary).tolist()
            }
            
            logger.info(f"✓ Model evaluation: Accuracy={metrics['accuracy']:.4f}, Anomalies detected={metrics['anomalies_detected']}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to evaluate model: {e}")
            return {}
    
    def get_anomaly_scores(self, X: np.ndarray) -> pd.DataFrame:
        """
        Get anomaly scores for samples
        
        Args:
            X: Features
            
        Returns:
            DataFrame with anomaly scores and predictions
        """
        try:
            if self.model is None:
                logger.error("Model not trained")
                return pd.DataFrame()
            
            scores = self.decision_function(X)
            predictions = self.predict(X)
            
            results = pd.DataFrame({
                'anomaly_score': scores,
                'is_anomaly': np.where(predictions == -1, True, False)
            })
            
            return results.sort_values('anomaly_score')
            
        except Exception as e:
            logger.error(f"Failed to get anomaly scores: {e}")
            return pd.DataFrame()
    
    def save_model(self, filepath: str = 'models/isolation_forest.pkl'):
        """Save model to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'n_estimators': self.n_estimators,
                'contamination': self.contamination,
                'random_state': self.random_state
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"✓ Saved Isolation Forest model to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self, filepath: str = 'models/isolation_forest.pkl'):
        """Load model from file"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"Model file not found: {filepath}")
                return False
            
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.n_estimators = model_data.get('n_estimators', 200)
            self.contamination = model_data.get('contamination', 0.1)
            self.random_state = model_data.get('random_state', 42)
            
            logger.info(f"✓ Loaded Isolation Forest model from {filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


def train_isolation_forest(X_train: np.ndarray, n_estimators: int = 200,
                          contamination: float = 0.1) -> IsolationForestModel:
    """Convenience function to train Isolation Forest"""
    model = IsolationForestModel(n_estimators, contamination)
    model.build_model()
    model.train(X_train)
    return model


if __name__ == "__main__":
    from analytics.load_data import load_sample_data
    from models.preprocessing import preprocess_data
    from sklearn.model_selection import train_test_split
    
    print("Loading data...")
    df = load_sample_data()
    
    X = df.drop(['sensor_type', 'sensor_id', 'timestamp'], axis=1, errors='ignore')
    
    # For anomaly detection, we train on normal data only
    X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
    X_train_processed, X_test_processed = preprocess_data(X_train, X_test)
    
    print("\nTraining Isolation Forest...")
    iso_model = IsolationForestModel(n_estimators=100, contamination=0.1)
    iso_model.build_model()
    iso_model.train(X_train_processed)
    
    print("\nDetecting anomalies...")
    predictions = iso_model.predict(X_test_processed)
    n_anomalies = (predictions == -1).sum()
    print(f"Detected {n_anomalies} anomalies out of {len(X_test_processed)} samples")
    
    # Get anomaly scores
    scores = iso_model.get_anomaly_scores(X_test_processed)
    print(f"\nTop 5 most anomalous samples:")
    print(scores.head())