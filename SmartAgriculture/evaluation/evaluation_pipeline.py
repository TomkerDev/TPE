"""
Evaluation Pipeline Module

This module provides end-to-end evaluation pipelines for comprehensive model assessment.
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
class EvaluationConfig:
    """Configuration for evaluation pipeline"""
    task_type: str = 'classification'
    metrics: List[str] = None
    generate_plots: bool = True
    perform_statistical_tests: bool = True
    statistical_test_type: str = 'wilcoxon'
    alpha: float = 0.05
    output_dir: str = 'results'
    save_plots: bool = True
    plots_dir: str = 'plots'
    generate_report: bool = True
    report_format: str = 'markdown'


class EvaluationPipeline:
    """End-to-end evaluation pipeline"""
    
    def __init__(self, config: EvaluationConfig = None):
        """
        Initialize EvaluationPipeline
        
        Args:
            config: Evaluation configuration
        """
        self.config = config or EvaluationConfig()
        self.results: Dict[str, Any] = {}
        self.visualizations: List[str] = []
        self.statistical_tests: Dict[str, Any] = {}
        
        # Create output directories
        os.makedirs(self.config.output_dir, exist_ok=True)
        if self.config.save_plots:
            os.makedirs(self.config.plots_dir, exist_ok=True)
        
    def evaluate_model(self, model_name: str, y_true: np.ndarray, 
                      y_pred: np.ndarray, y_prob: np.ndarray = None,
                      training_time: float = 0.0,
                      metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluate a single model
        
        Args:
            model_name: Name of the model
            y_true: True labels
            y_pred: Predicted labels
            y_prob: Prediction probabilities (optional)
            training_time: Training time in seconds
            metadata: Additional metadata
            
        Returns:
            Dictionary with evaluation results
        """
        try:
            from .metrics import calculate_all_metrics
            
            # Calculate metrics
            metrics_result = calculate_all_metrics(
                y_true=y_true,
                y_pred=y_pred,
                y_prob=y_prob,
                task_type=self.config.task_type
            )
            
            # Store results
            result = {
                'model_name': model_name,
                'model_type': model_name,
                'task_type': self.config.task_type,
                'metrics': metrics_result.metrics,
                'predictions': y_pred,
                'probabilities': y_prob,
                'training_time': training_time,
                'metadata': metadata or {}
            }
            
            self.results[model_name] = result
            
            logger.info(f"✓ Evaluated {model_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to evaluate {model_name}: {e}")
            return {}
    
    def generate_visualizations(self, model_name: str, 
                               y_true: np.ndarray, 
                               y_pred: np.ndarray,
                               y_prob: np.ndarray = None) -> List[str]:
        """
        Generate visualizations for a model
        
        Args:
            model_name: Name of the model
            y_true: True labels
            y_pred: Predicted labels
            y_prob: Prediction probabilities (optional)
            
        Returns:
            List of generated visualization paths
        """
        try:
            if not self.config.generate_plots:
                return []
            
            viz_paths = []
            base_path = os.path.join(self.config.plots_dir, model_name)
            os.makedirs(base_path, exist_ok=True)
            
            # Confusion Matrix
            if self.config.task_type in ['classification', 'anomaly']:
                from .confusion_matrix_plot import plot_confusion_matrix
                
                cm_path = os.path.join(base_path, 'confusion_matrix.png')
                plot_confusion_matrix(
                    y_true, y_pred,
                    title=f"{model_name} - Confusion Matrix",
                    save_path=cm_path,
                    show=False
                )
                viz_paths.append(cm_path)
            
            # ROC Curve
            if y_prob is not None and self.config.task_type == 'classification':
                from .roc_curve_plot import plot_roc_curve
                
                roc_path = os.path.join(base_path, 'roc_curve.png')
                plot_roc_curve(
                    y_true, y_prob,
                    title=f"{model_name} - ROC Curve",
                    save_path=roc_path,
                    show=False
                )
                viz_paths.append(roc_path)
            
            # Precision-Recall Curve
            if y_prob is not None and self.config.task_type == 'classification':
                from .precision_recall_plot import plot_precision_recall_curve
                
                pr_path = os.path.join(base_path, 'precision_recall_curve.png')
                plot_precision_recall_curve(
                    y_true, y_prob,
                    title=f"{model_name} - Precision-Recall Curve",
                    save_path=pr_path,
                    show=False
                )
                viz_paths.append(pr_path)
            
            self.visualizations.extend(viz_paths)
            
            logger.info(f"✓ Generated {len(viz_paths)} visualizations for {model_name}")
            
            return viz_paths
            
        except Exception as e:
            logger.error(f"Failed to generate visualizations for {model_name}: {e}")
            return []
    
    def perform_statistical_analysis(self, predictions: Dict[str, np.ndarray],
                                    y_true: np.ndarray) -> Dict[str, Any]:
        """
        Perform statistical analysis on model predictions
        
        Args:
            predictions: Dictionary of model names to predictions
            y_true: True labels
            
        Returns:
            Dictionary with statistical test results
        """
        try:
            if not self.config.perform_statistical_tests:
                return {}
            
            from .statistical_test import statistical_comparison
            
            # Perform statistical comparison
            test_results = statistical_comparison(
                predictions=predictions,
                y_true=y_true,
                test_type=self.config.statistical_test_type,
                alpha=self.config.alpha
            )
            
            self.statistical_tests = {
                'comparison': test_results.to_dict(orient='records'),
                'test_type': self.config.statistical_test_type,
                'alpha': self.config.alpha
            }
            
            logger.info(f"✓ Performed statistical analysis with {len(test_results)} comparisons")
            
            return self.statistical_tests
            
        except Exception as e:
            logger.error(f"Failed to perform statistical analysis: {e}")
            return {}
    
    def run_full_evaluation(self, models: Dict[str, Any],
                           X_test: np.ndarray, y_test: np.ndarray,
                           training_times: Dict[str, float] = None,
                           metadata: Dict[str, Dict[str, Any]] = None) -> str:
        """
        Run complete evaluation pipeline
        
        Args:
            models: Dictionary of model names to trained models
            X_test: Test features
            y_test: Test labels
            training_times: Dictionary of model names to training times
            metadata: Dictionary of model names to metadata
            
        Returns:
            Path to evaluation report
        """
        try:
            logger.info("="*80)
            logger.info("STARTING FULL EVALUATION PIPELINE")
            logger.info("="*80)
            
            training_times = training_times or {}
            metadata = metadata or {}
            
            # Step 1: Evaluate all models
            logger.info("\nStep 1: Evaluating models...")
            predictions = {}
            probabilities = {}
            
            for model_name, model in models.items():
                # Make predictions
                y_pred = model.predict(X_test)
                predictions[model_name] = y_pred
                
                # Get probabilities if available
                y_prob = None
                if hasattr(model, 'predict_proba'):
                    try:
                        y_prob = model.predict_proba(X_test)
                        probabilities[model_name] = y_prob
                    except:
                        pass
                
                # Evaluate model
                self.evaluate_model(
                    model_name=model_name,
                    y_true=y_test,
                    y_pred=y_pred,
                    y_prob=y_prob,
                    training_time=training_times.get(model_name, 0.0),
                    metadata=metadata.get(model_name, {})
                )
                
                # Generate visualizations
                if self.config.generate_plots:
                    self.generate_visualizations(model_name, y_test, y_pred, y_prob)
            
            # Step 2: Statistical analysis
            logger.info("\nStep 2: Performing statistical analysis...")
            if len(predictions) > 1:
                self.perform_statistical_analysis(predictions, y_test)
            
            # Step 3: Generate report
            logger.info("\nStep 3: Generating evaluation report...")
            report_path = ""
            
            if self.config.generate_report:
                from .report import generate_evaluation_report
                
                report_path = generate_evaluation_report(
                    model_results=self.results,
                    task_type=self.config.task_type,
                    statistical_tests=self.statistical_tests,
                    visualizations=self.visualizations,
                    output_dir=self.config.output_dir,
                    format=self.config.report_format
                )
            
            # Step 4: Save results
            logger.info("\nStep 4: Saving results...")
            results_path = os.path.join(self.config.output_dir, 'evaluation_results.json')
            self.save_results(results_path)
            
            logger.info("\n" + "="*80)
            logger.info("EVALUATION PIPELINE COMPLETED")
            logger.info("="*80)
            logger.info(f"Models evaluated: {len(self.results)}")
            logger.info(f"Visualizations generated: {len(self.visualizations)}")
            logger.info(f"Report generated: {report_path}")
            logger.info(f"Results saved: {results_path}")
            
            return report_path
            
        except Exception as e:
            logger.error(f"Failed to run evaluation pipeline: {e}")
            return ""
    
    def save_results(self, filepath: str):
        """Save evaluation results to JSON"""
        try:
            # Convert results to serializable format
            serializable_results = {}
            for model_name, result in self.results.items():
                serializable_results[model_name] = {
                    'model_name': result['model_name'],
                    'model_type': result['model_type'],
                    'task_type': result['task_type'],
                    'metrics': result['metrics'],
                    'training_time': result['training_time'],
                    'metadata': result['metadata']
                }
            
            results_data = {
                'timestamp': datetime.now().isoformat(),
                'task_type': self.config.task_type,
                'results': serializable_results,
                'statistical_tests': self.statistical_tests,
                'visualizations': self.visualizations
            }
            
            with open(filepath, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            logger.info(f"✓ Saved results to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def load_results(self, filepath: str) -> bool:
        """Load evaluation results from JSON"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"Results file not found: {filepath}")
                return False
            
            with open(filepath, 'r') as f:
                results_data = json.load(f)
            
            self.results = results_data.get('results', {})
            self.statistical_tests = results_data.get('statistical_tests', {})
            self.visualizations = results_data.get('visualizations', [])
            
            logger.info(f"✓ Loaded results from {filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load results: {e}")
            return False
    
    def get_summary(self) -> str:
        """Get evaluation summary"""
        try:
            from .compare_models import ModelComparator, ModelResult
            
            if not self.results:
                return "No results available"
            
            # Create comparator
            comparator = ModelComparator()
            
            for model_name, result in self.results.items():
                model_result = ModelResult(
                    model_name=model_name,
                    model_type=result['model_type'],
                    task_type=result['task_type'],
                    metrics=result['metrics'],
                    training_time=result['training_time']
                )
                comparator.add_result(model_result)
            
            # Generate summary
            lines = []
            lines.append("="*80)
            lines.append("EVALUATION SUMMARY")
            lines.append("="*80)
            lines.append(f"Task Type: {self.config.task_type}")
            lines.append(f"Models Evaluated: {len(self.results)}")
            lines.append("")
            
            # Best model
            best = comparator.get_best_model()
            if best:
                lines.append(f"Best Model: {best.model_name}")
                
                # Determine best metric
                if self.config.task_type == 'classification':
                    best_metric = 'accuracy'
                elif self.config.task_type == 'regression':
                    best_metric = 'r2_score'
                else:
                    best_metric = 'f1_score'
                
                lines.append(f"Best {best_metric}: {best.metrics.get(best_metric, 0.0):.4f}")
            
            lines.append("")
            lines.append("Model Comparison:")
            lines.append("-"*80)
            
            comparison = comparator.compare_multiple_metrics()
            lines.append(comparison.to_string(index=False))
            
            lines.append("")
            lines.append("="*80)
            
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"Failed to get summary: {e}")
            return f"Error: {e}"
    
    def clear(self):
        """Clear all results"""
        self.results.clear()
        self.visualizations.clear()
        self.statistical_tests.clear()
        logger.info("✓ Cleared all evaluation results")


def run_full_evaluation(models: Dict[str, Any],
                       X_test: np.ndarray, y_test: np.ndarray,
                       task_type: str = 'classification',
                       training_times: Dict[str, float] = None,
                       output_dir: str = 'results',
                       generate_plots: bool = True,
                       generate_report: bool = True) -> str:
    """
    Convenience function to run full evaluation
    
    Args:
        models: Dictionary of model names to trained models
        X_test: Test features
        y_test: Test labels
        task_type: Type of task
        training_times: Dictionary of training times
        output_dir: Output directory
        generate_plots: Whether to generate plots
        generate_report: Whether to generate report
        
    Returns:
        Path to evaluation report
    """
    config = EvaluationConfig(
        task_type=task_type,
        generate_plots=generate_plots,
        generate_report=generate_report,
        output_dir=output_dir
    )
    
    pipeline = EvaluationPipeline(config)
    return pipeline.run_full_evaluation(models, X_test, y_test, training_times)


if __name__ == "__main__":
    # Test evaluation pipeline
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    import time
    
    print("Testing Evaluation Pipeline...")
    print("="*80)
    
    # Generate sample data
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=3,
                               n_informative=15, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train models
    print("\nTraining models...")
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42)
    }
    
    training_times = {}
    for name, model in models.items():
        start_time = time.time()
        model.fit(X_train, y_train)
        training_times[name] = time.time() - start_time
        print(f"{name} trained in {training_times[name]:.2f}s")
    
    # Configure pipeline
    config = EvaluationConfig(
        task_type='classification',
        generate_plots=True,
        generate_report=True,
        report_format='markdown',
        output_dir='results/evaluation'
    )
    
    # Run pipeline
    print("\nRunning evaluation pipeline...")
    pipeline = EvaluationPipeline(config)
    report_path = pipeline.run_full_evaluation(
        models=models,
        X_test=X_test,
        y_test=y_test,
        training_times=training_times
    )
    
    # Print summary
    print("\n" + pipeline.get_summary())
    
    print(f"\n✓ Evaluation complete!")
    print(f"  Report: {report_path}")
    print(f"  Plots: {config.plots_dir}/")
    print(f"  Results: {config.output_dir}/evaluation_results.json")