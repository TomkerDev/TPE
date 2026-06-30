"""
Decision Tree Classification Model
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report
import joblib
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DecisionTreeModel:
    """Decision Tree classifier"""
    
    def __init__(self, max_depth: int = 15, random_state: int = 42):
        """
        Initialize Decision Tree model
        
        Args:
            max_depth: Maximum depth of tree
            random_state: Random seed
        """
        self.max_depth = max_depth
        self.random_state = random_state
        self.model = None
        self.feature_importance = None
        
    def build_model(self) -> DecisionTreeClassifier:
        """Build Decision Tree model"""
        try:
            self.model = DecisionTreeClassifier(
                max_depth=self.max_depth,
                random_state=self.random_state
            )
            
            logger.info(f"✓ Built Decision Tree model: max_depth={self.max_depth}")
            
            return self.model
            
        except Exception as e:
            logger.error(f"Failed to build Decision Tree model: {e}")
            return None
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> bool:
        """Train the model"""
        try:
            if self.model is None:
                self.build_model()
            
            self.model.fit(X_train, y_train)
            
            if hasattr(self.model, 'feature_importances_'):
                self.feature_importance = self.model.feature_importances_
            
            logger.info("✓ Decision Tree model trained successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to train Decision Tree model: {e}")
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
    
    def get_feature_importance(self, feature_names: list = None) -> pd.DataFrame:
        """Get feature importance"""
        try:
            if self.feature_importance is None:
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
    
    def save_model(self, filepath: str = 'models/decision_tree.pkl'):
        """Save model to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'feature_importance': self.feature_importance,
                'max_depth': self.max_depth,
                'random_state': self.random_state
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"✓ Saved Decision Tree model to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self, filepath: str = 'models/decision_tree.pkl'):
        """Load model from file"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"Model file not found: {filepath}")
                return False
            
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.feature_importance = model_data.get('feature_importance')
            self.max_depth = model_data.get('max_depth', 15)
            self.random_state = model_data.get('random_state', 42)
            
            logger.info(f"✓ Loaded Decision Tree model from {filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


def train_decision_tree(X_train: np.ndarray, y_train: np.ndarray,
                       max_depth: int = 15) -> DecisionTreeModel:
    """Convenience function to train Decision Tree"""
    model = DecisionTreeModel(max_depth)
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
    
    print("\nTraining Decision Tree...")
    dt_model = DecisionTreeModel(max_depth=10)
    dt_model.build_model()
    dt_model.train(X_train_processed, y_train)
    
    print("\nEvaluating...")
    metrics = dt_model.evaluate(X_test_processed, y_test)
    print(f"Accuracy: {metrics['accuracy']:.4f}")