"""
Model Benchmarking Module

This module provides tools for benchmarking ML model performance.
"""
import time
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import psutil
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ModelBenchmarkResult:
    """Container for model benchmark results"""
    model_name: str
    model_type: str
    operation: str  # 'training' or 'prediction'
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_time: float
    throughput: float  # operations per second
    memory_used: float  # MB
    cpu_percent: float
    accuracy: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ModelBenchmark:
    """Benchmark ML model performance"""
    
    def __init__(self):
        """Initialize model benchmark"""
        self.results: List[ModelBenchmarkResult] = []
        
    def benchmark_training(self, model, X_train, y_train,
                          model_name: str = "unknown",
                          model_type: str = "unknown",
                          iterations: int = 1) -> ModelBenchmarkResult:
        """
        Benchmark model training time
        
        Args:
            model: ML model to benchmark
            X_train: Training features
            y_train: Training labels
            model_name: Name of the model
            model_type: Type of model
            iterations: Number of training iterations
            
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"Benchmarking training for {model_name}: {iterations} iterations")
            
            times = []
            memory_usage = []
            cpu_usage = []
            
            for i in range(iterations):
                # Get initial resource usage
                process = psutil.Process(os.getpid())
                mem_before = process.memory_info().rss / 1024 / 1024  # MB
                cpu_before = psutil.cpu_percent()
                
                # Train model
                start = time.perf_counter()
                model.fit(X_train, y_train)
                end = time.perf_counter()
                
                # Get final resource usage
                mem_after = process.memory_info().rss / 1024 / 1024  # MB
                cpu_after = psutil.cpu_percent()
                
                elapsed = end - start
                times.append(elapsed)
                memory_usage.append(mem_after - mem_before)
                cpu_usage.append(cpu_after)
                
                logger.info(f"  Iteration {i+1}/{iterations}: {elapsed:.3f}s")
            
            result = ModelBenchmarkResult(
                model_name=model_name,
                model_type=model_type,
                operation='training',
                total_time=float(np.sum(times)),
                avg_time=float(np.mean(times)),
                min_time=float(np.min(times)),
                max_time=float(np.max(times)),
                std_time=float(np.std(times)),
                throughput=iterations / np.sum(times) if np.sum(times) > 0 else 0,
                memory_used=float(np.mean(memory_usage)),
                cpu_percent=float(np.mean(cpu_usage))
            )
            
            self.results.append(result)
            
            logger.info(f"✓ Training benchmark complete:")
            logger.info(f"  Avg Time: {result.avg_time:.3f}s")
            logger.info(f"  Memory: {result.memory_used:.2f} MB")
            logger.info(f"  CPU: {result.cpu_percent:.1f}%")
            
            return result
            
        except Exception as e:
            logger.error(f"Training benchmark failed: {e}")
            raise
    
    def benchmark_prediction(self, model, X_test,
                            model_name: str = "unknown",
                            model_type: str = "unknown",
                            iterations: int = 100) -> ModelBenchmarkResult:
        """
        Benchmark model prediction time
        
        Args:
            model: ML model to benchmark
            X_test: Test features
            model_name: Name of the model
            model_type: Type of model
            iterations: Number of prediction iterations
            
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"Benchmarking prediction for {model_name}: {iterations} iterations")
            
            times = []
            memory_usage = []
            cpu_usage = []
            
            for i in range(iterations):
                # Get initial resource usage
                process = psutil.Process(os.getpid())
                mem_before = process.memory_info().rss / 1024 / 1024  # MB
                cpu_before = psutil.cpu_percent()
                
                # Make prediction
                start = time.perf_counter()
                model.predict(X_test)
                end = time.perf_counter()
                
                # Get final resource usage
                mem_after = process.memory_info().rss / 1024 / 1024  # MB
                cpu_after = psutil.cpu_percent()
                
                elapsed = end - start
                times.append(elapsed)
                memory_usage.append(mem_after - mem_before)
                cpu_usage.append(cpu_after)
            
            result = ModelBenchmarkResult(
                model_name=model_name,
                model_type=model_type,
                operation='prediction',
                total_time=float(np.sum(times)),
                avg_time=float(np.mean(times)),
                min_time=float(np.min(times)),
                max_time=float(np.max(times)),
                std_time=float(np.std(times)),
                throughput=iterations / np.sum(times) if np.sum(times) > 0 else 0,
                memory_used=float(np.mean(memory_usage)),
                cpu_percent=float(np.mean(cpu_usage))
            )
            
            self.results.append(result)
            
            logger.info(f"✓ Prediction benchmark complete:")
            logger.info(f"  Avg Time: {result.avg_time:.3f}s")
            logger.info(f"  Throughput: {result.throughput:.2f} predictions/s")
            logger.info(f"  Memory: {result.memory_used:.2f} MB")
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction benchmark failed: {e}")
            raise
    
    def benchmark_model_comparison(self, models: Dict[str, Any],
                                  X_train, y_train, X_test,
                                  model_types: Dict[str, str] = None) -> pd.DataFrame:
        """
        Benchmark multiple models for comparison
        
        Args:
            models: Dictionary of model names to model objects
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            model_types: Dictionary of model names to model types
            
        Returns:
            Comparison DataFrame
        """
        try:
            logger.info(f"Benchmarking {len(models)} models")
            
            comparison_data = []
            
            for model_name, model in models.items():
                model_type = model_types.get(model_name, "unknown") if model_types else "unknown"
                
                # Benchmark training
                train_result = self.benchmark_training(
                    model, X_train, y_train,
                    model_name=model_name,
                    model_type=model_type,
                    iterations=1
                )
                
                # Benchmark prediction
                pred_result = self.benchmark_prediction(
                    model, X_test,
                    model_name=model_name,
                    model_type=model_type,
                    iterations=100
                )
                
                # Calculate accuracy if possible
                accuracy = None
                if hasattr(model, 'score'):
                    try:
                        accuracy = model.score(X_test, y_test)
                    except:
                        pass
                
                comparison_data.append({
                    'Model': model_name,
                    'Type': model_type,
                    'Training Time (s)': train_result.avg_time,
                    'Prediction Time (s)': pred_result.avg_time,
                    'Prediction Throughput (pred/s)': pred_result.throughput,
                    'Memory (MB)': pred_result.memory_used,
                    'CPU (%)': pred_result.cpu_percent,
                    'Accuracy': accuracy
                })
            
            df = pd.DataFrame(comparison_data)
            
            logger.info("✓ Model comparison benchmark complete")
            
            return df
            
        except Exception as e:
            logger.error(f"Model comparison benchmark failed: {e}")
            return pd.DataFrame()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get benchmark summary"""
        try:
            if not self.results:
                return {}
            
            summary = {
                'total_benchmarks': len(self.results),
                'by_model': {},
                'by_operation': {}
            }
            
            for result in self.results:
                # By model
                if result.model_name not in summary['by_model']:
                    summary['by_model'][result.model_name] = {
                        'count': 0,
                        'avg_time': [],
                        'memory': [],
                        'cpu': []
                    }
                
                summary['by_model'][result.model_name]['count'] += 1
                summary['by_model'][result.model_name]['avg_time'].append(result.avg_time)
                summary['by_model'][result.model_name]['memory'].append(result.memory_used)
                summary['by_model'][result.model_name]['cpu'].append(result.cpu_percent)
                
                # By operation
                if result.operation not in summary['by_operation']:
                    summary['by_operation'][result.operation] = {
                        'count': 0,
                        'avg_time': [],
                        'throughput': []
                    }
                
                summary['by_operation'][result.operation]['count'] += 1
                summary['by_operation'][result.operation]['avg_time'].append(result.avg_time)
                summary['by_operation'][result.operation]['throughput'].append(result.throughput)
            
            # Calculate averages
            for model_name, data in summary['by_model'].items():
                data['avg_time'] = float(np.mean(data['avg_time']))
                data['memory'] = float(np.mean(data['memory']))
                data['cpu'] = float(np.mean(data['cpu']))
            
            for op_name, data in summary['by_operation'].items():
                data['avg_time'] = float(np.mean(data['avg_time']))
                data['throughput'] = float(np.mean(data['throughput']))
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get summary: {e}")
            return {}
    
    def export_results(self, filepath: str):
        """Export benchmark results to JSON"""
        try:
            results_data = {
                'timestamp': datetime.now().isoformat(),
                'summary': self.get_summary(),
                'detailed_results': [
                    {
                        'model_name': r.model_name,
                        'model_type': r.model_type,
                        'operation': r.operation,
                        'total_time': r.total_time,
                        'avg_time': r.avg_time,
                        'min_time': r.min_time,
                        'max_time': r.max_time,
                        'std_time': r.std_time,
                        'throughput': r.throughput,
                        'memory_used': r.memory_used,
                        'cpu_percent': r.cpu_percent,
                        'accuracy': r.accuracy,
                        'timestamp': r.timestamp
                    }
                    for r in self.results
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            logger.info(f"✓ Exported results to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export results: {e}")


def benchmark_model(model, X_train, y_train, X_test,
                   model_name: str = "unknown",
                   iterations: int = 10) -> Dict[str, Any]:
    """
    Convenience function to benchmark a model
    
    Args:
        model: ML model to benchmark
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        model_name: Name of the model
        iterations: Number of iterations
        
    Returns:
        Benchmark results dictionary
    """
    benchmark = ModelBenchmark()
    
    train_result = benchmark.benchmark_training(
        model, X_train, y_train,
        model_name=model_name,
        iterations=iterations
    )
    
    pred_result = benchmark.benchmark_prediction(
        model, X_test,
        model_name=model_name,
        iterations=100
    )
    
    return {
        'model_name': model_name,
        'training_time': train_result.avg_time,
        'prediction_time': pred_result.avg_time,
        'prediction_throughput': pred_result.throughput,
        'memory_used': pred_result.memory_used,
        'cpu_percent': pred_result.cpu_percent
    }


if __name__ == "__main__":
    # Test model benchmark
    print("Testing Model Benchmark...")
    print("="*80)
    
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.svm import SVC
    from sklearn.neighbors import KNeighborsClassifier
    
    # Create sample data
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create models
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(kernel='rbf', random_state=42),
        'KNN': KNeighborsClassifier(n_neighbors=5)
    }
    
    model_types = {
        'Random Forest': 'ensemble',
        'SVM': 'svm',
        'KNN': 'instance_based'
    }
    
    # Run benchmark
    benchmark = ModelBenchmark()
    
    print("\n1. Individual Model Benchmarks:")
    for model_name, model in models.items():
        print(f"\nBenchmarking {model_name}...")
        result = benchmark.benchmark_training(
            model, X_train, y_train,
            model_name=model_name,
            model_type=model_types[model_name],
            iterations=1
        )
        
        pred_result = benchmark.benchmark_prediction(
            model, X_test,
            model_name=model_name,
            iterations=50
        )
        
        print(f"  Training: {result.avg_time:.3f}s")
        print(f"  Prediction: {pred_result.avg_time:.4f}s")
    
    print("\n2. Model Comparison:")
    comparison = benchmark.benchmark_model_comparison(
        models, X_train, y_train, X_test, model_types
    )
    print(comparison.to_string(index=False))
    
    print("\n3. Summary:")
    summary = benchmark.get_summary()
    print(json.dumps(summary, indent=2))
    
    # Export results
    benchmark.export_results('results/model_benchmark.json')
    
    print("\n✓ Model benchmark test complete!")