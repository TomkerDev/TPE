"""
Throughput Testing Module

This module provides tools for measuring and analyzing system throughput.
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
class ThroughputMeasurement:
    """Single throughput measurement"""
    measurement_id: int
    duration: float
    operations_completed: int
    throughput: float  # operations per second
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ThroughputTestResult:
    """Container for throughput test results"""
    test_name: str
    total_duration: float
    total_operations: int
    avg_throughput: float
    min_throughput: float
    max_throughput: float
    std_throughput: float
    success_rate: float
    errors: int
    measurements: List[ThroughputMeasurement] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ThroughputTester:
    """Test and measure system throughput"""
    
    def __init__(self):
        """Initialize throughput tester"""
        self.results: List[ThroughputTestResult] = []
        
    def measure_throughput(self, operation_func: Callable,
                          duration: float = 1.0,
                          measurement_id: int = 0) -> ThroughputMeasurement:
        """
        Measure throughput over a fixed duration
        
        Args:
            operation_func: Function to measure
            duration: Measurement duration in seconds
            measurement_id: Measurement identifier
            
        Returns:
            Throughput measurement
        """
        try:
            operations = 0
            start_time = time.perf_counter()
            end_time = start_time + duration
            
            while time.perf_counter() < end_time:
                try:
                    operation_func()
                    operations += 1
                except:
                    pass
            
            actual_duration = time.perf_counter() - start_time
            throughput = operations / actual_duration if actual_duration > 0 else 0
            
            measurement = ThroughputMeasurement(
                measurement_id=measurement_id,
                duration=actual_duration,
                operations_completed=operations,
                throughput=throughput
            )
            
            return measurement
            
        except Exception as e:
            logger.error(f"Throughput measurement failed: {e}")
            return ThroughputMeasurement(
                measurement_id=measurement_id,
                duration=0,
                operations_completed=0,
                throughput=0
            )
    
    def test_throughput(self, operation_func: Callable,
                       num_measurements: int = 10,
                       measurement_duration: float = 1.0,
                       warmup: bool = True,
                       test_name: str = "throughput_test") -> ThroughputTestResult:
        """
        Test throughput with multiple measurements
        
        Args:
            operation_func: Function to test
            num_measurements: Number of measurements
            measurement_duration: Duration per measurement
            warmup: Whether to perform warmup
            test_name: Test name
            
        Returns:
            Throughput test results
        """
        try:
            logger.info(f"Testing throughput: {num_measurements} measurements of {measurement_duration}s each")
            
            measurements = []
            errors = 0
            
            # Warmup
            if warmup:
                logger.info("Warmup: 3 measurements")
                for i in range(3):
                    self.measure_throughput(operation_func, measurement_duration, i)
            
            # Actual test
            for i in range(num_measurements):
                measurement = self.measure_throughput(operation_func, measurement_duration, i)
                measurements.append(measurement)
            
            # Calculate statistics
            throughputs = [m.throughput for m in measurements]
            total_operations = sum(m.operations_completed for m in measurements)
            total_duration = sum(m.duration for m in measurements)
            
            if not throughputs:
                logger.warning("No successful measurements")
                return ThroughputTestResult(
                    test_name=test_name,
                    total_duration=0,
                    total_operations=0,
                    avg_throughput=0,
                    min_throughput=0,
                    max_throughput=0,
                    std_throughput=0,
                    success_rate=0,
                    errors=num_measurements
                )
            
            avg_throughput = float(np.mean(throughputs))
            min_throughput = float(np.min(throughputs))
            max_throughput = float(np.max(throughputs))
            std_throughput = float(np.std(throughputs))
            success_rate = num_measurements / num_measurements * 100  # All measurements succeed
            
            result = ThroughputTestResult(
                test_name=test_name,
                total_duration=total_duration,
                total_operations=total_operations,
                avg_throughput=avg_throughput,
                min_throughput=min_throughput,
                max_throughput=max_throughput,
                std_throughput=std_throughput,
                success_rate=success_rate,
                errors=errors,
                measurements=measurements
            )
            
            self.results.append(result)
            
            logger.info(f"✓ Throughput test complete:")
            logger.info(f"  Avg Throughput: {avg_throughput:.2f} ops/s")
            logger.info(f"  Min: {min_throughput:.2f} ops/s")
            logger.info(f"  Max: {max_throughput:.2f} ops/s")
            logger.info(f"  Total Operations: {total_operations}")
            
            return result
            
        except Exception as e:
            logger.error(f"Throughput test failed: {e}")
            raise
    
    def test_throughput_over_time(self, operation_func: Callable,
                                 duration: float = 60.0,
                                 interval: float = 5.0,
                                 test_name: str = "throughput_over_time") -> pd.DataFrame:
        """
        Test throughput over an extended period
        
        Args:
            operation_func: Function to test
            duration: Total test duration in seconds
            interval: Measurement interval in seconds
            test_name: Test name
            
        Returns:
            DataFrame with throughput over time
        """
        try:
            logger.info(f"Testing throughput over time: {duration}s with {interval}s intervals")
            
            measurements = []
            start_time = time.perf_counter()
            measurement_id = 0
            
            while time.perf_counter() - start_time < duration:
                measurement = self.measure_throughput(
                    operation_func,
                    duration=interval,
                    measurement_id=measurement_id
                )
                
                measurements.append(measurement)
                measurement_id += 1
                
                logger.info(f"  Measurement {measurement_id}: {measurement.throughput:.2f} ops/s")
            
            # Create DataFrame
            data = []
            for m in measurements:
                data.append({
                    'measurement_id': m.measurement_id,
                    'timestamp': datetime.fromisoformat(m.timestamp),
                    'duration': m.duration,
                    'operations': m.operations_completed,
                    'throughput': m.throughput
                })
            
            df = pd.DataFrame(data)
            
            logger.info("✓ Throughput over time test complete")
            logger.info(f"  Avg Throughput: {df['throughput'].mean():.2f} ops/s")
            logger.info(f"  Min Throughput: {df['throughput'].min():.2f} ops/s")
            logger.info(f"  Max Throughput: {df['throughput'].max():.2f} ops/s")
            
            return df
            
        except Exception as e:
            logger.error(f"Throughput over time test failed: {e}")
            raise
    
    def test_sustained_throughput(self, operation_func: Callable,
                                 target_throughput: float,
                                 duration: float = 30.0,
                                 test_name: str = "sustained_throughput") -> Dict[str, Any]:
        """
        Test ability to sustain target throughput
        
        Args:
            operation_func: Function to test
            target_throughput: Target operations per second
            duration: Test duration in seconds
            test_name: Test name
            
        Returns:
            Test results
        """
        try:
            logger.info(f"Testing sustained throughput: {target_throughput} ops/s for {duration}s")
            
            target_interval = 1.0 / target_throughput if target_throughput > 0 else 0
            operations = 0
            errors = 0
            latencies = []
            
            start_time = time.perf_counter()
            end_time = start_time + duration
            
            while time.perf_counter() < end_time:
                op_start = time.perf_counter()
                
                try:
                    operation_func()
                    operations += 1
                except:
                    errors += 1
                
                op_end = time.perf_counter()
                latencies.append((op_end - op_start) * 1000)
                
                # Sleep to maintain target throughput
                elapsed = time.perf_counter() - op_start
                if elapsed < target_interval:
                    time.sleep(target_interval - elapsed)
            
            actual_duration = time.perf_counter() - start_time
            actual_throughput = operations / actual_duration if actual_duration > 0 else 0
            
            results = {
                'test_name': test_name,
                'target_throughput': target_throughput,
                'actual_throughput': actual_throughput,
                'duration': actual_duration,
                'total_operations': operations,
                'errors': errors,
                'success_rate': (operations - errors) / operations * 100 if operations > 0 else 0,
                'throughput_ratio': actual_throughput / target_throughput if target_throughput > 0 else 0,
                'avg_latency': float(np.mean(latencies)) if latencies else 0,
                'max_latency': float(np.max(latencies)) if latencies else 0
            }
            
            logger.info(f"✓ Sustained throughput test complete:")
            logger.info(f"  Target: {target_throughput:.2f} ops/s")
            logger.info(f"  Actual: {actual_throughput:.2f} ops/s")
            logger.info(f"  Ratio: {results['throughput_ratio']:.2f}")
            logger.info(f"  Success Rate: {results['success_rate']:.2f}%")
            
            return results
            
        except Exception as e:
            logger.error(f"Sustained throughput test failed: {e}")
            raise
    
    def compare_throughput(self, operation_funcs: Dict[str, Callable],
                          num_measurements: int = 10,
                          measurement_duration: float = 1.0) -> pd.DataFrame:
        """
        Compare throughput of different operations
        
        Args:
            operation_funcs: Dictionary of operation names to functions
            num_measurements: Number of measurements per operation
            measurement_duration: Duration per measurement
            
        Returns:
            Comparison DataFrame
        """
        try:
            logger.info(f"Comparing throughput of {len(operation_funcs)} operations")
            
            comparison_data = []
            
            for op_name, op_func in operation_funcs.items():
                logger.info(f"Testing: {op_name}")
                
                result = self.test_throughput(
                    op_func,
                    num_measurements=num_measurements,
                    measurement_duration=measurement_duration,
                    test_name=op_name
                )
                
                comparison_data.append({
                    'Operation': op_name,
                    'Avg Throughput (ops/s)': result.avg_throughput,
                    'Min Throughput (ops/s)': result.min_throughput,
                    'Max Throughput (ops/s)': result.max_throughput,
                    'Std Dev': result.std_throughput,
                    'Total Operations': result.total_operations,
                    'Success Rate (%)': result.success_rate
                })
            
            df = pd.DataFrame(comparison_data)
            
            logger.info("✓ Throughput comparison complete")
            
            return df
            
        except Exception as e:
            logger.error(f"Throughput comparison failed: {e}")
            return pd.DataFrame()
    
    def get_throughput_trends(self) -> pd.DataFrame:
        """Get throughput trends over time"""
        try:
            if not self.results:
                return pd.DataFrame()
            
            trends = []
            
            for result in self.results:
                for measurement in result.measurements:
                    trends.append({
                        'timestamp': datetime.fromisoformat(measurement.timestamp),
                        'throughput': measurement.throughput,
                        'operations': measurement.operations_completed,
                        'duration': measurement.duration,
                        'test_name': result.test_name
                    })
            
            df = pd.DataFrame(trends)
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to get throughput trends: {e}")
            return pd.DataFrame()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        try:
            if not self.results:
                return {}
            
            all_throughputs = []
            for result in self.results:
                all_throughputs.extend([m.throughput for m in result.measurements])
            
            if not all_throughputs:
                return {}
            
            summary = {
                'total_tests': len(self.results),
                'total_measurements': len(all_throughputs),
                'overall_avg_throughput': float(np.mean(all_throughputs)),
                'overall_min': float(np.min(all_throughputs)),
                'overall_max': float(np.max(all_throughputs)),
                'overall_std': float(np.std(all_throughputs)),
                'total_operations': sum(r.total_operations for r in self.results)
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
                        'total_duration': r.total_duration,
                        'total_operations': r.total_operations,
                        'avg_throughput': r.avg_throughput,
                        'min_throughput': r.min_throughput,
                        'max_throughput': r.max_throughput,
                        'std_throughput': r.std_throughput,
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


def test_throughput(operation_func: Callable,
                   num_measurements: int = 10,
                   measurement_duration: float = 1.0) -> Dict[str, Any]:
    """
    Convenience function to test throughput
    
    Args:
        operation_func: Function to test
        num_measurements: Number of measurements
        measurement_duration: Duration per measurement
        
    Returns:
        Throughput test results
    """
    tester = ThroughputTester()
    result = tester.test_throughput(operation_func, num_measurements, measurement_duration)
    
    return {
        'test_name': result.test_name,
        'avg_throughput': result.avg_throughput,
        'min_throughput': result.min_throughput,
        'max_throughput': result.max_throughput,
        'std_throughput': result.std_throughput,
        'total_operations': result.total_operations,
        'success_rate': result.success_rate
    }


if __name__ == "__main__":
    # Test throughput
    print("Testing Throughput...")
    print("="*80)
    
    # Create test operation
    def test_operation():
        """Simulate an operation"""
        time.sleep(0.001)  # Simulate processing
        return True
    
    # Run throughput test
    tester = ThroughputTester()
    
    print("\n1. Basic Throughput Test:")
    result = tester.test_throughput(
        test_operation,
        num_measurements=10,
        measurement_duration=1.0
    )
    
    print(f"\nResults:")
    print(f"  Total Operations: {result.total_operations}")
    print(f"  Avg Throughput: {result.avg_throughput:.2f} ops/s")
    print(f"  Min Throughput: {result.min_throughput:.2f} ops/s")
    print(f"  Max Throughput: {result.max_throughput:.2f} ops/s")
    print(f"  Std Dev: {result.std_throughput:.2f}")
    
    print("\n2. Throughput Over Time (30s):")
    time_df = tester.test_throughput_over_time(
        test_operation,
        duration=30.0,
        interval=5.0
    )
    print(time_df.to_string(index=False))
    
    print("\n3. Sustained Throughput Test (500 ops/s for 10s):")
    sustained = tester.test_sustained_throughput(
        test_operation,
        target_throughput=500,
        duration=10.0
    )
    print(json.dumps(sustained, indent=2))
    
    print("\n4. Summary:")
    summary = tester.get_summary()
    print(json.dumps(summary, indent=2))
    
    # Export results
    tester.export_results('results/throughput_test.json')
    
    print("\n✓ Throughput test complete!")