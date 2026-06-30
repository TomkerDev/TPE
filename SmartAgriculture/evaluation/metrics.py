"""
Core Metrics Calculation Module

This module provides unified metrics calculation for all model types.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MetricsResult:
    """Container for metrics results"""
    task_type: str
    metrics: Dict[str, Any]
    predictions: Optional[np.ndarray] = None
    probabilities: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def calculate_all_metrics(y_true: np.ndarray, y_pred: np.ndarray,
                         y_prob: Optional[np.ndarray] = None,
                         task_type: str = 'classification',
                         **kwargs) -> MetricsResult:
    """
    Calculate all relevant metrics based on task type
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_prob: Prediction probabilities (optional)
        task_type: 'classification', 'regression', or 'anomaly'
        **kwargs: Additional arguments
        
    Returns:
        MetricsResult object
    """
    try:
        if task_type == 'classification':
            from .classification_metrics import evaluate_classification
            metrics = evaluate_classification(y_true, y_pred, y_prob)
            
        elif task_type == 'regression':
            from .regression_metrics import evaluate_regression
            metrics = evaluate_regression(y_true, y_pred)
            
        elif task_type == 'anomaly':
            from .anomaly_metrics import evaluate_anomaly_detection
            metrics = evaluate_anomaly_detection(y_true, y_pred)
            
        else:
            raise ValueError(f"Unknown task type: {task_type}")
        
        result = MetricsResult(
            task_type=task_type,
            metrics=metrics,
            predictions=y_pred,
            probabilities=y_prob,
            metadata=kwargs
        )
        
        logger.info(f"✓ Calculated {task_type} metrics")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to calculate metrics: {e}")
        return MetricsResult(task_type=task_type, metrics={})


def format_metrics_report(metrics: Dict[str, Any], 
                         model_name: str = "Model") -> str:
    """
    Format metrics as a readable report
    
    Args:
        metrics: Dictionary of metrics
        model_name: Name of the model
        
    Returns:
        Formatted report string
    """
    try:
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"Metrics Report: {model_name}")
        lines.append(f"{'='*60}")
        
        for key, value in metrics.items():
            if isinstance(value, (int, float, np.floating, np.integer)):
                lines.append(f"{key:.<40} {value:.4f}")
            elif isinstance(value, dict):
                lines.append(f"\n{key}:")
                for k, v in value.items():
                    if isinstance(v, (int, float, np.floating, np.integer)):
                        lines.append(f"  {k:.<38} {v:.4f}")
                    else:
                        lines.append(f"  {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"{key:.<40} {value}")
            else:
                lines.append(f"{key:.<40} {value}")
        
        lines.append(f"{'='*60}\n")
        
        return "\n".join(lines)
        
    except Exception as e:
        logger.error(f"Failed to format metrics report: {e}")
        return f"Error formatting report: {e}"


def compare_metric_scores(results: Dict[str, MetricsResult],
                         metric: str = 'accuracy') -> pd.DataFrame:
    """
    Compare a specific metric across multiple models
    
    Args:
        results: Dictionary of model names to MetricsResult
        metric: Metric to compare
        
    Returns:
        DataFrame with comparison
    """
    try:
        comparison_data = []
        
        for model_name, result in results.items():
            score = result.metrics.get(metric, 0.0)
            comparison_data.append({
                'Model': model_name,
                'Task': result.task_type,
                metric: score
            })
        
        df = pd.DataFrame(comparison_data)
        df = df.sort_values(metric, ascending=False)
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to compare metric scores: {e}")
        return pd.DataFrame()


def aggregate_cross_validation_scores(scores: np.ndarray) -> Dict[str, float]:
    """
    Aggregate cross-validation scores
    
    Args:
        scores: Array of CV scores
        
    Returns:
        Dictionary with aggregated statistics
    """
    try:
        return {
            'mean': float(np.mean(scores)),
            'std': float(np.std(scores)),
            'min': float(np.min(scores)),
            'max': float(np.max(scores)),
            'median': float(np.median(scores)),
            'q25': float(np.percentile(scores, 25)),
            'q75': float(np.percentile(scores, 75))
        }
        
    except Exception as e:
        logger.error(f"Failed to aggregate CV scores: {e}")
        return {}


def calculate_confidence_interval(scores: np.ndarray, 
                                 confidence: float = 0.95) -> tuple:
    """
    Calculate confidence interval for scores
    
    Args:
        scores: Array of scores
        confidence: Confidence level (0-1)
        
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    try:
        from scipy import stats
        
        n = len(scores)
        mean = np.mean(scores)
        se = stats.sem(scores)
        
        # Calculate confidence interval
        ci = se * stats.t.ppf((1 + confidence) / 2, n - 1)
        
        return (float(mean - ci), float(mean + ci))
        
    except Exception as e:
        logger.error(f"Failed to calculate confidence interval: {e}")
        return (0.0, 0.0)


if __name__ == "__main__":
    # Test metrics calculation
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    
    print("Testing metrics calculation...")
    
    # Generate sample data
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=3, 
                               n_informative=15, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)
    
    # Calculate metrics
    result = calculate_all_metrics(
        y_true=y_test,
        y_pred=y_pred,
        y_prob=y_prob,
        task_type='classification'
    )
    
    # Print report
    print(format_metrics_report(result.metrics, "Random Forest"))
    
    # Test regression metrics
    from sklearn.datasets import make_regression
    from sklearn.linear_model import LinearRegression
    
    print("\n" + "="*60)
    print("Testing regression metrics...")
    
    X_reg, y_reg = make_regression(n_samples=1000, n_features=20, random_state=42)
    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)
    
    reg_model = LinearRegression()
    reg_model.fit(X_train_r, y_train_r)
    y_pred_r = reg_model.predict(X_test_r)
    
    reg_result = calculate_all_metrics(
        y_true=y_test_r,
        y_pred=y_pred_r,
        task_type='regression'
    )
    
    print(format_metrics_report(reg_result.metrics, "Linear Regression"))