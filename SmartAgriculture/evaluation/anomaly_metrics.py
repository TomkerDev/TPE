"""
Anomaly Detection Metrics Module

This module provides comprehensive metrics for anomaly detection tasks.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    confusion_matrix,
    classification_report,
    roc_auc_score,
    average_precision_score
)
from sklearn.metrics import precision_recall_curve, roc_curve

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnomalyMetrics:
    """Comprehensive anomaly detection metrics calculator"""
    
    def __init__(self, y_true: np.ndarray, y_pred: np.ndarray,
                 anomaly_scores: Optional[np.ndarray] = None):
        """
        Initialize AnomalyMetrics
        
        Args:
            y_true: True labels (0 = normal, 1 = anomaly)
            y_pred: Predicted labels (1 = normal, -1 = anomaly for Isolation Forest)
            anomaly_scores: Anomaly scores (optional, lower = more anomalous)
        """
        # Convert predictions: -1 (anomaly) -> 1, 1 (normal) -> 0
        self.y_true = np.array(y_true)
        self.y_pred_binary = np.where(y_pred == -1, 1, 0) if np.any(y_pred == -1) else y_pred
        self.anomaly_scores = anomaly_scores
        self.metrics = {}
        
    def calculate_all(self) -> Dict[str, Any]:
        """Calculate all anomaly detection metrics"""
        try:
            self.metrics = {
                'accuracy': self.accuracy(),
                'precision': self.precision(),
                'recall': self.recall(),
                'f1_score': self.f1_score(),
                'specificity': self.specificity(),
                'confusion_matrix': self.confusion_matrix().tolist(),
                'classification_report': self.classification_report(),
                'anomalies_detected': int((self.y_pred_binary == 1).sum()),
                'normal_detected': int((self.y_pred_binary == 0).sum()),
                'total_samples': len(self.y_true),
                'true_anomalies': int(self.y_true.sum()),
                'true_normal': int((self.y_true == 0).sum())
            }
            
            # Add ROC-AUC if scores provided
            if self.anomaly_scores is not None:
                self.metrics['roc_auc'] = self.roc_auc()
                self.metrics['average_precision'] = self.average_precision()
            
            logger.info("✓ Calculated all anomaly detection metrics")
            
            return self.metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate anomaly detection metrics: {e}")
            return {}
    
    def accuracy(self) -> float:
        """Calculate accuracy"""
        return float(accuracy_score(self.y_true, self.y_pred_binary))
    
    def precision(self) -> float:
        """Calculate precision (positive predictive value)"""
        try:
            return float(precision_score(self.y_true, self.y_pred_binary, zero_division=0))
        except:
            return 0.0
    
    def recall(self) -> float:
        """Calculate recall (sensitivity, true positive rate)"""
        try:
            return float(recall_score(self.y_true, self.y_pred_binary, zero_division=0))
        except:
            return 0.0
    
    def f1_score(self) -> float:
        """Calculate F1-score"""
        try:
            return float(f1_score(self.y_true, self.y_pred_binary, zero_division=0))
        except:
            return 0.0
    
    def specificity(self) -> float:
        """Calculate specificity (true negative rate)"""
        try:
            cm = confusion_matrix(self.y_true, self.y_pred_binary)
            tn = cm[0, 0]
            fp = cm[0, 1]
            
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            return float(specificity)
            
        except Exception as e:
            logger.error(f"Failed to calculate specificity: {e}")
            return 0.0
    
    def false_positive_rate(self) -> float:
        """Calculate false positive rate"""
        try:
            return 1 - self.specificity()
        except:
            return 0.0
    
    def confusion_matrix(self) -> np.ndarray:
        """Calculate confusion matrix"""
        return confusion_matrix(self.y_true, self.y_pred_binary)
    
    def classification_report(self) -> str:
        """Generate classification report"""
        return classification_report(self.y_true, self.y_pred_binary, 
                                     target_names=['Normal', 'Anomaly'],
                                     zero_division=0)
    
    def roc_auc(self) -> float:
        """Calculate ROC AUC score"""
        try:
            if self.anomaly_scores is None:
                logger.warning("No anomaly scores provided for ROC AUC")
                return 0.0
            
            # For anomaly detection, we need to invert scores (higher score = more anomalous)
            # If lower scores mean more anomalous, negate them
            scores = -self.anomaly_scores if np.mean(self.anomaly_scores[:10]) < np.mean(self.anomaly_scores[-10:]) else self.anomaly_scores
            
            return float(roc_auc_score(self.y_true, scores))
            
        except Exception as e:
            logger.error(f"Failed to calculate ROC AUC: {e}")
            return 0.0
    
    def average_precision(self) -> float:
        """Calculate Average Precision (AP)"""
        try:
            if self.anomaly_scores is None:
                logger.warning("No anomaly scores provided for Average Precision")
                return 0.0
            
            # Invert scores if needed
            scores = -self.anomaly_scores if np.mean(self.anomaly_scores[:10]) < np.mean(self.anomaly_scores[-10:]) else self.anomaly_scores
            
            return float(average_precision_score(self.y_true, scores))
            
        except Exception as e:
            logger.error(f"Failed to calculate Average Precision: {e}")
            return 0.0
    
    def detection_rate(self, threshold: float = 0.5) -> float:
        """
        Calculate detection rate at given threshold
        
        Args:
            threshold: Threshold for anomaly scores
            
        Returns:
            Detection rate (recall)
        """
        try:
            if self.anomaly_scores is None:
                return 0.0
            
            # Invert scores if needed
            scores = -self.anomaly_scores if np.mean(self.anomaly_scores[:10]) < np.mean(self.anomaly_scores[-10:]) else self.anomaly_scores
            
            y_pred_thresh = np.where(scores >= threshold, 1, 0)
            return float(recall_score(self.y_true, y_pred_thresh, zero_division=0))
            
        except Exception as e:
            logger.error(f"Failed to calculate detection rate: {e}")
            return 0.0
    
    def false_alarm_rate(self, threshold: float = 0.5) -> float:
        """
        Calculate false alarm rate at given threshold
        
        Args:
            threshold: Threshold for anomaly scores
            
        Returns:
            False alarm rate (FPR)
        """
        try:
            if self.anomaly_scores is None:
                return 0.0
            
            # Invert scores if needed
            scores = -self.anomaly_scores if np.mean(self.anomaly_scores[:10]) < np.mean(self.anomaly_scores[-10:]) else self.anomaly_scores
            
            y_pred_thresh = np.where(scores >= threshold, 1, 0)
            fp = ((y_pred_thresh == 1) & (self.y_true == 0)).sum()
            tn = ((y_pred_thresh == 0) & (self.y_true == 0)).sum()
            
            return float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate false alarm rate: {e}")
            return 0.0
    
    def get_roc_curve_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Get ROC curve data
        
        Returns:
            Tuple of (fpr, tpr, thresholds)
        """
        try:
            if self.anomaly_scores is None:
                return np.array([]), np.array([]), np.array([])
            
            # Invert scores if needed
            scores = -self.anomaly_scores if np.mean(self.anomaly_scores[:10]) < np.mean(self.anomaly_scores[-10:]) else self.anomaly_scores
            
            fpr, tpr, thresholds = roc_curve(self.y_true, scores)
            return fpr, tpr, thresholds
            
        except Exception as e:
            logger.error(f"Failed to get ROC curve data: {e}")
            return np.array([]), np.array([]), np.array([])
    
    def get_precision_recall_curve_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Get Precision-Recall curve data
        
        Returns:
            Tuple of (precision, recall, thresholds)
        """
        try:
            if self.anomaly_scores is None:
                return np.array([]), np.array([]), np.array([])
            
            # Invert scores if needed
            scores = -self.anomaly_scores if np.mean(self.anomaly_scores[:10]) < np.mean(self.anomaly_scores[-10:]) else self.anomaly_scores
            
            precision, recall, thresholds = precision_recall_curve(self.y_true, scores)
            return precision, recall, thresholds
            
        except Exception as e:
            logger.error(f"Failed to get Precision-Recall curve data: {e}")
            return np.array([]), np.array([]), np.array([])
    
    def get_threshold_metrics(self, thresholds: np.ndarray) -> pd.DataFrame:
        """
        Calculate metrics at different thresholds
        
        Args:
            thresholds: Array of thresholds to evaluate
            
        Returns:
            DataFrame with metrics at each threshold
        """
        try:
            if self.anomaly_scores is None:
                return pd.DataFrame()
            
            # Invert scores if needed
            scores = -self.anomaly_scores if np.mean(self.anomaly_scores[:10]) < np.mean(self.anomaly_scores[-10:]) else self.anomaly_scores
            
            results = []
            for threshold in thresholds:
                y_pred_thresh = np.where(scores >= threshold, 1, 0)
                
                tp = ((y_pred_thresh == 1) & (self.y_true == 1)).sum()
                fp = ((y_pred_thresh == 1) & (self.y_true == 0)).sum()
                tn = ((y_pred_thresh == 0) & (self.y_true == 0)).sum()
                fn = ((y_pred_thresh == 0) & (self.y_true == 1)).sum()
                
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
                
                results.append({
                    'threshold': threshold,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'fpr': fpr,
                    'tp': tp,
                    'fp': fp,
                    'tn': tn,
                    'fn': fn
                })
            
            return pd.DataFrame(results)
            
        except Exception as e:
            logger.error(f"Failed to calculate threshold metrics: {e}")
            return pd.DataFrame()


def evaluate_anomaly_detection(y_true: np.ndarray, y_pred: np.ndarray,
                               anomaly_scores: Optional[np.ndarray] = None) -> Dict[str, Any]:
    """
    Convenience function to evaluate anomaly detection model
    
    Args:
        y_true: True labels (0 = normal, 1 = anomaly)
        y_pred: Predicted labels (1 = normal, -1 = anomaly)
        anomaly_scores: Anomaly scores (optional)
        
    Returns:
        Dictionary with all metrics
    """
    evaluator = AnomalyMetrics(y_true, y_pred, anomaly_scores)
    return evaluator.calculate_all()


if __name__ == "__main__":
    # Test anomaly detection metrics
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import IsolationForest
    
    print("Testing anomaly detection metrics...")
    
    # Generate sample data (imbalanced - 10% anomalies)
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=2,
                               weights=[0.9, 0.1], n_informative=15, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Isolation Forest (unsupervised)
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X_train)
    
    # Make predictions
    y_pred = model.predict(X_test)  # 1 = normal, -1 = anomaly
    anomaly_scores = model.decision_function(X_test)
    
    # Calculate metrics
    metrics = evaluate_anomaly_detection(y_test, y_pred, anomaly_scores)
    
    # Print results
    print("\nAnomaly Detection Metrics:")
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            print(f"{key:.<40} {value:.4f}")
        elif isinstance(value, str):
            print(f"\n{key}:")
            print(value)
        elif isinstance(value, list):
            print(f"{key:.<40} {value}")
        else:
            print(f"{key}: {value}")
    
    # Get ROC and PR curve data
    evaluator = AnomalyMetrics(y_test, y_pred, anomaly_scores)
    fpr, tpr, thresholds = evaluator.get_roc_curve_data()
    
    print(f"\nROC Curve: {len(fpr)} points")
    print(f"ROC AUC: {metrics.get('roc_auc', 0.0):.4f}")
    
    # Threshold analysis
    threshold_df = evaluator.get_threshold_metrics(np.linspace(-0.5, 0.5, 10))
    print(f"\nThreshold Analysis (first 5):")
    print(threshold_df.head().to_string(index=False))