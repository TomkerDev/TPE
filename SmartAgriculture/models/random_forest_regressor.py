"""
Random Forest Regression Model
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RandomForestRegressorModel:
    """Random Forest Regressor"""
    
    def __init__(self, n_estimators: int = 300, max_depth: int = 20,
                 random_state: int = 42):
        """
        Initialize Random Forest Regressor
        
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
        
    def build_model(self) -> RandomForestRegressor:
        """Build Random Forest Regressor model"""
        try:
            self.model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                random_state=self.random_state,
                n_jobs=-1
            )
            
            logger.info(f"✓ Built Random Forest Regressor: {self.n_estimators} trees")
            
            return self.model
            
        except Exception as e:
            logger.error(f"Failed to build Random Forest Regressor: {e}")
            return None
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> bool:
        """Train the model"""
        try:
            if self.model is None:
                self.build_model()
            
            self.model.fit(X_train, y_train)
            
            if hasattr(self.model, 'feature_importances_'):
                self.feature_importance = self.model.feature_importances_
            
            logger.info("✓ Random Forest Regressor trained successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to train Random Forest Regressor: {e}")
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
                'mse': float(mean_squared_error(y_test, y_pred)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
                'mae': float(mean_absolute_error(y_test, y_pred)),
                'r2_score': float(r2_score(y_test, y_pred))
            }
            
            logger.info(f"✓ Model evaluation: R²={metrics['r2_score']:.4f}, RMSE={metrics['rmse']:.4f}")
            
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
    
    def save_model(self, filepath: str = 'models/random_forest_regressor.pkl'):
        """Save model to file"""
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
            logger.info(f"✓ Saved Random Forest Regressor to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self, filepath: str = 'models/random_forest_regressor.pkl'):
        """Load model from file"""
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
            
            logger.info(f"✓ Loaded Random Forest Regressor from {filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


def train_random_forest_regressor(X_train: np.ndarray, y_train: np.ndarray,
                                  n_estimators: int = 300, max_depth: int = 20) -> RandomForestRegressorModel:
    """Convenience function to train Random Forest Regressor"""
    model = RandomForestRegressorModel(n_estimators, max_depth)
    model.build_model()
    model.train(X_train, y_train)
    return model


if __name__ == "__main__":
    from analytics.load_data import load_sample_data
    from models.preprocessing import preprocess_data
    from sklearn.model_selection import train_test_split
    
    print("Loading data...")
    df = load_sample_data()
    
    X = df.drop(['sensor_type', 'sensor_id', 'timestamp', 'value'], axis=1, errors='ignore')
    y = df['value']  # Regression target
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train_processed, X_test_processed = preprocess_data(X_train, X_test)
    
    print("\nTraining Random Forest Regressor...")
    rf_model = RandomForestRegressorModel(n_estimators=100, max_depth=15)
    rf_model.build_model()
    rf_model.train(X_train_processed, y_train)
    
    print("\nEvaluating...")
    metrics = rf_model.evaluate(X_test_processed, y_test)
    print(f"R² Score: {metrics['r2_score']:.4f}")
    print(f"RMSE: {metrics['rmse']:.4f}")