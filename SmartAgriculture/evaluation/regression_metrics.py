"""
Regression Metrics Module

This module provides comprehensive metrics for regression tasks.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    explained_variance_score,
    max_error,
    median_absolute_error,
    mean_absolute_percentage_error
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RegressionMetrics:
    """Comprehensive regression metrics calculator"""
    
    def __init__(self, y_true: np.ndarray, y_pred: np.ndarray):
        """
        Initialize RegressionMetrics
        
        Args:
            y_true: True values
            y_pred: Predicted values
        """
        self.y_true = np.array(y_true)
        self.y_pred = np.array(y_pred)
        self.residuals = self.y_true - self.y_pred
        self.metrics = {}
        
    def calculate_all(self) -> Dict[str, Any]:
        """Calculate all regression metrics"""
        try:
            self.metrics = {
                'mae': self.mae(),
                'mse': self.mse(),
                'rmse': self.rmse(),
                'mape': self.mape(),
                'r2_score': self.r2_score(),
                'explained_variance': self.explained_variance(),
                'max_error': self.max_error(),
                'median_ae': self.median_absolute_error(),
                'mean_residual': float(np.mean(self.residuals)),
                'std_residual': float(np.std(self.residuals)),
                'residuals': self.residuals.tolist()
            }
            
            logger.info("✓ Calculated all regression metrics")
            
            return self.metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate regression metrics: {e}")
            return {}
    
    def mae(self) -> float:
        """Mean Absolute Error"""
        return float(mean_absolute_error(self.y_true, self.y_pred))
    
    def mse(self) -> float:
        """Mean Squared Error"""
        return float(mean_squared_error(self.y_true, self.y_pred))
    
    def rmse(self) -> float:
        """Root Mean Squared Error"""
        return float(np.sqrt(mean_squared_error(self.y_true, self.y_pred)))
    
    def mape(self) -> float:
        """Mean Absolute Percentage Error"""
        try:
            return float(mean_absolute_percentage_error(self.y_true, self.y_pred))
        except:
            # Manual calculation if sklearn version doesn't have it
            return calculate_mape(self.y_true, self.y_pred)
    
    def r2_score(self) -> float:
        """R-squared score"""
        return float(r2_score(self.y_true, self.y_pred))
    
    def explained_variance(self) -> float:
        """Explained variance score"""
        return float(explained_variance_score(self.y_true, self.y_pred))
    
    def max_error(self) -> float:
        """Maximum residual error"""
        return float(max_error(self.y_true, self.y_pred))
    
    def median_absolute_error(self) -> float:
        """Median absolute error"""
        return float(median_absolute_error(self.y_true, self.y_pred))
    
    def adjusted_r2(self, n_features: int = 1) -> float:
        """
        Adjusted R-squared score
        
        Args:
            n_features: Number of features used in the model
            
        Returns:
            Adjusted R² score
        """
        try:
            n = len(self.y_true)
            r2 = self.r2_score()
            
            # Avoid division by zero
            if n - n_features - 1 <= 0:
                return r2
            
            adjusted_r2 = 1 - (1 - r2) * (n - 1) / (n - n_features - 1)
            return float(adjusted_r2)
            
        except Exception as e:
            logger.error(f"Failed to calculate adjusted R²: {e}")
            return 0.0
    
    def mean_bias_error(self) -> float:
        """Mean Bias Error"""
        return float(np.mean(self.residuals))
    
    def root_mean_squared_percentage_error(self) -> float:
        """Root Mean Squared Percentage Error"""
        try:
            percentage_errors = ((self.y_true - self.y_pred) / self.y_true) ** 2
            return float(np.sqrt(np.mean(percentage_errors) * 100))
        except:
            return 0.0
    
    def get_residuals(self) -> np.ndarray:
        """Get residuals"""
        return self.residuals
    
    def get_residual_stats(self) -> Dict[str, float]:
        """Get residual statistics"""
        try:
            return {
                'mean': float(np.mean(self.residuals)),
                'std': float(np.std(self.residuals)),
                'min': float(np.min(self.residuals)),
                'max': float(np.max(self.residuals)),
                'median': float(np.median(self.residuals)),
                'q25': float(np.percentile(self.residuals, 25)),
                'q75': float(np.percentile(self.residuals, 75))
            }
        except Exception as e:
            logger.error(f"Failed to get residual stats: {e}")
            return {}
    
    def residuals_dataframe(self) -> pd.DataFrame:
        """Get residuals as DataFrame for analysis"""
        try:
            return pd.DataFrame({
                'y_true': self.y_true,
                'y_pred': self.y_pred,
                'residuals': self.residuals,
                'residuals_abs': np.abs(self.residuals),
                'residuals_pct': (self.residuals / self.y_true) * 100
            })
        except Exception as e:
            logger.error(f"Failed to create residuals DataFrame: {e}")
            return pd.DataFrame()


def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray,
                       n_features: int = 1) -> Dict[str, Any]:
    """
    Convenience function to evaluate regression model
    
    Args:
        y_true: True values
        y_pred: Predicted values
        n_features: Number of features (for adjusted R²)
        
    Returns:
        Dictionary with all metrics
    """
    evaluator = RegressionMetrics(y_true, y_pred)
    metrics = evaluator.calculate_all()
    
    # Add adjusted R²
    metrics['adjusted_r2'] = evaluator.adjusted_r2(n_features)
    
    return metrics


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Mean Absolute Percentage Error
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        MAPE value (percentage)
    """
    try:
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        # Avoid division by zero
        mask = y_true != 0
        if not np.any(mask):
            return 0.0
        
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        return float(mape)
        
    except Exception as e:
        logger.error(f"Failed to calculate MAPE: {e}")
        return 0.0


def calculate_smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Symmetric Mean Absolute Percentage Error
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        SMAPE value (percentage)
    """
    try:
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        denominator = (np.abs(y_true) + np.abs(y_pred)) / 2
        mask = denominator != 0
        
        if not np.any(mask):
            return 0.0
        
        smape = np.mean(np.abs(y_pred[mask] - y_true[mask]) / denominator[mask]) * 100
        return float(smape)
        
    except Exception as e:
        logger.error(f"Failed to calculate SMAPE: {e}")
        return 0.0


if __name__ == "__main__":
    # Test regression metrics
    from sklearn.datasets import make_regression
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    
    print("Testing regression metrics...")
    
    # Generate sample data
    X, y = make_regression(n_samples=1000, n_features=20, noise=10, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    metrics = evaluate_regression(y_test, y_pred, n_features=20)
    
    # Print results
    print("\nRegression Metrics:")
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            print(f"{key:.<40} {value:.4f}")
        elif isinstance(value, list):
            print(f"{key:.<40} [{len(value)} values]")
        else:
            print(f"{key}: {value}")
    
    # Get residual statistics
    evaluator = RegressionMetrics(y_test, y_pred)
    residual_stats = evaluator.get_residual_stats()
    print("\nResidual Statistics:")
    for key, value in residual_stats.items():
        print(f"{key:.<40} {value:.4f}")
    
    # Test MAPE calculation
    print(f"\nMAPE: {calculate_mape(y_test, y_pred):.4f}%")
    print(f"SMAPE: {calculate_smape(y_test, y_pred):.4f}%")