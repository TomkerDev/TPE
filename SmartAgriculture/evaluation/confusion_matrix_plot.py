"""
Confusion Matrix Visualization Module

This module provides functions for plotting confusion matrices.
"""
import pandas as pd
import numpy as np
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Tuple
from sklearn.metrics import confusion_matrix

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray,
                         class_names: Optional[List[str]] = None,
                         title: str = "Confusion Matrix",
                         figsize: Tuple[int, int] = (8, 6),
                         cmap: str = "Blues",
                         normalize: bool = False,
                         save_path: Optional[str] = None,
                         show: bool = True) -> plt.Figure:
    """
    Plot confusion matrix
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        class_names: List of class names
        title: Plot title
        figsize: Figure size
        cmap: Color map
        normalize: Whether to normalize the matrix
        save_path: Path to save the figure (optional)
        show: Whether to show the figure
        
    Returns:
        Matplotlib figure
    """
    try:
        # Calculate confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # Normalize if requested
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            fmt = '.2f'
            title = f"{title} (Normalized)"
        else:
            fmt = 'd'
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot heatmap
        sns.heatmap(cm, annot=True, fmt=fmt, cmap=cmap,
                    xticklabels=class_names,
                    yticklabels=class_names,
                    ax=ax, cbar=True)
        
        # Set labels
        ax.set_xlabel('Predicted Label', fontsize=12)
        ax.set_ylabel('True Label', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Rotate labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        plt.setp(ax.get_yticklabels(), rotation=0)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved confusion matrix to {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to plot confusion matrix: {e}")
        return None


def plot_normalized_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray,
                                     class_names: Optional[List[str]] = None,
                                     title: str = "Normalized Confusion Matrix",
                                     figsize: Tuple[int, int] = (8, 6),
                                     cmap: str = "Blues",
                                     save_path: Optional[str] = None,
                                     show: bool = True) -> plt.Figure:
    """
    Plot normalized confusion matrix (by row)
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        class_names: List of class names
        title: Plot title
        figsize: Figure size
        cmap: Color map
        save_path: Path to save the figure (optional)
        show: Whether to show the figure
        
    Returns:
        Matplotlib figure
    """
    return plot_confusion_matrix(
        y_true, y_pred, class_names, title, figsize, cmap,
        normalize=True, save_path=save_path, show=show
    )


def plot_confusion_matrix_comparison(y_true: np.ndarray,
                                    predictions: Dict[str, np.ndarray],
                                    class_names: Optional[List[str]] = None,
                                    figsize: Tuple[int, int] = (20, 5),
                                    cmap: str = "Blues",
                                    save_path: Optional[str] = None,
                                    show: bool = True) -> plt.Figure:
    """
    Plot confusion matrices for multiple models side by side
    
    Args:
        y_true: True labels
        predictions: Dictionary of model names to predictions
        class_names: List of class names
        figsize: Figure size
        cmap: Color map
        save_path: Path to save the figure (optional)
        show: Whether to show the figure
        
    Returns:
        Matplotlib figure
    """
    try:
        n_models = len(predictions)
        fig, axes = plt.subplots(1, n_models, figsize=figsize)
        
        if n_models == 1:
            axes = [axes]
        
        for idx, (model_name, y_pred) in enumerate(predictions.items()):
            cm = confusion_matrix(y_true, y_pred)
            cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            
            sns.heatmap(cm_normalized, annot=True, fmt='.2f', cmap=cmap,
                       xticklabels=class_names,
                       yticklabels=class_names,
                       ax=axes[idx], cbar=False)
            
            axes[idx].set_xlabel('Predicted Label', fontsize=10)
            axes[idx].set_ylabel('True Label', fontsize=10)
            axes[idx].set_title(model_name, fontsize=12, fontweight='bold')
            
            plt.setp(axes[idx].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        plt.suptitle('Confusion Matrix Comparison (Normalized)', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved confusion matrix comparison to {save_path}")
        
        if show:
            plt.show()
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to plot confusion matrix comparison: {e}")
        return None


def plot_confusion_matrix_with_metrics(y_true: np.ndarray, y_pred: np.ndarray,
                                      class_names: Optional[List[str]] = None,
                                      title: str = "Confusion Matrix with Metrics",
                                      figsize: Tuple[int, int] = (10, 8),
                                      cmap: str = "Blues",
                                      save_path: Optional[str] = None,
                                      show: bool = True) -> plt.Figure:
    """
    Plot confusion matrix with additional metrics
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        class_names: List of class names
        title: Plot title
        figsize: Figure size
        cmap: Color map
        save_path: Path to save the figure (optional)
        show: Whether to show the figure
        
    Returns:
        Matplotlib figure
    """
    try:
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        cm = confusion_matrix(y_true, y_pred)
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Plot raw confusion matrix
        sns.heatmap(cm, annot=True, fmt='d', cmap=cmap,
                   xticklabels=class_names,
                   yticklabels=class_names,
                   ax=ax1, cbar=True)
        ax1.set_xlabel('Predicted Label', fontsize=11)
        ax1.set_ylabel('True Label', fontsize=11)
        ax1.set_title('Raw Counts', fontsize=12, fontweight='bold')
        plt.setp(ax1.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Plot normalized confusion matrix
        sns.heatmap(cm_normalized, annot=True, fmt='.2f', cmap=cmap,
                   xticklabels=class_names,
                   yticklabels=class_names,
                   ax=ax2, cbar=True)
        ax2.set_xlabel('Predicted Label', fontsize=11)
        ax2.set_ylabel('True Label', fontsize=11)
        ax2.set_title('Normalized by Row', fontsize=12, fontweight='bold')
        plt.setp(ax2.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Add metrics text box
        metrics_text = f'Overall Metrics:\n'
        metrics_text += f'Accuracy: {accuracy:.4f}\n'
        metrics_text += f'Precision: {precision:.4f}\n'
        metrics_text += f'Recall: {recall:.4f}\n'
        metrics_text += f'F1-Score: {f1:.4f}'
        
        fig.text(0.5, 0.02, metrics_text, ha='center', fontsize=11,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0.05, 1, 0.98])
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved confusion matrix with metrics to {save_path}")
        
        if show:
            plt.show()
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to plot confusion matrix with metrics: {e}")
        return None


if __name__ == "__main__":
    # Test confusion matrix plotting
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    
    print("Testing confusion matrix plotting...")
    
    # Generate sample data
    X, y = make_classification(n_samples=500, n_features=20, n_classes=3,
                               n_informative=15, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    class_names = ['Class A', 'Class B', 'Class C']
    
    # Plot basic confusion matrix
    print("\n1. Basic Confusion Matrix:")
    plot_confusion_matrix(y_test, y_pred, class_names, 
                         title="Random Forest Confusion Matrix",
                         save_path="confusion_matrix.png")
    
    # Plot normalized confusion matrix
    print("\n2. Normalized Confusion Matrix:")
    plot_normalized_confusion_matrix(y_test, y_pred, class_names,
                                    save_path="confusion_matrix_normalized.png")
    
    # Plot with metrics
    print("\n3. Confusion Matrix with Metrics:")
    plot_confusion_matrix_with_metrics(y_test, y_pred, class_names,
                                      save_path="confusion_matrix_with_metrics.png")
    
    # Plot comparison
    print("\n4. Model Comparison:")
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.svm import SVC
    
    dt_model = DecisionTreeClassifier(max_depth=10, random_state=42)
    dt_model.fit(X_train, y_train)
    dt_pred = dt_model.predict(X_test)
    
    svm_model = SVC(kernel='rbf', random_state=42)
    svm_model.fit(X_train, y_train)
    svm_pred = svm_model.predict(X_test)
    
    predictions = {
        'Random Forest': y_pred,
        'Decision Tree': dt_pred,
        'SVM': svm_pred
    }
    
    plot_confusion_matrix_comparison(y_test, predictions, class_names,
                                    save_path="confusion_matrix_comparison.png")