"""
XGBoost Classification Model
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report
import joblib
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class XGBoostModel:
    """XGBoost classifier"""
    
    def __init__(self, n_estimators: int = 400, learning_rate: float = 0.05,
                 max_depth: int = 8, random_state: int = 42):
        """
        Initialize XGBoost model
        
        Args:
            n_estimators: Number of boosting rounds
            learning_rate: Learning rate
            max_depth: Maximum tree depth
            random_state: Random seed
        """
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.random_state = random_state
        self.model = None
        self.feature_importance = None
        
    def build_model(self) -> XGBClassifier:
        """Build XGBoost model"""
        try:
            self.model = XGBClassifier(
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                max_depth=self.max_depth,
                random_state=self.random_state,
                n_jobs=-1,
                use_label_encoder=False,
                eval_metric='mlogloss'
            )
            
            logger.info(f"✓ Built XGBoost model: {self.n_estimators} estimators, lr={self.learning_rate}")
            
            return self.model
            
        except Exception as e:
            logger.error(f"Failed to build XGBoost model: {e}")
            return None
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> bool:
        """Train the model"""
        try:
            if self.model is None:
                self.build_model()
            
            self.model.fit(X_train, y_train, verbose=False)
            
            if hasattr(self.model, 'feature_importances_'):
                self.feature_importance = self.model.feature_importances_
            
            logger.info("✓ XGBoost model trained successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to train XGBoost model: {e}")
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
    
    def save_model(self, filepath: str = 'models/xgboost.pkl'):
        """Save model to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'feature_importance': self.feature_importance,
                'n_estimators': self.n_estimators,
                'learning_rate': self.learning_rate,
                'max_depth': self.max_depth,
                'random_state': self.random_state
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"✓ Saved XGBoost model to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self, filepath: str = 'models/xgboost.pkl'):
        """Load model from file"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"Model file not found: {filepath}")
                return False
            
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.feature_importance = model_data.get('feature_importance')
            self.n_estimators = model_data.get('n_estimators', 400)
            self.learning_rate = model_data.get('learning_rate', 0.05)
            self.max_depth = model_data.get('max_depth', 8)
            self.random_state = model_data.get('random_state', 42)
            
            logger.info(f"✓ Loaded XGBoost model from {filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


def train_xgboost(X_train: np.ndarray, y_train: np.ndarray,
                 n_estimators: int = 400, learning_rate: float = 0.05,
                 max_depth: int = 8) -> XGBoostModel:
    """Convenience function to train XGBoost"""
    model = XGBoostModel(n_estimators, learning_rate, max_depth)
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
    
    print("\nTraining XGBoost...")
    xgb_model = XGBoostModel(n_estimators=200, learning_rate=0.05, max_depth=6)
    xgb_model.build_model()
    xgb_model.train(X_train_processed, y_train)
    
    print("\nEvaluating...")
    metrics = xgb_model.evaluate(X_test_processed, y_test)
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    
    # Feature importance
    feature_names = X_train.columns.tolist()
    importance = xgb_model.get_feature_importance(feature_names)
    print(f"\nTop 5 important features:")
    print(importance.head())