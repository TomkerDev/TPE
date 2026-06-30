"""
Classification Metrics Module

This module provides comprehensive metrics for classification tasks.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score,
    log_loss,
    cohen_kappa_score,
    matthews_corrcoef
)
from sklearn.preprocessing import label_binarize

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClassificationMetrics:
    """Comprehensive classification metrics calculator"""
    
    def __init__(self, y_true: np.ndarray, y_pred: np.ndarray, 
                 y_prob: Optional[np.ndarray] = None,
                 class_names: Optional[list] = None):
        """
        Initialize ClassificationMetrics
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_prob: Prediction probabilities (optional)
            class_names: List of class names (optional)
        """
        self.y_true = y_true
        self.y_pred = y_pred
        self.y_prob = y_prob
        self.class_names = class_names or [f'Class {i}' for i in range(len(np.unique(y_true)))]
        self.n_classes = len(np.unique(y_true))
        self.metrics = {}
        
    def calculate_all(self) -> Dict[str, Any]:
        """Calculate all classification metrics"""
        try:
            self.metrics = {
                'accuracy': self.accuracy(),
                'precision': self.precision(),
                'recall': self.recall(),
                'f1_score': self.f1_score(),
                'specificity': self.specificity(),
                'balanced_accuracy': self.balanced_accuracy(),
                'cohen_kappa': self.cohen_kappa(),
                'matthews_corrcoef': self.matthews_corrcoef(),
                'confusion_matrix': self.confusion_matrix().tolist(),
                'classification_report': self.classification_report()
            }
            
            # Add ROC-AUC if probabilities provided
            if self.y_prob is not None:
                self.metrics['roc_auc'] = self.roc_auc()
                self.metrics['log_loss'] = self.log_loss()
            
            logger.info("✓ Calculated all classification metrics")
            
            return self.metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate classification metrics: {e}")
            return {}
    
    def accuracy(self) -> float:
        """Calculate accuracy"""
        return float(accuracy_score(self.y_true, self.y_pred))
    
    def precision(self, average: str = 'weighted') -> float:
        """Calculate precision"""
        try:
            return float(precision_score(self.y_true, self.y_pred, average=average, zero_division=0))
        except:
            return 0.0
    
    def recall(self, average: str = 'weighted') -> float:
        """Calculate recall (sensitivity)"""
        try:
            return float(recall_score(self.y_true, self.y_pred, average=average, zero_division=0))
        except:
            return 0.0
    
    def f1_score(self, average: str = 'weighted') -> float:
        """Calculate F1-score"""
        try:
            return float(f1_score(self.y_true, self.y_pred, average=average, zero_division=0))
        except:
            return 0.0
    
    def specificity(self) -> float:
        """Calculate specificity (true negative rate)"""
        try:
            cm = confusion_matrix(self.y_true, self.y_pred)
            specificity_per_class = []
            
            for i in range(len(cm)):
                tp = cm[i, i]
                fp = cm[:, i].sum() - tp
                fn = cm[i, :].sum() - tp
                tn = cm.sum() - tp - fp - fn
                
                specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
                specificity_per_class.append(specificity)
            
            return float(np.mean(specificity_per_class))
            
        except Exception as e:
            logger.error(f"Failed to calculate specificity: {e}")
            return 0.0
    
    def balanced_accuracy(self) -> float:
        """Calculate balanced accuracy"""
        try:
            return float(recall_score(self.y_true, self.y_pred, average='macro', zero_division=0))
        except:
            return 0.0
    
    def cohen_kappa(self) -> float:
        """Calculate Cohen's Kappa"""
        try:
            return float(cohen_kappa_score(self.y_true, self.y_pred))
        except:
            return 0.0
    
    def matthews_corrcoef(self) -> float:
        """Calculate Matthews Correlation Coefficient"""
        try:
            return float(matthews_corrcoef(self.y_true, self.y_pred))
        except:
            return 0.0
    
    def confusion_matrix(self) -> np.ndarray:
        """Calculate confusion matrix"""
        return confusion_matrix(self.y_true, self.y_pred)
    
    def classification_report(self) -> str:
        """Generate classification report"""
        return classification_report(self.y_true, self.y_pred, 
                                     target_names=self.class_names,
                                     zero_division=0)
    
    def roc_auc(self, average: str = 'macro') -> float:
        """Calculate ROC AUC score"""
        try:
            if self.y_prob is None:
                logger.warning("No probabilities provided for ROC AUC")
                return 0.0
            
            # Handle binary and multiclass
            if self.n_classes == 2:
                # Binary classification
                if self.y_prob.ndim == 2:
                    y_prob_binary = self.y_prob[:, 1]
                else:
                    y_prob_binary = self.y_prob
                return float(roc_auc_score(self.y_true, y_prob_binary))
            else:
                # Multiclass classification
                y_true_bin = label_binarize(self.y_true, classes=range(self.n_classes))
                return float(roc_auc_score(y_true_bin, self.y_prob, 
                                          multi_class='ovr', average=average))
        except Exception as e:
            logger.error(f"Failed to calculate ROC AUC: {e}")
            return 0.0
    
    def log_loss(self) -> float:
        """Calculate log loss"""
        try:
            if self.y_prob is None:
                logger.warning("No probabilities provided for log loss")
                return 0.0
            
            return float(log_loss(self.y_true, self.y_prob))
        except Exception as e:
            logger.error(f"Failed to calculate log loss: {e}")
            return 0.0
    
    def per_class_metrics(self) -> pd.DataFrame:
        """Calculate per-class metrics"""
        try:
            cm = confusion_matrix(self.y_true, self.y_pred)
            
            per_class = []
            for i in range(len(cm)):
                tp = cm[i, i]
                fp = cm[:, i].sum() - tp
                fn = cm[i, :].sum() - tp
                tn = cm.sum() - tp - fp - fn
                
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
                
                per_class.append({
                    'Class': self.class_names[i] if i < len(self.class_names) else f'Class {i}',
                    'Precision': precision,
                    'Recall': recall,
                    'F1-Score': f1,
                    'Specificity': specificity,
                    'Support': cm[i, :].sum()
                })
            
            return pd.DataFrame(per_class)
            
        except Exception as e:
            logger.error(f"Failed to calculate per-class metrics: {e}")
            return pd.DataFrame()


def evaluate_classification(y_true: np.ndarray, y_pred: np.ndarray,
                           y_prob: Optional[np.ndarray] = None,
                           class_names: Optional[list] = None) -> Dict[str, Any]:
    """
    Convenience function to evaluate classification model
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_prob: Prediction probabilities (optional)
        class_names: List of class names (optional)
        
    Returns:
        Dictionary with all metrics
    """
    evaluator = ClassificationMetrics(y_true, y_pred, y_prob, class_names)
    return evaluator.calculate_all()


if __name__ == "__main__":
    # Test classification metrics
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    
    print("Testing classification metrics...")
    
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
    metrics = evaluate_classification(
        y_true=y_test,
        y_pred=y_pred,
        y_prob=y_prob,
        class_names=['Class A', 'Class B', 'Class C']
    )
    
    # Print results
    print("\nClassification Metrics:")
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            print(f"{key:.<40} {value:.4f}")
        elif isinstance(value, str):
            print(f"\n{key}:")
            print(value)
        else:
            print(f"{key}: {value}")
    
    # Per-class metrics
    evaluator = ClassificationMetrics(y_test, y_pred, y_prob, ['Class A', 'Class B', 'Class C'])
    per_class = evaluator.per_class_metrics()
    print("\nPer-Class Metrics:")
    print(per_class.to_string(index=False))