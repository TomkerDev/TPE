"""
Database Benchmarking Module

This module provides tools for benchmarking database performance.
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
class DatabaseBenchmarkResult:
    """Container for database benchmark results"""
    db_name: str
    operation: str
    total_operations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_time: float
    throughput: float  # operations per second
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class DatabaseBenchmark:
    """Benchmark database performance"""
    
    def __init__(self):
        """Initialize database benchmark"""
        self.results: List[DatabaseBenchmarkResult] = []
        
    def benchmark_postgresql(self, query_func: Callable, 
                            query: str,
                            iterations: int = 100) -> DatabaseBenchmarkResult:
        """
        Benchmark PostgreSQL performance
        
        Args:
            query_func: Function to execute query
            query: SQL query to execute
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"Benchmarking PostgreSQL: {iterations} iterations")
            
            times = []
            
            for i in range(iterations):
                start = time.perf_counter()
                query_func(query)
                end = time.perf_counter()
                
                elapsed = (end - start) * 1000  # Convert to milliseconds
                times.append(elapsed)
            
            result = DatabaseBenchmarkResult(
                db_name='postgresql',
                operation='query',
                total_operations=iterations,
                total_time=float(np.sum(times)),
                avg_time=float(np.mean(times)),
                min_time=float(np.min(times)),
                max_time=float(np.max(times)),
                std_time=float(np.std(times)),
                throughput=iterations / np.sum(times) * 1000 if np.sum(times) > 0 else 0
            )
            
            self.results.append(result)
            
            logger.info(f"✓ PostgreSQL benchmark complete:")
            logger.info(f"  Avg Time: {result.avg_time:.2f} ms")
            logger.info(f"  Throughput: {result.throughput:.2f} queries/s")
            
            return result
            
        except Exception as e:
            logger.error(f"PostgreSQL benchmark failed: {e}")
            raise
    
    def benchmark_timescaledb(self, query_func: Callable,
                             query: str,
                             iterations: int = 100) -> DatabaseBenchmarkResult:
        """
        Benchmark TimescaleDB performance
        
        Args:
            query_func: Function to execute query
            query: SQL query to execute
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"Benchmarking TimescaleDB: {iterations} iterations")
            
            times = []
            
            for i in range(iterations):
                start = time.perf_counter()
                query_func(query)
                end = time.perf_counter()
                
                elapsed = (end - start) * 1000
                times.append(elapsed)
            
            result = DatabaseBenchmarkResult(
                db_name='timescaledb',
                operation='query',
                total_operations=iterations,
                total_time=float(np.sum(times)),
                avg_time=float(np.mean(times)),
                min_time=float(np.min(times)),
                max_time=float(np.max(times)),
                std_time=float(np.std(times)),
                throughput=iterations / np.sum(times) * 1000 if np.sum(times) > 0 else 0
            )
            
            self.results.append(result)
            
            logger.info(f"✓ TimescaleDB benchmark complete:")
            logger.info(f"  Avg Time: {result.avg_time:.2f} ms")
            logger.info(f"  Throughput: {result.throughput:.2f} queries/s")
            
            return result
            
        except Exception as e:
            logger.error(f"TimescaleDB benchmark failed: {e}")
            raise
    
    def benchmark_mongodb(self, query_func: Callable,
                         query: dict,
                         iterations: int = 100) -> DatabaseBenchmarkResult:
        """
        Benchmark MongoDB performance
        
        Args:
            query_func: Function to execute query
            query: MongoDB query
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"Benchmarking MongoDB: {iterations} iterations")
            
            times = []
            
            for i in range(iterations):
                start = time.perf_counter()
                query_func(query)
                end = time.perf_counter()
                
                elapsed = (end - start) * 1000
                times.append(elapsed)
            
            result = DatabaseBenchmarkResult(
                db_name='mongodb',
                operation='query',
                total_operations=iterations,
                total_time=float(np.sum(times)),
                avg_time=float(np.mean(times)),
                min_time=float(np.min(times)),
                max_time=float(np.max(times)),
                std_time=float(np.std(times)),
                throughput=iterations / np.sum(times) * 1000 if np.sum(times) > 0 else 0
            )
            
            self.results.append(result)
            
            logger.info(f"✓ MongoDB benchmark complete:")
            logger.info(f"  Avg Time: {result.avg_time:.2f} ms")
            logger.info(f"  Throughput: {result.throughput:.2f} queries/s")
            
            return result
            
        except Exception as e:
            logger.error(f"MongoDB benchmark failed: {e}")
            raise
    
    def benchmark_neo4j(self, query_func: Callable,
                       query: str,
                       iterations: int = 100) -> DatabaseBenchmarkResult:
        """
        Benchmark Neo4j performance
        
        Args:
            query_func: Function to execute query
            query: Cypher query
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"Benchmarking Neo4j: {iterations} iterations")
            
            times = []
            
            for i in range(iterations):
                start = time.perf_counter()
                query_func(query)
                end = time.perf_counter()
                
                elapsed = (end - start) * 1000
                times.append(elapsed)
            
            result = DatabaseBenchmarkResult(
                db_name='neo4j',
                operation='query',
                total_operations=iterations,
                total_time=float(np.sum(times)),
                avg_time=float(np.mean(times)),
                min_time=float(np.min(times)),
                max_time=float(np.max(times)),
                std_time=float(np.std(times)),
                throughput=iterations / np.sum(times) * 1000 if np.sum(times) > 0 else 0
            )
            
            self.results.append(result)
            
            logger.info(f"✓ Neo4j benchmark complete:")
            logger.info(f"  Avg Time: {result.avg_time:.2f} ms")
            logger.info(f"  Throughput: {result.throughput:.2f} queries/s")
            
            return result
            
        except Exception as e:
            logger.error(f"Neo4j benchmark failed: {e}")
            raise
    
    def benchmark_write_performance(self, write_func: Callable,
                                   data: Any,
                                   iterations: int = 100) -> DatabaseBenchmarkResult:
        """
        Benchmark write performance
        
        Args:
            write_func: Function to write data
            data: Data to write
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"Benchmarking write performance: {iterations} iterations")
            
            times = []
            
            for i in range(iterations):
                start = time.perf_counter()
                write_func(data)
                end = time.perf_counter()
                
                elapsed = (end - start) * 1000
                times.append(elapsed)
            
            result = DatabaseBenchmarkResult(
                db_name='unknown',
                operation='write',
                total_operations=iterations,
                total_time=float(np.sum(times)),
                avg_time=float(np.mean(times)),
                min_time=float(np.min(times)),
                max_time=float(np.max(times)),
                std_time=float(np.std(times)),
                throughput=iterations / np.sum(times) * 1000 if np.sum(times) > 0 else 0
            )
            
            self.results.append(result)
            
            logger.info(f"✓ Write benchmark complete:")
            logger.info(f"  Avg Time: {result.avg_time:.2f} ms")
            logger.info(f"  Throughput: {result.throughput:.2f} writes/s")
            
            return result
            
        except Exception as e:
            logger.error(f"Write benchmark failed: {e}")
            raise
    
    def benchmark_read_performance(self, read_func: Callable,
                                  query_params: Any,
                                  iterations: int = 100) -> DatabaseBenchmarkResult:
        """
        Benchmark read performance
        
        Args:
            read_func: Function to read data
            query_params: Query parameters
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"Benchmarking read performance: {iterations} iterations")
            
            times = []
            
            for i in range(iterations):
                start = time.perf_counter()
                read_func(query_params)
                end = time.perf_counter()
                
                elapsed = (end - start) * 1000
                times.append(elapsed)
            
            result = DatabaseBenchmarkResult(
                db_name='unknown',
                operation='read',
                total_operations=iterations,
                total_time=float(np.sum(times)),
                avg_time=float(np.mean(times)),
                min_time=float(np.min(times)),
                max_time=float(np.max(times)),
                std_time=float(np.std(times)),
                throughput=iterations / np.sum(times) * 1000 if np.sum(times) > 0 else 0
            )
            
            self.results.append(result)
            
            logger.info(f"✓ Read benchmark complete:")
            logger.info(f"  Avg Time: {result.avg_time:.2f} ms")
            logger.info(f"  Throughput: {result.throughput:.2f} reads/s")
            
            return result
            
        except Exception as e:
            logger.error(f"Read benchmark failed: {e}")
            raise
    
    def compare_databases(self, db_results: Dict[str, DatabaseBenchmarkResult]) -> pd.DataFrame:
        """
        Compare database performance
        
        Args:
            db_results: Dictionary of database name to results
            
        Returns:
            Comparison DataFrame
        """
        try:
            comparison_data = []
            
            for db_name, result in db_results.items():
                comparison_data.append({
                    'Database': db_name,
                    'Operation': result.operation,
                    'Avg Time (ms)': result.avg_time,
                    'Min Time (ms)': result.min_time,
                    'Max Time (ms)': result.max_time,
                    'Throughput (ops/s)': result.throughput,
                    'Total Operations': result.total_operations
                })
            
            df = pd.DataFrame(comparison_data)
            
            logger.info("✓ Database comparison complete")
            
            return df
            
        except Exception as e:
            logger.error(f"Database comparison failed: {e}")
            return pd.DataFrame()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get benchmark summary"""
        try:
            if not self.results:
                return {}
            
            summary = {
                'total_benchmarks': len(self.results),
                'by_database': {},
                'by_operation': {}
            }
            
            for result in self.results:
                # By database
                if result.db_name not in summary['by_database']:
                    summary['by_database'][result.db_name] = {
                        'count': 0,
                        'avg_time': [],
                        'throughput': []
                    }
                
                summary['by_database'][result.db_name]['count'] += 1
                summary['by_database'][result.db_name]['avg_time'].append(result.avg_time)
                summary['by_database'][result.db_name]['throughput'].append(result.throughput)
                
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
            for db_name, data in summary['by_database'].items():
                data['avg_time'] = float(np.mean(data['avg_time']))
                data['throughput'] = float(np.mean(data['throughput']))
            
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
                        'db_name': r.db_name,
                        'operation': r.operation,
                        'total_operations': r.total_operations,
                        'total_time': r.total_time,
                        'avg_time': r.avg_time,
                        'min_time': r.min_time,
                        'max_time': r.max_time,
                        'std_time': r.std_time,
                        'throughput': r.throughput,
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


def benchmark_database(db_func: Callable,
                      operation_type: str = 'query',
                      iterations: int = 100) -> Dict[str, Any]:
    """
    Convenience function to benchmark database
    
    Args:
        db_func: Database function to benchmark
        operation_type: Type of operation ('query', 'write', 'read')
        iterations: Number of iterations
        
    Returns:
        Benchmark results dictionary
    """
    benchmark = DatabaseBenchmark()
    
    if operation_type == 'query':
        result = benchmark.benchmark_postgresql(db_func, "", iterations)
    elif operation_type == 'write':
        result = benchmark.benchmark_write_performance(db_func, None, iterations)
    elif operation_type == 'read':
        result = benchmark.benchmark_read_performance(db_func, None, iterations)
    else:
        raise ValueError(f"Unknown operation type: {operation_type}")
    
    return {
        'db_name': result.db_name,
        'operation': result.operation,
        'avg_time': result.avg_time,
        'min_time': result.min_time,
        'max_time': result.max_time,
        'throughput': result.throughput,
        'total_operations': result.total_operations
    }


if __name__ == "__main__":
    # Test database benchmark
    print("Testing Database Benchmark...")
    print("="*80)
    
    # Create test functions
    def test_query(query: str):
        """Simulate database query"""
        time.sleep(0.01)  # Simulate query time
        return [{'id': i, 'value': i * 2} for i in range(10)]
    
    def test_write(data):
        """Simulate database write"""
        time.sleep(0.005)  # Simulate write time
        return True
    
    def test_read(params):
        """Simulate database read"""
        time.sleep(0.008)  # Simulate read time
        return [{'id': i, 'value': i * 2} for i in range(10)]
    
    # Run benchmarks
    benchmark = DatabaseBenchmark()
    
    print("\n1. PostgreSQL Query Benchmark:")
    pg_result = benchmark.benchmark_postgresql(test_query, "SELECT * FROM test", iterations=50)
    
    print("\n2. MongoDB Query Benchmark:")
    mongo_result = benchmark.benchmark_mongodb(test_query, {"sensor_id": "TEMP_001"}, iterations=50)
    
    print("\n3. Write Performance Benchmark:")
    write_result = benchmark.benchmark_write_performance(test_write, {'test': 'data'}, iterations=50)
    
    print("\n4. Read Performance Benchmark:")
    read_result = benchmark.benchmark_read_performance(test_read, {'id': 1}, iterations=50)
    
    print("\n5. Database Comparison:")
    comparison = benchmark.compare_databases({
        'PostgreSQL': pg_result,
        'MongoDB': mongo_result,
        'Write': write_result,
        'Read': read_result
    })
    print(comparison.to_string(index=False))
    
    print("\n6. Summary:")
    summary = benchmark.get_summary()
    print(json.dumps(summary, indent=2))
    
    # Export results
    benchmark.export_results('results/database_benchmark.json')
    
    print("\n✓ Database benchmark test complete!")