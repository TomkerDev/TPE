"""
Pipeline Benchmarking Module

This module provides tools for benchmarking the IoT data pipeline performance.
"""
import time
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PipelineBenchmarkResult:
    """Container for pipeline benchmark results"""
    total_messages: int
    total_time: float
    throughput: float  # messages per second
    avg_latency: float  # milliseconds
    min_latency: float
    max_latency: float
    std_latency: float
    success_rate: float
    errors: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class PipelineBenchmark:
    """Benchmark the IoT data pipeline"""
    
    def __init__(self):
        """Initialize pipeline benchmark"""
        self.results: List[PipelineBenchmarkResult] = []
        self.latencies: List[float] = []
        
    def benchmark_ingestion(self, pipeline_func: Callable, 
                           messages: int = 1000,
                           warmup: int = 100) -> PipelineBenchmarkResult:
        """
        Benchmark data ingestion pipeline
        
        Args:
            pipeline_func: Function that processes a single message
            messages: Number of messages to process
            warmup: Number of warmup messages (not counted)
            
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"Starting pipeline benchmark: {messages} messages")
            
            # Warmup
            logger.info(f"Warmup: {warmup} messages")
            for i in range(warmup):
                pipeline_func(i)
            
            # Actual benchmark
            latencies = []
            errors = 0
            start_time = time.perf_counter()
            
            for i in range(messages):
                try:
                    msg_start = time.perf_counter()
                    pipeline_func(i)
                    msg_end = time.perf_counter()
                    
                    latency_ms = (msg_end - msg_start) * 1000  # Convert to milliseconds
                    latencies.append(latency_ms)
                    
                except Exception as e:
                    errors += 1
                    logger.error(f"Error processing message {i}: {e}")
            
            end_time = time.perf_counter()
            total_time = end_time - start_time
            
            # Calculate metrics
            throughput = messages / total_time if total_time > 0 else 0
            avg_latency = np.mean(latencies) if latencies else 0
            min_latency = np.min(latencies) if latencies else 0
            max_latency = np.max(latencies) if latencies else 0
            std_latency = np.std(latencies) if latencies else 0
            success_rate = (messages - errors) / messages * 100 if messages > 0 else 0
            
            result = PipelineBenchmarkResult(
                total_messages=messages,
                total_time=total_time,
                throughput=throughput,
                avg_latency=avg_latency,
                min_latency=min_latency,
                max_latency=max_latency,
                std_latency=std_latency,
                success_rate=success_rate,
                errors=errors
            )
            
            self.results.append(result)
            self.latencies.extend(latencies)
            
            logger.info(f"✓ Benchmark complete:")
            logger.info(f"  Throughput: {throughput:.2f} msg/s")
            logger.info(f"  Avg Latency: {avg_latency:.2f} ms")
            logger.info(f"  Success Rate: {success_rate:.2f}%")
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline benchmark failed: {e}")
            raise
    
    def benchmark_etl_pipeline(self, etl_pipeline_func: Callable,
                              data_size: int = 1000,
                              iterations: int = 10) -> Dict[str, Any]:
        """
        Benchmark ETL pipeline
        
        Args:
            etl_pipeline_func: ETL pipeline function
            data_size: Size of test data
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"Benchmarking ETL pipeline: {iterations} iterations")
            
            times = []
            
            for i in range(iterations):
                start = time.perf_counter()
                etl_pipeline_func(data_size)
                end = time.perf_counter()
                
                elapsed = end - start
                times.append(elapsed)
                
                logger.info(f"  Iteration {i+1}/{iterations}: {elapsed:.3f}s")
            
            results = {
                'data_size': data_size,
                'iterations': iterations,
                'mean_time': float(np.mean(times)),
                'std_time': float(np.std(times)),
                'min_time': float(np.min(times)),
                'max_time': float(np.max(times)),
                'total_time': float(np.sum(times)),
                'throughput': data_size / np.mean(times) if np.mean(times) > 0 else 0
            }
            
            logger.info(f"✓ ETL benchmark complete:")
            logger.info(f"  Mean time: {results['mean_time']:.3f}s")
            logger.info(f"  Throughput: {results['throughput']:.2f} records/s")
            
            return results
            
        except Exception as e:
            logger.error(f"ETL benchmark failed: {e}")
            raise
    
    def benchmark_with_load(self, pipeline_func: Callable,
                           message_counts: List[int] = None) -> pd.DataFrame:
        """
        Benchmark pipeline with different message loads
        
        Args:
            pipeline_func: Pipeline function
            message_counts: List of message counts to test
            
        Returns:
            DataFrame with results
        """
        try:
            if message_counts is None:
                message_counts = [100, 500, 1000, 5000, 10000, 50000]
            
            logger.info(f"Benchmarking with varying loads: {message_counts}")
            
            results = []
            
            for count in message_counts:
                logger.info(f"Testing with {count} messages...")
                result = self.benchmark_ingestion(pipeline_func, messages=count)
                
                results.append({
                    'messages': count,
                    'total_time': result.total_time,
                    'throughput': result.throughput,
                    'avg_latency': result.avg_latency,
                    'success_rate': result.success_rate
                })
            
            df = pd.DataFrame(results)
            
            logger.info("✓ Load benchmarking complete")
            
            return df
            
        except Exception as e:
            logger.error(f"Load benchmark failed: {e}")
            raise
    
    def get_summary(self) -> Dict[str, Any]:
        """Get benchmark summary"""
        try:
            if not self.results:
                return {}
            
            throughputs = [r.throughput for r in self.results]
            latencies = [r.avg_latency for r in self.results]
            
            summary = {
                'total_benchmarks': len(self.results),
                'avg_throughput': float(np.mean(throughputs)),
                'max_throughput': float(np.max(throughputs)),
                'min_throughput': float(np.min(throughputs)),
                'avg_latency': float(np.mean(latencies)),
                'max_latency': float(np.max(latencies)),
                'min_latency': float(np.min(latencies)),
                'total_messages_processed': sum(r.total_messages for r in self.results),
                'total_errors': sum(r.errors for r in self.results),
                'avg_success_rate': float(np.mean([r.success_rate for r in self.results]))
            }
            
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
                        'total_messages': r.total_messages,
                        'total_time': r.total_time,
                        'throughput': r.throughput,
                        'avg_latency': r.avg_latency,
                        'min_latency': r.min_latency,
                        'max_latency': r.max_latency,
                        'std_latency': r.std_latency,
                        'success_rate': r.success_rate,
                        'errors': r.errors,
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


def benchmark_pipeline(pipeline_func: Callable,
                      messages: int = 1000,
                      warmup: int = 100) -> Dict[str, Any]:
    """
    Convenience function to benchmark pipeline
    
    Args:
        pipeline_func: Pipeline function
        messages: Number of messages
        warmup: Warmup messages
        
    Returns:
        Benchmark results dictionary
    """
    benchmark = PipelineBenchmark()
    result = benchmark.benchmark_ingestion(pipeline_func, messages, warmup)
    
    return {
        'total_messages': result.total_messages,
        'total_time': result.total_time,
        'throughput': result.throughput,
        'avg_latency': result.avg_latency,
        'min_latency': result.min_latency,
        'max_latency': result.max_latency,
        'std_latency': result.std_latency,
        'success_rate': result.success_rate,
        'errors': result.errors
    }


if __name__ == "__main__":
    # Test pipeline benchmark
    print("Testing Pipeline Benchmark...")
    print("="*80)
    
    # Create a simple test pipeline
    def test_pipeline(message_id: int):
        """Simulate pipeline processing"""
        time.sleep(0.001)  # Simulate processing
        return message_id * 2
    
    # Run benchmark
    benchmark = PipelineBenchmark()
    
    print("\n1. Single benchmark (1000 messages):")
    result = benchmark.benchmark_ingestion(test_pipeline, messages=1000, warmup=10)
    
    print(f"\nResults:")
    print(f"  Messages: {result.total_messages}")
    print(f"  Time: {result.total_time:.3f}s")
    print(f"  Throughput: {result.throughput:.2f} msg/s")
    print(f"  Avg Latency: {result.avg_latency:.2f} ms")
    print(f"  Success Rate: {result.success_rate:.2f}%")
    
    print("\n2. Load test:")
    load_results = benchmark.benchmark_with_load(test_pipeline)
    print(load_results.to_string(index=False))
    
    print("\n3. Summary:")
    summary = benchmark.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")
    
    # Export results
    benchmark.export_results('results/pipeline_benchmark.json')
    
    print("\n✓ Pipeline benchmark test complete!")