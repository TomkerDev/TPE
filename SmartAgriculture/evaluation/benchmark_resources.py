"""
Resource Usage Benchmarking Module

This module provides tools for monitoring and benchmarking system resource usage.
"""
import time
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, List, Optional
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
class ResourceSnapshot:
    """Snapshot of system resources at a point in time"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    cpu_percent: float = 0.0
    cpu_count: int = 0
    memory_percent: float = 0.0
    memory_used_gb: float = 0.0
    memory_total_gb: float = 0.0
    disk_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    process_memory_mb: float = 0.0
    process_cpu_percent: float = 0.0


@dataclass
class ResourceBenchmarkResult:
    """Container for resource benchmark results"""
    duration: float
    cpu_avg: float
    cpu_max: float
    cpu_min: float
    memory_avg: float
    memory_max: float
    memory_min: float
    disk_usage: float
    network_sent: float
    network_recv: float
    snapshots: List[ResourceSnapshot] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ResourceMonitor:
    """Monitor system resource usage"""
    
    def __init__(self, pid: int = None):
        """
        Initialize resource monitor
        
        Args:
            pid: Process ID to monitor (None for current process)
        """
        self.pid = pid or os.getpid()
        self.process = psutil.Process(self.pid)
        self.snapshots: List[ResourceSnapshot] = []
        self.monitoring = False
        
    def take_snapshot(self) -> ResourceSnapshot:
        """
        Take a snapshot of current resource usage
        
        Returns:
            Resource snapshot
        """
        try:
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            
            # Memory info
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024 ** 3)
            memory_total_gb = memory.total / (1024 ** 3)
            
            # Disk info
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024 ** 3)
            disk_total_gb = disk.total / (1024 ** 3)
            
            # Network info
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / (1024 ** 2)
            network_recv_mb = network.bytes_recv / (1024 ** 2)
            
            # Process info
            process_memory = self.process.memory_info().rss / (1024 ** 2)  # MB
            process_cpu = self.process.cpu_percent(interval=0.1)
            
            snapshot = ResourceSnapshot(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                cpu_count=cpu_count,
                memory_percent=memory_percent,
                memory_used_gb=memory_used_gb,
                memory_total_gb=memory_total_gb,
                disk_percent=disk_percent,
                disk_used_gb=disk_used_gb,
                disk_total_gb=disk_total_gb,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                process_memory_mb=process_memory,
                process_cpu_percent=process_cpu
            )
            
            self.snapshots.append(snapshot)
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to take snapshot: {e}")
            return ResourceSnapshot()
    
    def start_monitoring(self, interval: float = 1.0):
        """
        Start continuous monitoring
        
        Args:
            interval: Monitoring interval in seconds
        """
        try:
            self.monitoring = True
            logger.info(f"Starting resource monitoring (interval: {interval}s)")
            
            while self.monitoring:
                self.take_snapshot()
                time.sleep(interval)
                
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring = False
        logger.info("Stopped resource monitoring")
    
    def get_current_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        try:
            snapshot = self.take_snapshot()
            
            return {
                'timestamp': snapshot.timestamp,
                'cpu': {
                    'percent': snapshot.cpu_percent,
                    'count': snapshot.cpu_count
                },
                'memory': {
                    'percent': snapshot.memory_percent,
                    'used_gb': snapshot.memory_used_gb,
                    'total_gb': snapshot.memory_total_gb
                },
                'disk': {
                    'percent': snapshot.disk_percent,
                    'used_gb': snapshot.disk_used_gb,
                    'total_gb': snapshot.disk_total_gb
                },
                'network': {
                    'sent_mb': snapshot.network_sent_mb,
                    'recv_mb': snapshot.network_recv_mb
                },
                'process': {
                    'memory_mb': snapshot.process_memory_mb,
                    'cpu_percent': snapshot.process_cpu_percent
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get current usage: {e}")
            return {}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of monitored resources"""
        try:
            if not self.snapshots:
                return {}
            
            cpu_values = [s.cpu_percent for s in self.snapshots]
            memory_values = [s.memory_percent for s in self.snapshots]
            process_memory = [s.process_memory_mb for s in self.snapshots]
            process_cpu = [s.process_cpu_percent for s in self.snapshots]
            
            summary = {
                'total_snapshots': len(self.snapshots),
                'duration': (datetime.fromisoformat(self.snapshots[-1].timestamp) - 
                            datetime.fromisoformat(self.snapshots[0].timestamp)).total_seconds(),
                'cpu': {
                    'avg': float(np.mean(cpu_values)),
                    'max': float(np.max(cpu_values)),
                    'min': float(np.min(cpu_values)),
                    'std': float(np.std(cpu_values))
                },
                'memory': {
                    'avg': float(np.mean(memory_values)),
                    'max': float(np.max(memory_values)),
                    'min': float(np.min(memory_values)),
                    'std': float(np.std(memory_values))
                },
                'process': {
                    'memory_avg_mb': float(np.mean(process_memory)),
                    'memory_max_mb': float(np.max(process_memory)),
                    'cpu_avg': float(np.mean(process_cpu)),
                    'cpu_max': float(np.max(process_cpu))
                },
                'disk': {
                    'percent': self.snapshots[-1].disk_percent,
                    'used_gb': self.snapshots[-1].disk_used_gb,
                    'total_gb': self.snapshots[-1].disk_total_gb
                },
                'network': {
                    'total_sent_mb': self.snapshots[-1].network_sent_mb,
                    'total_recv_mb': self.snapshots[-1].network_recv_mb
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get summary: {e}")
            return {}


class ResourceBenchmark:
    """Benchmark resource usage during operations"""
    
    def __init__(self, pid: int = None):
        """
        Initialize resource benchmark
        
        Args:
            pid: Process ID to monitor
        """
        self.pid = pid or os.getpid()
        self.monitor = ResourceMonitor(self.pid)
        self.results: List[ResourceBenchmarkResult] = []
        
    def benchmark_with_monitoring(self, operation_func: Callable,
                                 operation_name: str = "operation",
                                 interval: float = 0.5) -> ResourceBenchmarkResult:
        """
        Benchmark resource usage during an operation
        
        Args:
            operation_func: Function to benchmark
            operation_name: Name of the operation
            interval: Monitoring interval in seconds
            
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"Benchmarking resource usage for: {operation_name}")
            
            # Clear previous snapshots
            self.monitor.snapshots = []
            
            # Start monitoring in a separate thread
            import threading
            monitor_thread = threading.Thread(
                target=self.monitor.start_monitoring,
                args=(interval,),
                daemon=True
            )
            monitor_thread.start()
            
            # Execute operation
            start_time = time.perf_counter()
            operation_func()
            end_time = time.perf_counter()
            
            # Stop monitoring
            self.monitor.stop_monitoring()
            monitor_thread.join(timeout=2)
            
            duration = end_time - start_time
            
            # Get summary
            summary = self.monitor.get_summary()
            
            result = ResourceBenchmarkResult(
                duration=duration,
                cpu_avg=summary.get('cpu', {}).get('avg', 0),
                cpu_max=summary.get('cpu', {}).get('max', 0),
                cpu_min=summary.get('cpu', {}).get('min', 0),
                memory_avg=summary.get('memory', {}).get('avg', 0),
                memory_max=summary.get('memory', {}).get('max', 0),
                memory_min=summary.get('memory', {}).get('min', 0),
                disk_usage=summary.get('disk', {}).get('percent', 0),
                network_sent=summary.get('network', {}).get('total_sent_mb', 0),
                network_recv=summary.get('network', {}).get('total_recv_mb', 0),
                snapshots=self.monitor.snapshots.copy()
            )
            
            self.results.append(result)
            
            logger.info(f"✓ Resource benchmark complete:")
            logger.info(f"  Duration: {result.duration:.2f}s")
            logger.info(f"  CPU Avg: {result.cpu_avg:.1f}%")
            logger.info(f"  Memory Avg: {result.memory_avg:.1f}%")
            
            return result
            
        except Exception as e:
            logger.error(f"Resource benchmark failed: {e}")
            raise
    
    def get_summary(self) -> Dict[str, Any]:
        """Get benchmark summary"""
        try:
            if not self.results:
                return {}
            
            summary = {
                'total_benchmarks': len(self.results),
                'avg_duration': float(np.mean([r.duration for r in self.results])),
                'avg_cpu': float(np.mean([r.cpu_avg for r in self.results])),
                'avg_memory': float(np.mean([r.memory_avg for r in self.results])),
                'max_cpu': float(np.max([r.cpu_max for r in self.results])),
                'max_memory': float(np.max([r.memory_max for r in self.results]))
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
                        'operation': 'operation',
                        'duration': r.duration,
                        'cpu_avg': r.cpu_avg,
                        'cpu_max': r.cpu_max,
                        'cpu_min': r.cpu_min,
                        'memory_avg': r.memory_avg,
                        'memory_max': r.memory_max,
                        'memory_min': r.memory_min,
                        'disk_usage': r.disk_usage,
                        'network_sent_mb': r.network_sent,
                        'network_recv_mb': r.network_recv,
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


def monitor_resources(duration: int = 60, interval: float = 1.0) -> Dict[str, Any]:
    """
    Monitor system resources for a specified duration
    
    Args:
        duration: Monitoring duration in seconds
        interval: Sampling interval in seconds
        
    Returns:
        Resource usage summary
    """
    try:
        monitor = ResourceMonitor()
        
        logger.info(f"Monitoring resources for {duration} seconds...")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            monitor.take_snapshot()
            time.sleep(interval)
        
        summary = monitor.get_summary()
        
        logger.info("✓ Resource monitoring complete")
        
        return summary
        
    except Exception as e:
        logger.error(f"Resource monitoring failed: {e}")
        return {}


if __name__ == "__main__":
    # Test resource benchmark
    print("Testing Resource Benchmark...")
    print("="*80)
    
    # Test 1: Current usage
    print("\n1. Current Resource Usage:")
    monitor = ResourceMonitor()
    usage = monitor.get_current_usage()
    
    print(f"  CPU: {usage['cpu']['percent']:.1f}% ({usage['cpu']['count']} cores)")
    print(f"  Memory: {usage['memory']['percent']:.1f}% ({usage['memory']['used_gb']:.2f}/{usage['memory']['total_gb']:.2f} GB)")
    print(f"  Disk: {usage['disk']['percent']:.1f}% ({usage['disk']['used_gb']:.2f}/{usage['disk']['total_gb']:.2f} GB)")
    print(f"  Process Memory: {usage['process']['memory_mb']:.2f} MB")
    
    # Test 2: Benchmark with monitoring
    print("\n2. Benchmark with Resource Monitoring:")
    
    def test_operation():
        """Simulate a CPU-intensive operation"""
        time.sleep(0.5)
        # Allocate some memory
        data = [i for i in range(1000000)]
        time.sleep(0.5)
        del data
    
    benchmark = ResourceBenchmark()
    result = benchmark.benchmark_with_monitoring(test_operation, "test_operation")
    
    print(f"  Duration: {result.duration:.2f}s")
    print(f"  CPU Avg: {result.cpu_avg:.1f}%")
    print(f"  CPU Max: {result.cpu_max:.1f}%")
    print(f"  Memory Avg: {result.memory_avg:.1f}%")
    print(f"  Memory Max: {result.memory_max:.1f}%")
    
    # Test 3: Multiple operations
    print("\n3. Multiple Operations:")
    
    def light_operation():
        time.sleep(0.1)
    
    def heavy_operation():
        time.sleep(1.0)
        data = [i for i in range(5000000)]
        del data
    
    for op_name, op_func in [("Light", light_operation), ("Heavy", heavy_operation)]:
        result = benchmark.benchmark_with_monitoring(op_func, op_name)
        print(f"  {op_name}: Duration={result.duration:.2f}s, CPU={result.cpu_avg:.1f}%, Memory={result.memory_avg:.1f}%")
    
    # Test 4: Summary
    print("\n4. Summary:")
    summary = benchmark.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")
    
    # Export results
    benchmark.export_results('results/resource_benchmark.json')
    
    print("\n✓ Resource benchmark test complete!")