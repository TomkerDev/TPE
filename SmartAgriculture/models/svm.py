"""
Support Vector Machine (SVM) Classification Model
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report
import joblib
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SVMModel:
    """Support Vector Machine classifier"""
    
    def __init__(self, kernel: str = 'rbf', probability: bool = True, 
                 random_state: int = 42):
        """
        Initialize SVM model
        
        Args:
            kernel: Kernel type ('linear', 'rbf', 'poly', 'sigmoid')
            probability: Whether to enable probability estimates
            random_state: Random seed
        """
        self.kernel = kernel
        self.probability = probability
        self.random_state = random_state
        self.model = None
        
    def build_model(self) -> SVC:
        """Build SVM model"""
        try:
            self.model = SVC(
                kernel=self.kernel,
                probability=self.probability,
                random_state=self.random_state
            )
            
            logger.info(f"✓ Built SVM model: kernel={self.kernel}")
            
            return self.model
            
        except Exception as e:
            logger.error(f"Failed to build SVM model: {e}")
            return None
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> bool:
        """Train the model"""
        try:
            if self.model is None:
                self.build_model()
            
            self.model.fit(X_train, y_train)
            
            logger.info("✓ SVM model trained successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to train SVM model: {e}")
            return False
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        try:
            if self.model is None:
                logger.error("Model not trained")
                return np.array([])
            
            return self.model.predict(X)
            
        except Exception as e:
            logger.error(f"Failed to make predictions: {e}")
            return np.array([])
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities"""
        try:
            if self.model is None:
                logger.error("Model not trained")
                return np.array([])
            
            if not self.probability:
                logger.error("Probability estimates not enabled")
                return np.array([])
            
            return self.model.predict_proba(X)
            
        except Exception as e:
            logger.error(f"Failed to predict probabilities: {e}")
            return np.array([])
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Evaluate model performance"""
        try:
            if self.model is None:
                logger.error("Model not trained")
                return {}
            
            y_pred = self.predict(X_test)
            
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
    
    def save_model(self, filepath: str = 'models/svm.pkl'):
        """Save model to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'kernel': self.kernel,
                'probability': self.probability,
                'random_state': self.random_state
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"✓ Saved SVM model to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self, filepath: str = 'models/svm.pkl'):
        """Load model from file"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"Model file not found: {filepath}")
                return False
            
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.kernel = model_data.get('kernel', 'rbf')
            self.probability = model_data.get('probability', True)
            self.random_state = model_data.get('random_state', 42)
            
            logger.info(f"✓ Loaded SVM model from {filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


def train_svm(X_train: np.ndarray, y_train: np.ndarray,
              kernel: str = 'rbf') -> SVMModel:
    """Convenience function to train SVM"""
    model = SVMModel(kernel=kernel)
    model.build_model()
    model.train(X_train, y_train)
    return model


if __name__ == "__main__":
    from analytics.load_data import load_sample_data
    from models.preprocessing import preprocess_data
    from sklearn.model_selection import train_test_split
    
    print("Loading data...")
    df = load_sample_data()
    
    X = df.drop(['sensor_type', 'sensor_id', 'timestamp'], axis=1, errors='ignore')
    y = df['sensor_type']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train_processed, X_test_processed = preprocess_data(X_train, X_test)
    
    print("\nTraining SVM...")
    svm_model = SVMModel(kernel='rbf')
    svm_model.build_model()
    svm_model.train(X_train_processed, y_train)
    
    print("\nEvaluating...")
    metrics = svm_model.evaluate(X_test_processed, y_test)
    print(f"Accuracy: {metrics['accuracy']:.4f}")