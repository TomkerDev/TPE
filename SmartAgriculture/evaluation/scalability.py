"""
Scalability Testing Module

This module provides tools for testing system scalability with increasing loads.
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
class ScalabilityTestResult:
    """Container for scalability test results"""
    test_name: str
    load_size: int
    throughput: float
    avg_latency: float
    min_latency: float
    max_latency: float
    std_latency: float
    success_rate: float
    errors: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ScalabilityTester:
    """Test system scalability with increasing loads"""
    
    def __init__(self):
        """Initialize scalability tester"""
        self.results: List[ScalabilityTestResult] = []
        
    def test_scalability(self, operation_func: Callable,
                        load_sizes: List[int] = None,
                        operations_per_load: int = 100) -> pd.DataFrame:
        """
        Test scalability with increasing loads
        
        Args:
            operation_func: Function to test
            load_sizes: List of load sizes to test
            operations_per_load: Number of operations per load size
            
        Returns:
            DataFrame with scalability results
        """
        try:
            if load_sizes is None:
                load_sizes = [100, 500, 1000, 5000, 10000, 50000, 100000]
            
            logger.info(f"Testing scalability with loads: {load_sizes}")
            
            results = []
            
            for load_size in load_sizes:
                logger.info(f"Testing with load size: {load_size}")
                
                # Warmup
                for i in range(min(10, load_size // 10)):
                    try:
                        operation_func(i)
                    except:
                        pass
                
                # Actual test
                latencies = []
                errors = 0
                start_time = time.perf_counter()
                
                for i in range(operations_per_load):
                    try:
                        msg_start = time.perf_counter()
                        operation_func(i % load_size)
                        msg_end = time.perf_counter()
                        
                        latency_ms = (msg_end - msg_start) * 1000
                        latencies.append(latency_ms)
                        
                    except Exception as e:
                        errors += 1
                        logger.error(f"Error at load {load_size}, operation {i}: {e}")
                
                end_time = time.perf_counter()
                total_time = end_time - start_time
                
                # Calculate metrics
                throughput = operations_per_load / total_time if total_time > 0 else 0
                avg_latency = np.mean(latencies) if latencies else 0
                min_latency = np.min(latencies) if latencies else 0
                max_latency = np.max(latencies) if latencies else 0
                std_latency = np.std(latencies) if latencies else 0
                success_rate = (operations_per_load - errors) / operations_per_load * 100
                
                result = ScalabilityTestResult(
                    test_name="scalability_test",
                    load_size=load_size,
                    throughput=throughput,
                    avg_latency=avg_latency,
                    min_latency=min_latency,
                    max_latency=max_latency,
                    std_latency=std_latency,
                    success_rate=success_rate,
                    errors=errors
                )
                
                self.results.append(result)
                
                results.append({
                    'load_size': load_size,
                    'throughput': throughput,
                    'avg_latency': avg_latency,
                    'min_latency': min_latency,
                    'max_latency': max_latency,
                    'std_latency': std_latency,
                    'success_rate': success_rate,
                    'errors': errors
                })
                
                logger.info(f"  Throughput: {throughput:.2f} ops/s")
                logger.info(f"  Avg Latency: {avg_latency:.2f} ms")
                logger.info(f"  Success Rate: {success_rate:.2f}%")
            
            df = pd.DataFrame(results)
            
            logger.info("✓ Scalability testing complete")
            
            return df
            
        except Exception as e:
            logger.error(f"Scalability test failed: {e}")
            raise
    
    def test_concurrent_users(self, operation_func: Callable,
                             user_counts: List[int] = None,
                             operations_per_user: int = 50) -> pd.DataFrame:
        """
        Test scalability with concurrent users
        
        Args:
            operation_func: Function to test
            user_counts: List of user counts to test
            operations_per_user: Operations per user
            
        Returns:
            DataFrame with results
        """
        try:
            if user_counts is None:
                user_counts = [1, 5, 10, 25, 50, 100]
            
            logger.info(f"Testing concurrent users: {user_counts}")
            
            import threading
            import queue
            
            results = []
            
            for num_users in user_counts:
                logger.info(f"Testing with {num_users} concurrent users")
                
                result_queue = queue.Queue()
                
                def user_simulation(user_id: int):
                    """Simulate a user"""
                    user_latencies = []
                    user_errors = 0
                    
                    for i in range(operations_per_user):
                        try:
                            start = time.perf_counter()
                            operation_func(i)
                            end = time.perf_counter()
                            
                            latency_ms = (end - start) * 1000
                            user_latencies.append(latency_ms)
                            
                        except Exception as e:
                            user_errors += 1
                    
                    result_queue.put({
                        'user_id': user_id,
                        'latencies': user_latencies,
                        'errors': user_errors
                    })
                
                # Start threads
                start_time = time.perf_counter()
                threads = []
                
                for user_id in range(num_users):
                    thread = threading.Thread(target=user_simulation, args=(user_id,))
                    threads.append(thread)
                    thread.start()
                
                # Wait for all threads
                for thread in threads:
                    thread.join()
                
                end_time = time.perf_counter()
                total_time = end_time - start_time
                
                # Collect results
                all_latencies = []
                total_errors = 0
                
                while not result_queue.empty():
                    result = result_queue.get()
                    all_latencies.extend(result['latencies'])
                    total_errors += result['errors']
                
                total_operations = num_users * operations_per_user
                
                # Calculate metrics
                throughput = total_operations / total_time if total_time > 0 else 0
                avg_latency = np.mean(all_latencies) if all_latencies else 0
                min_latency = np.min(all_latencies) if all_latencies else 0
                max_latency = np.max(all_latencies) if all_latencies else 0
                std_latency = np.std(all_latencies) if all_latencies else 0
                success_rate = (total_operations - total_errors) / total_operations * 100
                
                results.append({
                    'num_users': num_users,
                    'total_operations': total_operations,
                    'total_time': total_time,
                    'throughput': throughput,
                    'avg_latency': avg_latency,
                    'min_latency': min_latency,
                    'max_latency': max_latency,
                    'std_latency': std_latency,
                    'success_rate': success_rate,
                    'errors': total_errors
                })
                
                logger.info(f"  Throughput: {throughput:.2f} ops/s")
                logger.info(f"  Avg Latency: {avg_latency:.2f} ms")
                logger.info(f"  Success Rate: {success_rate:.2f}%")
            
            df = pd.DataFrame(results)
            
            logger.info("✓ Concurrent user testing complete")
            
            return df
            
        except Exception as e:
            logger.error(f"Concurrent user test failed: {e}")
            raise
    
    def test_data_volume_scalability(self, process_func: Callable,
                                    data_sizes: List[int] = None) -> pd.DataFrame:
        """
        Test scalability with increasing data volumes
        
        Args:
            process_func: Function that processes data
            data_sizes: List of data sizes to test
            
        Returns:
            DataFrame with results
        """
        try:
            if data_sizes is None:
                data_sizes = [100, 1000, 10000, 100000, 500000, 1000000]
            
            logger.info(f"Testing data volume scalability: {data_sizes}")
            
            results = []
            
            for size in data_sizes:
                logger.info(f"Testing with data size: {size}")
                
                # Generate test data
                test_data = list(range(size))
                
                # Measure processing time
                start_time = time.perf_counter()
                process_func(test_data)
                end_time = time.perf_counter()
                
                elapsed = end_time - start_time
                throughput = size / elapsed if elapsed > 0 else 0
                
                results.append({
                    'data_size': size,
                    'processing_time': elapsed,
                    'throughput': throughput,
                    'records_per_second': throughput
                })
                
                logger.info(f"  Time: {elapsed:.3f}s")
                logger.info(f"  Throughput: {throughput:.2f} records/s")
            
            df = pd.DataFrame(results)
            
            logger.info("✓ Data volume scalability testing complete")
            
            return df
            
        except Exception as e:
            logger.error(f"Data volume scalability test failed: {e}")
            raise
    
    def get_scalability_metrics(self) -> Dict[str, Any]:
        """Calculate scalability metrics"""
        try:
            if not self.results:
                return {}
            
            # Extract data
            load_sizes = [r.load_size for r in self.results]
            throughputs = [r.throughput for r in self.results]
            latencies = [r.avg_latency for r in self.results]
            
            # Calculate scalability metrics
            metrics = {
                'total_tests': len(self.results),
                'load_range': {
                    'min': min(load_sizes),
                    'max': max(load_sizes)
                },
                'throughput': {
                    'min': float(np.min(throughputs)),
                    'max': float(np.max(throughputs)),
                    'avg': float(np.mean(throughputs)),
                    'at_max_load': float(throughputs[-1]) if throughputs else 0
                },
                'latency': {
                    'min': float(np.min(latencies)),
                    'max': float(np.max(latencies)),
                    'avg': float(np.mean(latencies)),
                    'at_max_load': float(latencies[-1]) if latencies else 0
                },
                'scalability_factor': self._calculate_scalability_factor(load_sizes, throughputs),
                'performance_degradation': self._calculate_performance_degradation(load_sizes, latencies)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate scalability metrics: {e}")
            return {}
    
    def _calculate_scalability_factor(self, load_sizes: List[int], 
                                     throughputs: List[float]) -> float:
        """Calculate scalability factor (how well throughput scales with load)"""
        try:
            if len(load_sizes) < 2 or len(throughputs) < 2:
                return 0.0
            
            # Calculate ratio of throughput increase to load increase
            load_ratio = load_sizes[-1] / load_sizes[0]
            throughput_ratio = throughputs[-1] / throughputs[0] if throughputs[0] > 0 else 0
            
            scalability_factor = throughput_ratio / load_ratio if load_ratio > 0 else 0
            
            return float(scalability_factor)
            
        except Exception as e:
            logger.error(f"Failed to calculate scalability factor: {e}")
            return 0.0
    
    def _calculate_performance_degradation(self, load_sizes: List[int],
                                          latencies: List[float]) -> float:
        """Calculate performance degradation percentage"""
        try:
            if len(latencies) < 2 or latencies[0] == 0:
                return 0.0
            
            degradation = ((latencies[-1] - latencies[0]) / latencies[0]) * 100
            
            return float(degradation)
            
        except Exception as e:
            logger.error(f"Failed to calculate performance degradation: {e}")
            return 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        try:
            if not self.results:
                return {}
            
            summary = {
                'total_tests': len(self.results),
                'max_load_tested': max(r.load_size for r in self.results),
                'max_throughput': max(r.throughput for r in self.results),
                'min_latency': min(r.avg_latency for r in self.results),
                'max_latency': max(r.avg_latency for r in self.results),
                'avg_success_rate': float(np.mean([r.success_rate for r in self.results])),
                'total_errors': sum(r.errors for r in self.results)
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
                'scalability_metrics': self.get_scalability_metrics(),
                'detailed_results': [
                    {
                        'test_name': r.test_name,
                        'load_size': r.load_size,
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


def test_scalability(operation_func: Callable,
                    load_sizes: List[int] = None) -> pd.DataFrame:
    """
    Convenience function to test scalability
    
    Args:
        operation_func: Function to test
        load_sizes: List of load sizes
        
    Returns:
        Results DataFrame
    """
    tester = ScalabilityTester()
    return tester.test_scalability(operation_func, load_sizes)


if __name__ == "__main__":
    # Test scalability
    print("Testing Scalability...")
    print("="*80)
    
    # Create test operation
    def test_operation(operation_id: int):
        """Simulate an operation"""
        time.sleep(0.001)  # Simulate processing
        return operation_id * 2
    
    # Run scalability test
    tester = ScalabilityTester()
    
    print("\n1. Load Scalability Test:")
    load_results = tester.test_scalability(
        test_operation,
        load_sizes=[100, 500, 1000, 5000, 10000],
        operations_per_load=100
    )
    print(load_results.to_string(index=False))
    
    print("\n2. Scalability Metrics:")
    metrics = tester.get_scalability_metrics()
    print(json.dumps(metrics, indent=2))
    
    print("\n3. Summary:")
    summary = tester.get_summary()
    print(json.dumps(summary, indent=2))
    
    # Export results
    tester.export_results('results/scalability_test.json')
    
    print("\n✓ Scalability test complete!")