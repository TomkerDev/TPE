"""
Learning Curve Visualization Module

This module provides functions for plotting learning curves and validation curves.
"""
import pandas as pd
import numpy as np
import logging
import matplotlib.pyplot as plt
from typing import Optional, List, Tuple, Dict, Any
from sklearn.model_selection import learning_curve, validation_curve
from sklearn.model_selection import StratifiedKFold, KFold

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def plot_learning_curve(model, X: np.ndarray, y: np.ndarray,
                       title: str = "Learning Curve",
                       figsize: Tuple[int, int] = (10, 6),
                       cv: int = 5,
                       train_sizes: Optional[np.ndarray] = None,
                       scoring: Optional[str] = None,
                       task_type: str = 'classification',
                       save_path: Optional[str] = None,
                       show: bool = True) -> plt.Figure:
    """
    Plot learning curve showing training and validation scores
    
    Args:
        model: Model object with fit() and score() methods
        X: Features
        y: Target
        title: Plot title
        figsize: Figure size
        cv: Number of cross-validation folds
        train_sizes: Array of training set sizes (optional)
        scoring: Scoring metric (optional)
        task_type: 'classification' or 'regression'
        save_path: Path to save the figure (optional)
        show: Whether to show the figure
        
    Returns:
        Matplotlib figure
    """
    try:
        # Default train sizes
        if train_sizes is None:
            train_sizes = np.linspace(0.1, 1.0, 10)
        
        # Choose CV strategy
        if task_type == 'classification':
            cv_obj = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        else:
            cv_obj = KFold(n_splits=cv, shuffle=True, random_state=42)
        
        # Calculate learning curve
        train_sizes_abs, train_scores, val_scores = learning_curve(
            model, X, y,
            cv=cv_obj,
            train_sizes=train_sizes,
            scoring=scoring,
            n_jobs=-1,
            random_state=42
        )
        
        # Calculate mean and std
        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        val_mean = np.mean(val_scores, axis=1)
        val_std = np.std(val_scores, axis=1)
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot learning curves
        ax.plot(train_sizes_abs, train_mean, 'o-', color='blue', 
               linewidth=2, markersize=6, label='Training Score')
        ax.fill_between(train_sizes_abs, train_mean - train_std, 
                       train_mean + train_std, alpha=0.2, color='blue')
        
        ax.plot(train_sizes_abs, val_mean, 'o-', color='orange', 
               linewidth=2, markersize=6, label='Validation Score')
        ax.fill_between(train_sizes_abs, val_mean - val_std, 
                       val_mean + val_std, alpha=0.2, color='orange')
        
        # Set labels and title
        ax.set_xlabel('Training Set Size', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Set y-axis limits based on task type
        if task_type == 'classification':
            ax.set_ylim([0.0, 1.05])
        else:
            # For regression, use dynamic limits
            y_min = min(val_mean.min(), train_mean.min()) - 0.1
            y_max = max(val_mean.max(), train_mean.max()) + 0.1
            ax.set_ylim([y_min, y_max])
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add legend
        ax.legend(loc='best', fontsize=10)
        
        # Add text box with final scores
        final_train = train_mean[-1]
        final_val = val_mean[-1]
        gap = final_train - final_val
        
        textstr = f'Final Training Score: {final_train:.4f}\n'
        textstr += f'Final Validation Score: {final_val:.4f}\n'
        textstr += f'Gap: {gap:.4f}'
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved learning curve to {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to plot learning curve: {e}")
        return None


def plot_validation_curve(model, X: np.ndarray, y: np.ndarray,
                         param_name: str, param_range: np.ndarray,
                         title: str = "Validation Curve",
                         figsize: Tuple[int, int] = (10, 6),
                         cv: int = 5,
                         scoring: Optional[str] = None,
                         task_type: str = 'classification',
                         save_path: Optional[str] = None,
                         show: bool = True) -> plt.Figure:
    """
    Plot validation curve for a hyperparameter
    
    Args:
        model: Model object
        X: Features
        y: Target
        param_name: Parameter name to vary
        param_range: Range of parameter values
        title: Plot title
        figsize: Figure size
        cv: Number of cross-validation folds
        scoring: Scoring metric (optional)
        task_type: 'classification' or 'regression'
        save_path: Path to save the figure (optional)
        show: Whether to show the figure
        
    Returns:
        Matplotlib figure
    """
    try:
        # Choose CV strategy
        if task_type == 'classification':
            cv_obj = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        else:
            cv_obj = KFold(n_splits=cv, shuffle=True, random_state=42)
        
        # Calculate validation curve
        train_scores, val_scores = validation_curve(
            model, X, y,
            param_name=param_name,
            param_range=param_range,
            cv=cv_obj,
            scoring=scoring,
            n_jobs=-1
        )
        
        # Calculate mean and std
        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        val_mean = np.mean(val_scores, axis=1)
        val_std = np.std(val_scores, axis=1)
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot validation curves
        ax.plot(param_range, train_mean, 'o-', color='blue', 
               linewidth=2, markersize=6, label='Training Score')
        ax.fill_between(param_range, train_mean - train_std, 
                       train_mean + train_std, alpha=0.2, color='blue')
        
        ax.plot(param_range, val_mean, 'o-', color='orange', 
               linewidth=2, markersize=6, label='Validation Score')
        ax.fill_between(param_range, val_mean - val_std, 
                       val_mean + val_std, alpha=0.2, color='orange')
        
        # Set labels and title
        ax.set_xlabel(param_name, fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Set y-axis limits
        if task_type == 'classification':
            ax.set_ylim([0.0, 1.05])
        else:
            y_min = min(val_mean.min(), train_mean.min()) - 0.1
            y_max = max(val_mean.max(), train_mean.max()) + 0.1
            ax.set_ylim([y_min, y_max])
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add legend
        ax.legend(loc='best', fontsize=10)
        
        # Find best parameter
        best_idx = np.argmax(val_mean)
        best_param = param_range[best_idx]
        best_score = val_mean[best_idx]
        
        # Add text box with best parameter
        textstr = f'Best {param_name}: {best_param}\n'
        textstr += f'Best Score: {best_score:.4f}'
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved validation curve to {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to plot validation curve: {e}")
        return None


def plot_learning_curve_comparison(models: Dict[str, Any], X: np.ndarray, y: np.ndarray,
                                  title: str = "Learning Curve Comparison",
                                  figsize: Tuple[int, int] = (12, 7),
                                  cv: int = 5,
                                  train_sizes: Optional[np.ndarray] = None,
                                  scoring: Optional[str] = None,
                                  task_type: str = 'classification',
                                  save_path: Optional[str] = None,
                                  show: bool = True) -> plt.Figure:
    """
    Plot learning curves for multiple models
    
    Args:
        models: Dictionary of model names to model objects
        X: Features
        y: Target
        title: Plot title
        figsize: Figure size
        cv: Number of cross-validation folds
        train_sizes: Array of training set sizes (optional)
        scoring: Scoring metric (optional)
        task_type: 'classification' or 'regression'
        save_path: Path to save the figure (optional)
        show: Whether to show the figure
        
    Returns:
        Matplotlib figure
    """
    try:
        # Default train sizes
        if train_sizes is None:
            train_sizes = np.linspace(0.1, 1.0, 10)
        
        # Choose CV strategy
        if task_type == 'classification':
            cv_obj = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        else:
            cv_obj = KFold(n_splits=cv, shuffle=True, random_state=42)
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(models)))
        
        for (model_name, model), color in zip(models.items(), colors):
            # Calculate learning curve
            train_sizes_abs, train_scores, val_scores = learning_curve(
                model, X, y,
                cv=cv_obj,
                train_sizes=train_sizes,
                scoring=scoring,
                n_jobs=-1,
                random_state=42
            )
            
            # Calculate mean
            train_mean = np.mean(train_scores, axis=1)
            val_mean = np.mean(val_scores, axis=1)
            
            # Plot training score
            ax1.plot(train_sizes_abs, train_mean, 'o-', color=color, 
                    linewidth=2, markersize=5, label=model_name)
            
            # Plot validation score
            ax2.plot(train_sizes_abs, val_mean, 'o-', color=color, 
                    linewidth=2, markersize=5, label=model_name)
        
        # Configure training score plot
        ax1.set_xlabel('Training Set Size', fontsize=11)
        ax1.set_ylabel('Training Score', fontsize=11)
        ax1.set_title('Training Score', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend(loc='lower right', fontsize=9)
        
        if task_type == 'classification':
            ax1.set_ylim([0.0, 1.05])
        
        # Configure validation score plot
        ax2.set_xlabel('Training Set Size', fontsize=11)
        ax2.set_ylabel('Validation Score', fontsize=11)
        ax2.set_title('Validation Score', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.legend(loc='lower right', fontsize=9)
        
        if task_type == 'classification':
            ax2.set_ylim([0.0, 1.05])
        
        plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved learning curve comparison to {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to plot learning curve comparison: {e}")
        return None


def get_learning_curve_data(model, X: np.ndarray, y: np.ndarray,
                           cv: int = 5,
                           train_sizes: Optional[np.ndarray] = None,
                           scoring: Optional[str] = None,
                           task_type: str = 'classification') -> Dict[str, Any]:
    """
    Get learning curve data for analysis
    
    Args:
        model: Model object
        X: Features
        y: Target
        cv: Number of cross-validation folds
        train_sizes: Array of training set sizes (optional)
        scoring: Scoring metric (optional)
        task_type: 'classification' or 'regression'
        
    Returns:
        Dictionary with learning curve data
    """
    try:
        # Default train sizes
        if train_sizes is None:
            train_sizes = np.linspace(0.1, 1.0, 10)
        
        # Choose CV strategy
        if task_type == 'classification':
            cv_obj = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        else:
            cv_obj = KFold(n_splits=cv, shuffle=True, random_state=42)
        
        # Calculate learning curve
        train_sizes_abs, train_scores, val_scores = learning_curve(
            model, X, y,
            cv=cv_obj,
            train_sizes=train_sizes,
            scoring=scoring,
            n_jobs=-1,
            random_state=42
        )
        
        return {
            'train_sizes': train_sizes_abs,
            'train_scores': train_scores,
            'val_scores': val_scores,
            'train_mean': np.mean(train_scores, axis=1),
            'train_std': np.std(train_scores, axis=1),
            'val_mean': np.mean(val_scores, axis=1),
            'val_std': np.std(val_scores, axis=1)
        }
        
    except Exception as e:
        logger.error(f"Failed to get learning curve data: {e}")
        return {}


if __name__ == "__main__":
    # Test learning curve plotting
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.svm import SVC
    
    print("Testing learning curve plotting...")
    
    # Generate sample data
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=2,
                               n_informative=15, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Plot single learning curve
    print("\n1. Single Learning Curve (Random Forest):")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    plot_learning_curve(model, X_train, y_train,
                       title="Random Forest Learning Curve",
                       cv=5,
                       save_path="learning_curve_rf.png")
    
    # Plot validation curve
    print("\n2. Validation Curve (max_depth):")
    plot_validation_curve(
        RandomForestClassifier(n_estimators=100, random_state=42),
        X_train, y_train,
        param_name='max_depth',
        param_range=np.arange(1, 21, 2),
        title="Random Forest - max_depth Validation Curve",
        cv=5,
        save_path="validation_curve_depth.png"
    )
    
    # Plot comparison
    print("\n3. Learning Curve Comparison:")
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(kernel='rbf', random_state=42)
    }
    
    plot_learning_curve_comparison(models, X_train, y_train,
                                  title="Model Learning Curve Comparison",
                                  cv=5,
                                  save_path="learning_curve_comparison.png")
    
    # Get learning curve data
    print("\n4. Learning Curve Data:")
    lc_data = get_learning_curve_data(model, X_train, y_train, cv=5)
    print(f"Training sizes: {lc_data['train_sizes']}")
    print(f"Final training score: {lc_data['train_mean'][-1]:.4f}")
    print(f"Final validation score: {lc_data['val_mean'][-1]:.4f}")