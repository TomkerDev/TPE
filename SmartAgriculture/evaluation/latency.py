"""
Latency Testing Module

This module provides tools for measuring and analyzing system latency.
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
class LatencyMeasurement:
    """Single latency measurement"""
    operation_id: int
    start_time: float
    end_time: float
    latency_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class LatencyTestResult:
    """Container for latency test results"""
    test_name: str
    total_operations: int
    avg_latency: float
    min_latency: float
    max_latency: float
    median_latency: float
    std_latency: float
    p95_latency: float
    p99_latency: float
    success_rate: float
    errors: int
    measurements: List[LatencyMeasurement] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class LatencyTester:
    """Test and measure system latency"""
    
    def __init__(self):
        """Initialize latency tester"""
        self.results: List[LatencyTestResult] = []
        
    def measure_latency(self, operation_func: Callable,
                       operation_id: int = 0) -> LatencyMeasurement:
        """
        Measure latency of a single operation
        
        Args:
            operation_func: Function to measure
            operation_id: Operation identifier
            
        Returns:
            Latency measurement
        """
        try:
            start_time = time.perf_counter()
            operation_func()
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            
            measurement = LatencyMeasurement(
                operation_id=operation_id,
                start_time=start_time,
                end_time=end_time,
                latency_ms=latency_ms
            )
            
            return measurement
            
        except Exception as e:
            logger.error(f"Latency measurement failed: {e}")
            return LatencyMeasurement(
                operation_id=operation_id,
                start_time=0,
                end_time=0,
                latency_ms=-1
            )
    
    def test_latency(self, operation_func: Callable,
                    num_operations: int = 1000,
                    warmup: int = 100,
                    test_name: str = "latency_test") -> LatencyTestResult:
        """
        Test latency with multiple operations
        
        Args:
            operation_func: Function to test
            num_operations: Number of operations
            warmup: Number of warmup operations
            test_name: Test name
            
        Returns:
            Latency test results
        """
        try:
            logger.info(f"Testing latency: {num_operations} operations (warmup: {warmup})")
            
            measurements = []
            errors = 0
            
            # Warmup
            logger.info(f"Warmup: {warmup} operations")
            for i in range(warmup):
                try:
                    self.measure_latency(operation_func, i)
                except:
                    pass
            
            # Actual test
            for i in range(num_operations):
                measurement = self.measure_latency(operation_func, i)
                
                if measurement.latency_ms >= 0:
                    measurements.append(measurement)
                else:
                    errors += 1
            
            # Calculate statistics
            latencies = [m.latency_ms for m in measurements]
            
            if not latencies:
                logger.warning("No successful measurements")
                return LatencyTestResult(
                    test_name=test_name,
                    total_operations=num_operations,
                    avg_latency=0,
                    min_latency=0,
                    max_latency=0,
                    median_latency=0,
                    std_latency=0,
                    p95_latency=0,
                    p99_latency=0,
                    success_rate=0,
                    errors=num_operations
                )
            
            avg_latency = float(np.mean(latencies))
            min_latency = float(np.min(latencies))
            max_latency = float(np.max(latencies))
            median_latency = float(np.median(latencies))
            std_latency = float(np.std(latencies))
            p95_latency = float(np.percentile(latencies, 95))
            p99_latency = float(np.percentile(latencies, 99))
            success_rate = (num_operations - errors) / num_operations * 100
            
            result = LatencyTestResult(
                test_name=test_name,
                total_operations=num_operations,
                avg_latency=avg_latency,
                min_latency=min_latency,
                max_latency=max_latency,
                median_latency=median_latency,
                std_latency=std_latency,
                p95_latency=p95_latency,
                p99_latency=p99_latency,
                success_rate=success_rate,
                errors=errors,
                measurements=measurements
            )
            
            self.results.append(result)
            
            logger.info(f"✓ Latency test complete:")
            logger.info(f"  Avg: {avg_latency:.2f} ms")
            logger.info(f"  Median: {median_latency:.2f} ms")
            logger.info(f"  P95: {p95_latency:.2f} ms")
            logger.info(f"  P99: {p99_latency:.2f} ms")
            logger.info(f"  Min: {min_latency:.2f} ms")
            logger.info(f"  Max: {max_latency:.2f} ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Latency test failed: {e}")
            raise
    
    def test_latency_under_load(self, operation_func: Callable,
                               load_levels: List[int] = None,
                               operations_per_level: int = 100) -> pd.DataFrame:
        """
        Test latency under different load levels
        
        Args:
            operation_func: Function to test
            load_levels: List of concurrent operation counts
            operations_per_level: Operations per load level
            
        Returns:
            DataFrame with results
        """
        try:
            if load_levels is None:
                load_levels = [1, 5, 10, 25, 50, 100]
            
            logger.info(f"Testing latency under load: {load_levels}")
            
            import threading
            import queue
            
            results = []
            
            for concurrent_ops in load_levels:
                logger.info(f"Testing with {concurrent_ops} concurrent operations")
                
                result_queue = queue.Queue()
                
                def single_operation(op_id: int):
                    """Single operation with latency measurement"""
                    latencies = []
                    errors = 0
                    
                    for i in range(operations_per_level // concurrent_ops):
                        measurement = self.measure_latency(operation_func, op_id)
                        
                        if measurement.latency_ms >= 0:
                            latencies.append(measurement.latency_ms)
                        else:
                            errors += 1
                    
                    result_queue.put({
                        'latencies': latencies,
                        'errors': errors
                    })
                
                # Start threads
                start_time = time.perf_counter()
                threads = []
                
                for op_id in range(concurrent_ops):
                    thread = threading.Thread(target=single_operation, args=(op_id,))
                    threads.append(thread)
                    thread.start()
                
                # Wait for completion
                for thread in threads:
                    thread.join()
                
                end_time = time.perf_counter()
                
                # Collect results
                all_latencies = []
                total_errors = 0
                
                while not result_queue.empty():
                    result = result_queue.get()
                    all_latencies.extend(result['latencies'])
                    total_errors += result['errors']
                
                total_operations = len(all_latencies) + total_errors
                
                if all_latencies:
                    results.append({
                        'concurrent_ops': concurrent_ops,
                        'total_operations': total_operations,
                        'total_time': end_time - start_time,
                        'avg_latency': float(np.mean(all_latencies)),
                        'median_latency': float(np.median(all_latencies)),
                        'min_latency': float(np.min(all_latencies)),
                        'max_latency': float(np.max(all_latencies)),
                        'p95_latency': float(np.percentile(all_latencies, 95)),
                        'p99_latency': float(np.percentile(all_latencies, 99)),
                        'std_latency': float(np.std(all_latencies)),
                        'success_rate': (total_operations - total_errors) / total_operations * 100,
                        'errors': total_errors
                    })
                    
                    logger.info(f"  Avg: {results[-1]['avg_latency']:.2f} ms, "
                              f"P95: {results[-1]['p95_latency']:.2f} ms")
            
            df = pd.DataFrame(results)
            
            logger.info("✓ Latency under load testing complete")
            
            return df
            
        except Exception as e:
            logger.error(f"Latency under load test failed: {e}")
            raise
    
    def analyze_latency_distribution(self, result: LatencyTestResult) -> Dict[str, Any]:
        """
        Analyze latency distribution
        
        Args:
            result: Latency test result
            
        Returns:
            Analysis results
        """
        try:
            latencies = [m.latency_ms for m in result.measurements]
            
            if not latencies:
                return {}
            
            analysis = {
                'statistics': {
                    'count': len(latencies),
                    'mean': float(np.mean(latencies)),
                    'median': float(np.median(latencies)),
                    'std': float(np.std(latencies)),
                    'min': float(np.min(latencies)),
                    'max': float(np.max(latencies))
                },
                'percentiles': {
                    'p50': float(np.percentile(latencies, 50)),
                    'p75': float(np.percentile(latencies, 75)),
                    'p90': float(np.percentile(latencies, 90)),
                    'p95': float(np.percentile(latencies, 95)),
                    'p99': float(np.percentile(latencies, 99)),
                    'p999': float(np.percentile(latencies, 99.9))
                },
                'distribution': {
                    'under_1ms': sum(1 for l in latencies if l < 1),
                    'under_10ms': sum(1 for l in latencies if l < 10),
                    'under_100ms': sum(1 for l in latencies if l < 100),
                    'over_100ms': sum(1 for l in latencies if l >= 100),
                    'over_1000ms': sum(1 for l in latencies if l >= 1000)
                },
                'coefficient_of_variation': float(np.std(latencies) / np.mean(latencies)) if np.mean(latencies) > 0 else 0
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Latency distribution analysis failed: {e}")
            return {}
    
    def get_latency_trends(self) -> pd.DataFrame:
        """Get latency trends over time"""
        try:
            if not self.results:
                return pd.DataFrame()
            
            trends = []
            
            for result in self.results:
                if result.measurements:
                    timestamps = [datetime.fromisoformat(m.timestamp) for m in result.measurements]
                    latencies = [m.latency_ms for m in result.measurements]
                    
                    for ts, lat in zip(timestamps, latencies):
                        trends.append({
                            'timestamp': ts,
                            'latency_ms': lat,
                            'test_name': result.test_name
                        })
            
            df = pd.DataFrame(trends)
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to get latency trends: {e}")
            return pd.DataFrame()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        try:
            if not self.results:
                return {}
            
            all_latencies = []
            for result in self.results:
                all_latencies.extend([m.latency_ms for m in result.measurements])
            
            if not all_latencies:
                return {}
            
            summary = {
                'total_tests': len(self.results),
                'total_measurements': len(all_latencies),
                'overall_avg': float(np.mean(all_latencies)),
                'overall_median': float(np.median(all_latencies)),
                'overall_p95': float(np.percentile(all_latencies, 95)),
                'overall_p99': float(np.percentile(all_latencies, 99)),
                'min_latency': float(np.min(all_latencies)),
                'max_latency': float(np.max(all_latencies)),
                'std_latency': float(np.std(all_latencies))
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get summary: {e}")
            return {}
    
    def export_results(self, filepath: str):
        """Export results to JSON"""
        try:
            results_data = {
                'timestamp': datetime.now().isoformat(),
                'summary': self.get_summary(),
                'detailed_results': [
                    {
                        'test_name': r.test_name,
                        'total_operations': r.total_operations,
                        'avg_latency': r.avg_latency,
                        'min_latency': r.min_latency,
                        'max_latency': r.max_latency,
                        'median_latency': r.median_latency,
                        'std_latency': r.std_latency,
                        'p95_latency': r.p95_latency,
                        'p99_latency': r.p99_latency,
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


def test_latency(operation_func: Callable,
                 num_operations: int = 1000,
                 warmup: int = 100) -> Dict[str, Any]:
    """
    Convenience function to test latency
    
    Args:
        operation_func: Function to test
        num_operations: Number of operations
        warmup: Warmup operations
        
    Returns:
        Latency test results
    """
    tester = LatencyTester()
    result = tester.test_latency(operation_func, num_operations, warmup)
    
    return {
        'test_name': result.test_name,
        'total_operations': result.total_operations,
        'avg_latency': result.avg_latency,
        'median_latency': result.median_latency,
        'min_latency': result.min_latency,
        'max_latency': result.max_latency,
        'p95_latency': result.p95_latency,
        'p99_latency': result.p99_latency,
        'std_latency': result.std_latency,
        'success_rate': result.success_rate
    }


if __name__ == "__main__":
    # Test latency
    print("Testing Latency...")
    print("="*80)
    
    # Create test operation
    def test_operation():
        """Simulate an operation with variable latency"""
        time.sleep(0.001 + np.random.uniform(0, 0.002))
        return True
    
    # Run latency test
    tester = LatencyTester()
    
    print("\n1. Basic Latency Test:")
    result = tester.test_latency(test_operation, num_operations=1000, warmup=100)
    
    print(f"\nResults:")
    print(f"  Total Operations: {result.total_operations}")
    print(f"  Avg Latency: {result.avg_latency:.2f} ms")
    print(f"  Median Latency: {result.median_latency:.2f} ms")
    print(f"  P95 Latency: {result.p95_latency:.2f} ms")
    print(f"  P99 Latency: {result.p99_latency:.2f} ms")
    print(f"  Min Latency: {result.min_latency:.2f} ms")
    print(f"  Max Latency: {result.max_latency:.2f} ms")
    print(f"  Success Rate: {result.success_rate:.2f}%")
    
    print("\n2. Latency Distribution Analysis:")
    analysis = tester.analyze_latency_distribution(result)
    print(json.dumps(analysis, indent=2))
    
    print("\n3. Latency Under Load:")
    load_results = tester.test_latency_under_load(
        test_operation,
        load_levels=[1, 5, 10, 25],
        operations_per_level=50
    )
    print(load_results.to_string(index=False))
    
    print("\n4. Summary:")
    summary = tester.get_summary()
    print(json.dumps(summary, indent=2))
    
    # Export results
    tester.export_results('results/latency_test.json')
    
    print("\n✓ Latency test complete!")