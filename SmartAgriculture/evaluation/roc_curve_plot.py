"""
ROC Curve Visualization Module

This module provides functions for plotting ROC curves and AUC scores.
"""
import pandas as pd
import numpy as np
import logging
import matplotlib.pyplot as plt
from typing import Optional, List, Tuple, Dict
from sklearn.metrics import roc_curve, auc, roc_auc_score
from sklearn.preprocessing import label_binarize

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def plot_roc_curve(y_true: np.ndarray, y_prob: np.ndarray,
                  title: str = "ROC Curve",
                  figsize: Tuple[int, int] = (8, 6),
                  class_names: Optional[List[str]] = None,
                  save_path: Optional[str] = None,
                  show: bool = True) -> plt.Figure:
    """
    Plot ROC curve for binary or multiclass classification
    
    Args:
        y_true: True labels
        y_prob: Prediction probabilities
        title: Plot title
        figsize: Figure size
        class_names: List of class names (for multiclass)
        save_path: Path to save the figure (optional)
        show: Whether to show the figure
        
    Returns:
        Matplotlib figure
    """
    try:
        fig, ax = plt.subplots(figsize=figsize)
        
        n_classes = len(np.unique(y_true))
        
        if n_classes == 2:
            # Binary classification
            if y_prob.ndim == 2:
                y_prob_binary = y_prob[:, 1]
            else:
                y_prob_binary = y_prob
            
            fpr, tpr, thresholds = roc_curve(y_true, y_prob_binary)
            roc_auc = auc(fpr, tpr)
            
            ax.plot(fpr, tpr, linewidth=2, label=f'ROC curve (AUC = {roc_auc:.3f})')
            
        else:
            # Multiclass classification
            y_true_bin = label_binarize(y_true, classes=range(n_classes))
            
            # Compute ROC curve and ROC area for each class
            fpr = {}
            tpr = {}
            roc_auc = {}
            
            for i in range(n_classes):
                fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_prob[:, i])
                roc_auc[i] = auc(fpr[i], tpr[i])
            
            # Plot all ROC curves
            colors = plt.cm.rainbow(np.linspace(0, 1, n_classes))
            
            for i, color in zip(range(n_classes), colors):
                class_name = class_names[i] if class_names and i < len(class_names) else f'Class {i}'
                ax.plot(fpr[i], tpr[i], color=color, linewidth=2,
                       label=f'{class_name} (AUC = {roc_auc[i]:.3f})')
            
            # Compute micro-average ROC curve
            fpr["micro"], tpr["micro"], _ = roc_curve(y_true_bin.ravel(), y_prob.ravel())
            roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
            
            # Compute macro-average ROC curve
            all_fpr = np.unique(np.concatenate([fpr[i] for i in range(n_classes)]))
            mean_tpr = np.zeros_like(all_fpr)
            for i in range(n_classes):
                mean_tpr += np.interp(all_fpr, fpr[i], tpr[i])
            mean_tpr /= n_classes
            
            fpr["macro"] = all_fpr
            tpr["macro"] = mean_tpr
            roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])
            
            ax.plot(fpr["micro"], tpr["micro"],
                   label=f'Micro-average (AUC = {roc_auc["micro"]:.3f})',
                   color='deeppink', linestyle=':', linewidth=2)
            
            ax.plot(fpr["macro"], tpr["macro"],
                   label=f'Macro-average (AUC = {roc_auc["macro"]:.3f})',
                   color='navy', linestyle=':', linewidth=2)
        
        # Plot diagonal line
        ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random Classifier')
        
        # Set labels and title
        ax.set_xlabel('False Positive Rate (FPR)', fontsize=12)
        ax.set_ylabel('True Positive Rate (TPR)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Set limits
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add legend
        ax.legend(loc="lower right", fontsize=10)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved ROC curve to {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to plot ROC curve: {e}")
        return None


def plot_multiclass_roc(y_true: np.ndarray, y_prob: np.ndarray,
                       class_names: List[str],
                       title: str = "Multiclass ROC Curves",
                       figsize: Tuple[int, int] = (10, 8),
                       save_path: Optional[str] = None,
                       show: bool = True) -> plt.Figure:
    """
    Plot ROC curves for each class in multiclass classification
    
    Args:
        y_true: True labels
        y_prob: Prediction probabilities
        class_names: List of class names
        title: Plot title
        figsize: Figure size
        save_path: Path to save the figure (optional)
        show: Whether to show the figure
        
    Returns:
        Matplotlib figure
    """
    return plot_roc_curve(y_true, y_prob, title, figsize, class_names, save_path, show)


def plot_roc_comparison(y_true: np.ndarray,
                       probabilities: Dict[str, np.ndarray],
                       title: str = "ROC Curve Comparison",
                       figsize: Tuple[int, int] = (10, 8),
                       save_path: Optional[str] = None,
                       show: bool = True) -> plt.Figure:
    """
    Plot ROC curves for multiple models
    
    Args:
        y_true: True labels
        probabilities: Dictionary of model names to prediction probabilities
        title: Plot title
        figsize: Figure size
        save_path: Path to save the figure (optional)
        show: Whether to show the figure
        
    Returns:
        Matplotlib figure
    """
    try:
        fig, ax = plt.subplots(figsize=figsize)
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(probabilities)))
        
        for (model_name, y_prob), color in zip(probabilities.items(), colors):
            # Handle binary and multiclass
            if y_prob.ndim == 2 and y_prob.shape[1] == 2:
                y_prob_binary = y_prob[:, 1]
            elif y_prob.ndim == 1:
                y_prob_binary = y_prob
            else:
                # Multiclass: use macro-average
                y_true_bin = label_binarize(y_true, classes=range(y_prob.shape[1]))
                fpr_micro, tpr_micro, _ = roc_curve(y_true_bin.ravel(), y_prob.ravel())
                roc_auc_micro = auc(fpr_micro, tpr_micro)
                
                ax.plot(fpr_micro, tpr_micro, color=color, linewidth=2,
                       label=f'{model_name} (AUC = {roc_auc_micro:.3f})')
                continue
            
            fpr, tpr, _ = roc_curve(y_true, y_prob_binary)
            roc_auc = auc(fpr, tpr)
            
            ax.plot(fpr, tpr, color=color, linewidth=2,
                   label=f'{model_name} (AUC = {roc_auc:.3f})')
        
        # Plot diagonal line
        ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random Classifier')
        
        # Set labels and title
        ax.set_xlabel('False Positive Rate (FPR)', fontsize=12)
        ax.set_ylabel('True Positive Rate (TPR)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Set limits
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add legend
        ax.legend(loc="lower right", fontsize=10)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved ROC comparison to {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to plot ROC comparison: {e}")
        return None


def get_roc_curve_data(y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, Any]:
    """
    Get ROC curve data for plotting or analysis
    
    Args:
        y_true: True labels
        y_prob: Prediction probabilities
        
    Returns:
        Dictionary with ROC curve data
    """
    try:
        n_classes = len(np.unique(y_true))
        result = {}
        
        if n_classes == 2:
            # Binary classification
            if y_prob.ndim == 2:
                y_prob_binary = y_prob[:, 1]
            else:
                y_prob_binary = y_prob
            
            fpr, tpr, thresholds = roc_curve(y_true, y_prob_binary)
            roc_auc = auc(fpr, tpr)
            
            result = {
                'fpr': fpr,
                'tpr': tpr,
                'thresholds': thresholds,
                'auc': roc_auc,
                'n_classes': 1
            }
        else:
            # Multiclass classification
            y_true_bin = label_binarize(y_true, classes=range(n_classes))
            
            fpr = {}
            tpr = {}
            roc_auc = {}
            thresholds = {}
            
            for i in range(n_classes):
                fpr[i], tpr[i], thresholds[i] = roc_curve(y_true_bin[:, i], y_prob[:, i])
                roc_auc[i] = auc(fpr[i], tpr[i])
            
            # Micro-average
            fpr_micro, tpr_micro, _ = roc_curve(y_true_bin.ravel(), y_prob.ravel())
            roc_auc_micro = auc(fpr_micro, tpr_micro)
            
            result = {
                'fpr_per_class': fpr,
                'tpr_per_class': tpr,
                'thresholds_per_class': thresholds,
                'auc_per_class': roc_auc,
                'fpr_micro': fpr_micro,
                'tpr_micro': tpr_micro,
                'auc_micro': roc_auc_micro,
                'n_classes': n_classes
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get ROC curve data: {e}")
        return {}


def calculate_auc_score(y_true: np.ndarray, y_prob: np.ndarray,
                       average: str = 'macro') -> float:
    """
    Calculate AUC score
    
    Args:
        y_true: True labels
        y_prob: Prediction probabilities
        average: Averaging method ('macro', 'micro', 'weighted')
        
    Returns:
        AUC score
    """
    try:
        n_classes = len(np.unique(y_true))
        
        if n_classes == 2:
            if y_prob.ndim == 2:
                y_prob_binary = y_prob[:, 1]
            else:
                y_prob_binary = y_prob
            return float(roc_auc_score(y_true, y_prob_binary))
        else:
            y_true_bin = label_binarize(y_true, classes=range(n_classes))
            return float(roc_auc_score(y_true_bin, y_prob, multi_class='ovr', average=average))
            
    except Exception as e:
        logger.error(f"Failed to calculate AUC score: {e}")
        return 0.0


if __name__ == "__main__":
    # Test ROC curve plotting
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    
    print("Testing ROC curve plotting...")
    
    # Generate sample data
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=3,
                               n_informative=15, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    class_names = ['Class A', 'Class B', 'Class C']
    
    # Train multiple models
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42)
    }
    
    probabilities = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        probabilities[name] = model.predict_proba(X_test)
    
    # Plot single ROC curve
    print("\n1. Single ROC Curve (Random Forest):")
    plot_roc_curve(y_test, probabilities['Random Forest'], 
                  title="Random Forest ROC Curve",
                  class_names=class_names,
                  save_path="roc_curve_rf.png")
    
    # Plot ROC comparison
    print("\n2. ROC Curve Comparison:")
    plot_roc_comparison(y_test, probabilities,
                       title="Model ROC Comparison",
                       save_path="roc_comparison.png")
    
    # Calculate AUC scores
    print("\n3. AUC Scores:")
    for name, prob in probabilities.items():
        auc = calculate_auc_score(y_test, prob)
        print(f"{name:.<40} {auc:.4f}")
    
    # Get ROC data
    print("\n4. ROC Curve Data:")
    roc_data = get_roc_curve_data(y_test, probabilities['Random Forest'])
    print(f"Number of classes: {roc_data['n_classes']}")
    if 'auc' in roc_data:
        print(f"AUC: {roc_data['auc']:.4f}")
    elif 'auc_micro' in roc_data:
        print(f"Micro AUC: {roc_data['auc_micro']:.4f}")