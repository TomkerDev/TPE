"""
Linear Regression Model
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinearRegressionModel:
    """Linear Regression model"""
    
    def __init__(self):
        """Initialize Linear Regression model"""
        self.model = None
        self.coefficients = None
        self.intercept = None
        
    def build_model(self) -> LinearRegression:
        """Build Linear Regression model"""
        try:
            self.model = LinearRegression()
            
            logger.info("✓ Built Linear Regression model")
            
            return self.model
            
        except Exception as e:
            logger.error(f"Failed to build Linear Regression model: {e}")
            return None
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> bool:
        """Train the model"""
        try:
            if self.model is None:
                self.build_model()
            
            self.model.fit(X_train, y_train)
            
            # Store coefficients
            self.coefficients = self.model.coef_
            self.intercept = self.model.intercept_
            
            logger.info("✓ Linear Regression model trained successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to train Linear Regression model: {e}")
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
    
    def get_coefficients(self, feature_names: list = None) -> pd.DataFrame:
        """Get model coefficients"""
        try:
            if self.coefficients is None:
                return pd.DataFrame()
            
            if feature_names is None:
                feature_names = [f'feature_{i}' for i in range(len(self.coefficients))]
            
            coef_df = pd.DataFrame({
                'feature': feature_names,
                'coefficient': self.coefficients
            }).sort_values('coefficient', key=abs, ascending=False)
            
            return coef_df
            
        except Exception as e:
            logger.error(f"Failed to get coefficients: {e}")
            return pd.DataFrame()
    
    def save_model(self, filepath: str = 'models/linear_regression.pkl'):
        """Save model to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'coefficients': self.coefficients,
                'intercept': self.intercept
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"✓ Saved Linear Regression model to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self, filepath: str = 'models/linear_regression.pkl'):
        """Load model from file"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"Model file not found: {filepath}")
                return False
            
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.coefficients = model_data.get('coefficients')
            self.intercept = model_data.get('intercept')
            
            logger.info(f"✓ Loaded Linear Regression model from {filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


def train_linear_regression(X_train: np.ndarray, y_train: np.ndarray) -> LinearRegressionModel:
    """Convenience function to train Linear Regression"""
    model = LinearRegressionModel()
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
    y = df['value']  # Regression target
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train_processed, X_test_processed = preprocess_data(X_train, X_test)
    
    print("\nTraining Linear Regression...")
    lr_model = LinearRegressionModel()
    lr_model.build_model()
    lr_model.train(X_train_processed, y_train)
    
    print("\nEvaluating...")
    metrics = lr_model.evaluate(X_test_processed, y_test)
    print(f"R² Score: {metrics['r2_score']:.4f}")
    print(f"RMSE: {metrics['rmse']:.4f}")