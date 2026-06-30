"""
Model Comparison Module

This module provides tools for comparing multiple models performance.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
import json
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ModelResult:
    """Container for model evaluation results"""
    model_name: str
    model_type: str
    task_type: str
    metrics: Dict[str, Any]
    predictions: Optional[np.ndarray] = None
    probabilities: Optional[np.ndarray] = None
    training_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ModelComparator:
    """Compare multiple models"""
    
    def __init__(self):
        """Initialize ModelComparator"""
        self.results: Dict[str, ModelResult] = {}
        
    def add_result(self, result: ModelResult):
        """Add a model result"""
        self.results[result.model_name] = result
        logger.info(f"✓ Added result for {result.model_name}")
    
    def add_results(self, results: List[ModelResult]):
        """Add multiple model results"""
        for result in results:
            self.results[result.model_name] = result
        logger.info(f"✓ Added {len(results)} results")
    
    def compare(self, metric: str = 'accuracy') -> pd.DataFrame:
        """
        Compare models by a specific metric
        
        Args:
            metric: Metric to compare by
            
        Returns:
            DataFrame with comparison
        """
        try:
            if not self.results:
                logger.warning("No results to compare")
                return pd.DataFrame()
            
            comparison_data = []
            
            for model_name, result in self.results.items():
                score = result.metrics.get(metric, 0.0)
                comparison_data.append({
                    'Model': model_name,
                    'Type': result.model_type,
                    'Task': result.task_type,
                    metric: score,
                    'Training Time (s)': result.training_time
                })
            
            df = pd.DataFrame(comparison_data)
            df = df.sort_values(metric, ascending=False)
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to compare models: {e}")
            return pd.DataFrame()
    
    def compare_multiple_metrics(self, metrics: List[str] = None) -> pd.DataFrame:
        """
        Compare models by multiple metrics
        
        Args:
            metrics: List of metrics to compare
            
        Returns:
            DataFrame with comparison
        """
        try:
            if not self.results:
                logger.warning("No results to compare")
                return pd.DataFrame()
            
            if metrics is None:
                # Auto-detect metrics based on task type
                metrics = []
                for result in self.results.values():
                    if result.task_type == 'classification':
                        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
                    elif result.task_type == 'regression':
                        metrics = ['r2_score', 'rmse', 'mae']
                    elif result.task_type == 'anomaly':
                        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
                    break
            
            comparison_data = []
            
            for model_name, result in self.results.items():
                row = {
                    'Model': model_name,
                    'Type': result.model_type,
                    'Task': result.task_type,
                    'Training Time (s)': result.training_time
                }
                
                for metric in metrics:
                    row[metric] = result.metrics.get(metric, 0.0)
                
                comparison_data.append(row)
            
            df = pd.DataFrame(comparison_data)
            
            # Sort by first metric
            if metrics:
                df = df.sort_values(metrics[0], ascending=False)
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to compare multiple metrics: {e}")
            return pd.DataFrame()
    
    def get_best_model(self, metric: str = 'accuracy') -> Optional[ModelResult]:
        """
        Get the best performing model
        
        Args:
            metric: Metric to use for ranking
            
        Returns:
            ModelResult of best model
        """
        try:
            if not self.results:
                logger.warning("No results available")
                return None
            
            best_model_name = max(self.results.keys(), 
                                 key=lambda x: self.results[x].metrics.get(metric, 0.0))
            best_result = self.results[best_model_name]
            
            logger.info(f"Best model: {best_model_name} with {metric}={best_result.metrics.get(metric, 0.0):.4f}")
            
            return best_result
            
        except Exception as e:
            logger.error(f"Failed to get best model: {e}")
            return None
    
    def get_ranking(self, metric: str = 'accuracy', top_n: int = None) -> List[Tuple[str, float]]:
        """
        Get ranking of models
        
        Args:
            metric: Metric to rank by
            top_n: Number of top models to return (None for all)
            
        Returns:
            List of (model_name, score) tuples
        """
        try:
            if not self.results:
                return []
            
            ranking = sorted(
                [(name, result.metrics.get(metric, 0.0)) 
                 for name, result in self.results.items()],
                key=lambda x: x[1],
                reverse=True
            )
            
            if top_n is not None:
                ranking = ranking[:top_n]
            
            return ranking
            
        except Exception as e:
            logger.error(f"Failed to get ranking: {e}")
            return []
    
    def generate_comparison_table(self, metrics: List[str] = None,
                                 output_file: str = None) -> str:
        """
        Generate a formatted comparison table
        
        Args:
            metrics: List of metrics to include
            output_file: File to save table (optional)
            
        Returns:
            Formatted table string
        """
        try:
            df = self.compare_multiple_metrics(metrics)
            
            if df.empty:
                return "No results to compare"
            
            # Format table
            table = df.to_string(index=False)
            
            # Save if file provided
            if output_file:
                df.to_csv(output_file, index=False)
                logger.info(f"✓ Saved comparison table to {output_file}")
            
            return table
            
        except Exception as e:
            logger.error(f"Failed to generate comparison table: {e}")
            return f"Error: {e}"
    
    def save_results(self, filepath: str = None) -> str:
        """
        Save all results to JSON file
        
        Args:
            filepath: Path to save results
            
        Returns:
            Path where results were saved
        """
        try:
            if filepath is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filepath = f'results/model_comparison_{timestamp}.json'
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Convert results to serializable format
            results_data = {}
            for model_name, result in self.results.items():
                results_data[model_name] = {
                    'model_name': result.model_name,
                    'model_type': result.model_type,
                    'task_type': result.task_type,
                    'metrics': result.metrics,
                    'training_time': result.training_time,
                    'metadata': result.metadata
                }
            
            # Save to JSON
            with open(filepath, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            logger.info(f"✓ Saved comparison results to {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return ""
    
    def load_results(self, filepath: str) -> bool:
        """
        Load results from JSON file
        
        Args:
            filepath: Path to results file
            
        Returns:
            True if loading successful
        """
        try:
            if not os.path.exists(filepath):
                logger.error(f"Results file not found: {filepath}")
                return False
            
            with open(filepath, 'r') as f:
                results_data = json.load(f)
            
            # Convert to ModelResult objects
            self.results = {}
            for model_name, data in results_data.items():
                result = ModelResult(
                    model_name=data['model_name'],
                    model_type=data['model_type'],
                    task_type=data['task_type'],
                    metrics=data['metrics'],
                    training_time=data.get('training_time', 0.0),
                    metadata=data.get('metadata', {})
                )
                self.results[model_name] = result
            
            logger.info(f"✓ Loaded {len(self.results)} results from {filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load results: {e}")
            return False
    
    def clear(self):
        """Clear all results"""
        self.results = {}
        logger.info("✓ Cleared all results")


def compare_models(results: Dict[str, ModelResult],
                   metric: str = 'accuracy') -> pd.DataFrame:
    """
    Convenience function to compare models
    
    Args:
        results: Dictionary of model results
        metric: Metric to compare by
        
    Returns:
        DataFrame with comparison
    """
    comparator = ModelComparator()
    comparator.add_results(list(results.values()))
    return comparator.compare(metric)


def create_comparison_table(results: Dict[str, ModelResult],
                           metrics: List[str] = None,
                           output_file: str = None) -> str:
    """
    Convenience function to create comparison table
    
    Args:
        results: Dictionary of model results
        metrics: List of metrics to include
        output_file: File to save table (optional)
        
    Returns:
        Formatted table string
    """
    comparator = ModelComparator()
    comparator.add_results(list(results.values()))
    return comparator.generate_comparison_table(metrics, output_file)


if __name__ == "__main__":
    # Test model comparison
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    import time
    
    print("Testing model comparison...")
    
    # Generate sample data
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=3,
                               n_informative=15, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train multiple models
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'SVM': SVC(kernel='rbf', probability=True, random_state=42)
    }
    
    comparator = ModelComparator()
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        start_time = time.time()
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        if hasattr(model, 'predict_proba'):
            y_prob = model.predict_proba(X_test)
        else:
            y_prob = None
        
        training_time = time.time() - start_time
        
        # Calculate metrics
        from evaluation.classification_metrics import evaluate_classification
        metrics = evaluate_classification(y_test, y_pred, y_prob)
        
        # Add result
        result = ModelResult(
            model_name=name,
            model_type=name,
            task_type='classification',
            metrics=metrics,
            predictions=y_pred,
            probabilities=y_prob,
            training_time=training_time
        )
        
        comparator.add_result(result)
    
    # Compare models
    print("\n" + "="*80)
    print("MODEL COMPARISON")
    print("="*80)
    
    comparison = comparator.compare('accuracy')
    print("\nComparison by Accuracy:")
    print(comparison.to_string(index=False))
    
    # Compare multiple metrics
    print("\n\nComparison by Multiple Metrics:")
    multi_comparison = comparator.compare_multiple_metrics()
    print(multi_comparison.to_string(index=False))
    
    # Get best model
    best = comparator.get_best_model('accuracy')
    print(f"\n\nBest Model: {best.model_name}")
    print(f"Accuracy: {best.metrics['accuracy']:.4f}")
    print(f"F1-Score: {best.metrics['f1_score']:.4f}")
    
    # Get ranking
    print("\n\nModel Ranking:")
    ranking = comparator.get_ranking('accuracy')
    for i, (model_name, score) in enumerate(ranking, 1):
        print(f"{i}. {model_name:.<40} {score:.4f}")
    
    # Save results
    comparator.save_results('results/model_comparison.json')
    
    # Generate table
    table = comparator.generate_comparison_table(
        metrics=['accuracy', 'precision', 'recall', 'f1_score'],
        output_file='results/comparison_table.csv'
    )
    print(f"\n\nComparison Table:")
    print(table)