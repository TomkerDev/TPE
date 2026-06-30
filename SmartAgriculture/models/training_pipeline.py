"""
Training Pipeline for Model Training and Evaluation
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
class TrainingResult:
    """Training result container"""
    model_name: str
    model_type: str
    train_score: float
    test_score: float
    metrics: Dict[str, Any]
    training_time: float
    model_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class TrainingPipeline:
    """Pipeline for training and evaluating models"""
    
    def __init__(self, models_dir: str = 'models', results_dir: str = 'results'):
        """
        Initialize TrainingPipeline
        
        Args:
            models_dir: Directory to save models
            results_dir: Directory to save results
        """
        self.models_dir = models_dir
        self.results_dir = results_dir
        os.makedirs(models_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)
        
        self.results: List[TrainingResult] = []
        
    def train_and_evaluate(self, model, model_name: str, model_type: str,
                          X_train: np.ndarray, y_train: np.ndarray,
                          X_test: np.ndarray, y_test: np.ndarray,
                          task_type: str = 'classification',
                          **kwargs) -> TrainingResult:
        """
        Train and evaluate a model
        
        Args:
            model: Model object with train() and evaluate() methods
            model_name: Name of the model
            model_type: Type of model (e.g., 'random_forest', 'xgboost')
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            task_type: 'classification' or 'regression'
            **kwargs: Additional arguments for training
            
        Returns:
            TrainingResult object
        """
        import time
        
        start_time = time.time()
        
        try:
            logger.info(f"Training {model_name}...")
            
            # Train model
            if hasattr(model, 'train'):
                train_success = model.train(X_train, y_train, **kwargs)
            else:
                # For scikit-learn models
                model.fit(X_train, y_train)
                train_success = True
            
            if not train_success:
                logger.error(f"Failed to train {model_name}")
                return None
            
            training_time = time.time() - start_time
            
            # Evaluate model
            logger.info(f"Evaluating {model_name}...")
            
            if hasattr(model, 'evaluate'):
                metrics = model.evaluate(X_test, y_test)
            else:
                # Manual evaluation for scikit-learn models
                from sklearn.metrics import accuracy_score, r2_score
                
                y_pred = model.predict(X_test)
                
                if task_type == 'classification':
                    metrics = {
                        'accuracy': float(accuracy_score(y_test, y_pred)),
                        'f1_score': 0.0,  # Placeholder
                        'precision': 0.0,
                        'recall': 0.0
                    }
                else:
                    metrics = {
                        'r2_score': float(r2_score(y_test, y_pred)),
                        'mse': 0.0,
                        'rmse': 0.0,
                        'mae': 0.0
                    }
            
            # Determine scores
            if task_type == 'classification':
                train_score = metrics.get('accuracy', 0.0)
                test_score = metrics.get('accuracy', 0.0)
            else:
                train_score = metrics.get('r2_score', 0.0)
                test_score = metrics.get('r2_score', 0.0)
            
            # Save model
            model_path = os.path.join(self.models_dir, f'{model_name}.pkl')
            
            if hasattr(model, 'save_model'):
                model.save_model(model_path)
            else:
                import joblib
                joblib.dump(model, model_path)
            
            # Create result
            result = TrainingResult(
                model_name=model_name,
                model_type=model_type,
                train_score=train_score,
                test_score=test_score,
                metrics=metrics,
                training_time=training_time,
                model_path=model_path,
                metadata={
                    'task_type': task_type,
                    'train_samples': len(X_train),
                    'test_samples': len(X_test),
                    'n_features': X_train.shape[1] if len(X_train.shape) > 1 else 1,
                    'training_date': datetime.now().isoformat()
                }
            )
            
            self.results.append(result)
            
            logger.info(f"✓ {model_name} - Test Score: {test_score:.4f}, Time: {training_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to train and evaluate {model_name}: {e}")
            return None
    
    def compare_models(self, metric: str = 'accuracy') -> pd.DataFrame:
        """
        Compare trained models
        
        Args:
            metric: Metric to compare by
            
        Returns:
            DataFrame with model comparison
        """
        try:
            if not self.results:
                logger.warning("No results to compare")
                return pd.DataFrame()
            
            comparison_data = []
            
            for result in self.results:
                row = {
                    'model_name': result.model_name,
                    'model_type': result.model_type,
                    'train_score': result.train_score,
                    'test_score': result.test_score,
                    'training_time': result.training_time,
                    metric: result.metrics.get(metric, 0.0)
                }
                comparison_data.append(row)
            
            comparison_df = pd.DataFrame(comparison_data)
            comparison_df = comparison_df.sort_values('test_score', ascending=False)
            
            return comparison_df
            
        except Exception as e:
            logger.error(f"Failed to compare models: {e}")
            return pd.DataFrame()
    
    def get_best_model(self, metric: str = 'accuracy') -> Optional[TrainingResult]:
        """
        Get the best performing model
        
        Args:
            metric: Metric to use for ranking
            
        Returns:
            TrainingResult of best model
        """
        try:
            if not self.results:
                logger.warning("No results available")
                return None
            
            best_result = max(self.results, key=lambda x: x.metrics.get(metric, 0.0))
            
            logger.info(f"Best model: {best_result.model_name} with {metric}={best_result.metrics.get(metric, 0.0):.4f}")
            
            return best_result
            
        except Exception as e:
            logger.error(f"Failed to get best model: {e}")
            return None
    
    def save_results(self, filename: str = None) -> str:
        """
        Save all results to JSON file
        
        Args:
            filename: Custom filename (optional)
            
        Returns:
            Path where results were saved
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'training_results_{timestamp}.json'
            
            filepath = os.path.join(self.results_dir, filename)
            
            # Convert results to serializable format
            results_data = []
            for result in self.results:
                result_dict = {
                    'model_name': result.model_name,
                    'model_type': result.model_type,
                    'train_score': result.train_score,
                    'test_score': result.test_score,
                    'metrics': result.metrics,
                    'training_time': result.training_time,
                    'model_path': result.model_path,
                    'metadata': result.metadata
                }
                results_data.append(result_dict)
            
            # Save to JSON
            with open(filepath, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            logger.info(f"✓ Saved results to {filepath}")
            
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
            
            # Convert to TrainingResult objects
            self.results = []
            for result_dict in results_data:
                result = TrainingResult(
                    model_name=result_dict['model_name'],
                    model_type=result_dict['model_type'],
                    train_score=result_dict['train_score'],
                    test_score=result_dict['test_score'],
                    metrics=result_dict['metrics'],
                    training_time=result_dict['training_time'],
                    model_path=result_dict['model_path'],
                    metadata=result_dict.get('metadata', {})
                )
                self.results.append(result)
            
            logger.info(f"✓ Loaded {len(self.results)} results from {filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load results: {e}")
            return False
    
    def generate_report(self, output_file: str = None) -> str:
        """
        Generate a training report
        
        Args:
            output_file: Output file path (optional)
            
        Returns:
            Report as string
        """
        try:
            if not self.results:
                return "No training results available."
            
            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("TRAINING REPORT")
            report_lines.append("=" * 80)
            report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"Total models trained: {len(self.results)}")
            report_lines.append("")
            
            # Summary table
            report_lines.append("-" * 80)
            report_lines.append("MODEL COMPARISON")
            report_lines.append("-" * 80)
            report_lines.append(f"{'Model':<20} {'Type':<15} {'Test Score':<12} {'Train Time':<12}")
            report_lines.append("-" * 80)
            
            for result in sorted(self.results, key=lambda x: x.test_score, reverse=True):
                report_lines.append(
                    f"{result.model_name:<20} {result.model_type:<15} "
                    f"{result.test_score:<12.4f} {result.training_time:<12.2f}s"
                )
            
            report_lines.append("-" * 80)
            report_lines.append("")
            
            # Best model
            best = self.get_best_model()
            if best:
                report_lines.append("BEST MODEL")
                report_lines.append("-" * 80)
                report_lines.append(f"Name: {best.model_name}")
                report_lines.append(f"Type: {best.model_type}")
                report_lines.append(f"Test Score: {best.test_score:.4f}")
                report_lines.append(f"Training Time: {best.training_time:.2f}s")
                report_lines.append("")
                report_lines.append("Metrics:")
                for key, value in best.metrics.items():
                    if isinstance(value, (int, float)):
                        report_lines.append(f"  {key}: {value:.4f}")
                report_lines.append("")
            
            # Detailed results
            report_lines.append("DETAILED RESULTS")
            report_lines.append("-" * 80)
            
            for result in self.results:
                report_lines.append(f"\n{result.model_name}:")
                report_lines.append(f"  Type: {result.model_type}")
                report_lines.append(f"  Train Score: {result.train_score:.4f}")
                report_lines.append(f"  Test Score: {result.test_score:.4f}")
                report_lines.append(f"  Training Time: {result.training_time:.2f}s")
                report_lines.append(f"  Model Path: {result.model_path}")
            
            report_lines.append("")
            report_lines.append("=" * 80)
            
            report = "\n".join(report_lines)
            
            # Save to file if specified
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(report)
                logger.info(f"✓ Saved report to {output_file}")
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return f"Error generating report: {e}"
    
    def clear_results(self):
        """Clear all results"""
        self.results = []
        logger.info("✓ Cleared all results")


def train_multiple_models(X_train: np.ndarray, y_train: np.ndarray,
                         X_test: np.ndarray, y_test: np.ndarray,
                         models_config: List[Dict[str, Any]],
                         task_type: str = 'classification',
                         models_dir: str = 'models') -> TrainingPipeline:
    """
    Train multiple models and compare them
    
    Args:
        X_train: Training features
        y_train: Training target
        X_test: Test features
        y_test: Test target
        models_config: List of model configurations
        task_type: 'classification' or 'regression'
        models_dir: Directory to save models
        
    Returns:
        TrainingPipeline with results
    """
    pipeline = TrainingPipeline(models_dir=models_dir)
    
    for config in models_config:
        model_class = config['class']
        model_name = config['name']
        model_type = config.get('type', model_name)
        params = config.get('params', {})
        
        try:
            # Initialize model
            model = model_class(**params)
            
            # Build model if method exists
            if hasattr(model, 'build_model'):
                model.build_model()
            
            # Train and evaluate
            pipeline.train_and_evaluate(
                model=model,
                model_name=model_name,
                model_type=model_type,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
                task_type=task_type
            )
            
        except Exception as e:
            logger.error(f"Failed to train {model_name}: {e}")
    
    return pipeline


if __name__ == "__main__":
    from analytics.load_data import load_sample_data
    from models.preprocessing import preprocess_data
    from models.train_test_split import split_data
    from sklearn.model_selection import train_test_split
    
    print("Loading data...")
    df = load_sample_data()
    
    X = df.drop(['sensor_type', 'sensor_id', 'timestamp'], axis=1, errors='ignore')
    y = df['sensor_type']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train_processed, X_test_processed = preprocess_data(X_train, X_test)
    
    print(f"\nTrain shape: {X_train_processed.shape}")
    print(f"Test shape: {X_test_processed.shape}")
    
    # Define models to train
    models_config = [
        {
            'class': lambda: __import__('models.random_forest', fromlist=['RandomForestModel']).RandomForestModel(n_estimators=100),
            'name': 'random_forest',
            'type': 'Random Forest'
        },
        {
            'class': lambda: __import__('models.decision_tree', fromlist=['DecisionTreeModel']).DecisionTreeModel(max_depth=10),
            'name': 'decision_tree',
            'type': 'Decision Tree'
        },
        {
            'class': lambda: __import__('models.xgboost_model', fromlist=['XGBoostModel']).XGBoostModel(n_estimators=100),
            'name': 'xgboost',
            'type': 'XGBoost'
        }
    ]
    
    print("\nTraining multiple models...")
    pipeline = train_multiple_models(
        X_train_processed, y_train,
        X_test_processed, y_test,
        models_config,
        task_type='classification'
    )
    
    print("\n" + pipeline.generate_report())
    
    # Save results
    pipeline.save_results()
    
    # Get best model
    best = pipeline.get_best_model()
    if best:
        print(f"\nBest model: {best.model_name}")