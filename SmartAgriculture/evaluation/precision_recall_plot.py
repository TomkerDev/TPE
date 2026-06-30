"""
Precision-Recall Curve Visualization Module

This module provides functions for plotting Precision-Recall curves.
"""
import pandas as pd
import numpy as np
import logging
import matplotlib.pyplot as plt
from typing import Optional, List, Tuple, Dict
from sklearn.metrics import precision_recall_curve, average_precision_score
from sklearn.preprocessing import label_binarize

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def plot_precision_recall_curve(y_true: np.ndarray, y_prob: np.ndarray,
                               title: str = "Precision-Recall Curve",
                               figsize: Tuple[int, int] = (8, 6),
                               class_names: Optional[List[str]] = None,
                               save_path: Optional[str] = None,
                               show: bool = True) -> plt.Figure:
    """
    Plot Precision-Recall curve for binary or multiclass classification
    
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
            
            precision, recall, thresholds = precision_recall_curve(y_true, y_prob_binary)
            avg_precision = average_precision_score(y_true, y_prob_binary)
            
            ax.plot(recall, precision, linewidth=2, 
                   label=f'Precision-Recall curve (AP = {avg_precision:.3f})')
            
        else:
            # Multiclass classification
            y_true_bin = label_binarize(y_true, classes=range(n_classes))
            
            # Compute PR curve for each class
            precision = {}
            recall = {}
            avg_precision = {}
            
            for i in range(n_classes):
                precision[i], recall[i], _ = precision_recall_curve(y_true_bin[:, i], y_prob[:, i])
                avg_precision[i] = average_precision_score(y_true_bin[:, i], y_prob[:, i])
            
            # Plot all PR curves
            colors = plt.cm.rainbow(np.linspace(0, 1, n_classes))
            
            for i, color in zip(range(n_classes), colors):
                class_name = class_names[i] if class_names and i < len(class_names) else f'Class {i}'
                ax.plot(recall[i], precision[i], color=color, linewidth=2,
                       label=f'{class_name} (AP = {avg_precision[i]:.3f})')
            
            # Compute micro-average PR curve
            precision_micro, recall_micro, _ = precision_recall_curve(
                y_true_bin.ravel(), y_prob.ravel()
            )
            avg_precision_micro = average_precision_score(y_true_bin, y_prob, average='micro')
            
            ax.plot(recall_micro, precision_micro,
                   label=f'Micro-average (AP = {avg_precision_micro:.3f})',
                   color='deeppink', linestyle=':', linewidth=2)
        
        # Set labels and title
        ax.set_xlabel('Recall', fontsize=12)
        ax.set_ylabel('Precision', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Set limits
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add legend
        ax.legend(loc="lower left", fontsize=10)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved Precision-Recall curve to {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to plot Precision-Recall curve: {e}")
        return None


def plot_precision_recall_multiclass(y_true: np.ndarray, y_prob: np.ndarray,
                                    class_names: List[str],
                                    title: str = "Multiclass Precision-Recall Curves",
                                    figsize: Tuple[int, int] = (10, 8),
                                    save_path: Optional[str] = None,
                                    show: bool = True) -> plt.Figure:
    """
    Plot Precision-Recall curves for each class in multiclass classification
    
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
    return plot_precision_recall_curve(y_true, y_prob, title, figsize, class_names, save_path, show)


def plot_pr_comparison(y_true: np.ndarray,
                      probabilities: Dict[str, np.ndarray],
                      title: str = "Precision-Recall Curve Comparison",
                      figsize: Tuple[int, int] = (10, 8),
                      save_path: Optional[str] = None,
                      show: bool = True) -> plt.Figure:
    """
    Plot Precision-Recall curves for multiple models
    
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
                # Multiclass: use micro-average
                y_true_bin = label_binarize(y_true, classes=range(y_prob.shape[1]))
                precision_micro, recall_micro, _ = precision_recall_curve(
                    y_true_bin.ravel(), y_prob.ravel()
                )
                avg_precision_micro = average_precision_score(y_true_bin, y_prob, average='micro')
                
                ax.plot(recall_micro, precision_micro, color=color, linewidth=2,
                       label=f'{model_name} (AP = {avg_precision_micro:.3f})')
                continue
            
            precision, recall, _ = precision_recall_curve(y_true, y_prob_binary)
            avg_precision = average_precision_score(y_true, y_prob_binary)
            
            ax.plot(recall, precision, color=color, linewidth=2,
                   label=f'{model_name} (AP = {avg_precision:.3f})')
        
        # Set labels and title
        ax.set_xlabel('Recall', fontsize=12)
        ax.set_ylabel('Precision', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Set limits
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add legend
        ax.legend(loc="lower left", fontsize=10)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved Precision-Recall comparison to {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to plot Precision-Recall comparison: {e}")
        return None


def get_precision_recall_data(y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, Any]:
    """
    Get Precision-Recall curve data for plotting or analysis
    
    Args:
        y_true: True labels
        y_prob: Prediction probabilities
        
    Returns:
        Dictionary with PR curve data
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
            
            precision, recall, thresholds = precision_recall_curve(y_true, y_prob_binary)
            avg_precision = average_precision_score(y_true, y_prob_binary)
            
            result = {
                'precision': precision,
                'recall': recall,
                'thresholds': thresholds,
                'average_precision': avg_precision,
                'n_classes': 1
            }
        else:
            # Multiclass classification
            y_true_bin = label_binarize(y_true, classes=range(n_classes))
            
            precision = {}
            recall = {}
            avg_precision = {}
            thresholds = {}
            
            for i in range(n_classes):
                precision[i], recall[i], thresholds[i] = precision_recall_curve(
                    y_true_bin[:, i], y_prob[:, i]
                )
                avg_precision[i] = average_precision_score(y_true_bin[:, i], y_prob[:, i])
            
            # Micro-average
            precision_micro, recall_micro, _ = precision_recall_curve(
                y_true_bin.ravel(), y_prob.ravel()
            )
            avg_precision_micro = average_precision_score(y_true_bin, y_prob, average='micro')
            
            result = {
                'precision_per_class': precision,
                'recall_per_class': recall,
                'thresholds_per_class': thresholds,
                'avg_precision_per_class': avg_precision,
                'precision_micro': precision_micro,
                'recall_micro': recall_micro,
                'avg_precision_micro': avg_precision_micro,
                'n_classes': n_classes
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get Precision-Recall curve data: {e}")
        return {}


def calculate_average_precision(y_true: np.ndarray, y_prob: np.ndarray,
                               average: str = 'macro') -> float:
    """
    Calculate Average Precision (AP) score
    
    Args:
        y_true: True labels
        y_prob: Prediction probabilities
        average: Averaging method ('macro', 'micro', 'weighted')
        
    Returns:
        Average Precision score
    """
    try:
        n_classes = len(np.unique(y_true))
        
        if n_classes == 2:
            if y_prob.ndim == 2:
                y_prob_binary = y_prob[:, 1]
            else:
                y_prob_binary = y_prob
            return float(average_precision_score(y_true, y_prob_binary))
        else:
            return float(average_precision_score(y_true, y_prob, average=average))
            
    except Exception as e:
        logger.error(f"Failed to calculate Average Precision: {e}")
        return 0.0


if __name__ == "__main__":
    # Test Precision-Recall curve plotting
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    
    print("Testing Precision-Recall curve plotting...")
    
    # Generate imbalanced sample data
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=3,
                               n_informative=15, weights=[0.5, 0.3, 0.2], random_state=42)
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
    
    # Plot single PR curve
    print("\n1. Single Precision-Recall Curve (Random Forest):")
    plot_precision_recall_curve(y_test, probabilities['Random Forest'],
                               title="Random Forest Precision-Recall Curve",
                               class_names=class_names,
                               save_path="pr_curve_rf.png")
    
    # Plot PR comparison
    print("\n2. Precision-Recall Comparison:")
    plot_pr_comparison(y_test, probabilities,
                      title="Model Precision-Recall Comparison",
                      save_path="pr_comparison.png")
    
    # Calculate AP scores
    print("\n3. Average Precision Scores:")
    for name, prob in probabilities.items():
        ap = calculate_average_precision(y_test, prob)
        print(f"{name:.<40} {ap:.4f}")
    
    # Get PR data
    print("\n4. Precision-Recall Curve Data:")
    pr_data = get_precision_recall_data(y_test, probabilities['Random Forest'])
    print(f"Number of classes: {pr_data['n_classes']}")
    if 'average_precision' in pr_data:
        print(f"Average Precision: {pr_data['average_precision']:.4f}")
    elif 'avg_precision_micro' in pr_data:
        print(f"Micro Average Precision: {pr_data['avg_precision_micro']:.4f}")