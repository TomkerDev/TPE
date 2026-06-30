"""
Figure Generation Module

This module provides tools for generating publication-quality figures for reports.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import os

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 16

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FigureGenerator:
    """Generate publication-quality figures"""
    
    def __init__(self, output_dir: str = "results/figures"):
        """
        Initialize figure generator
        
        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def plot_pipeline_throughput(self, data: pd.DataFrame,
                                title: str = "Pipeline Throughput",
                                save_path: str = None) -> str:
        """
        Plot pipeline throughput over time
        
        Args:
            data: DataFrame with throughput data
            title: Plot title
            save_path: Path to save figure
            
        Returns:
            Path to saved figure
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if 'measurement_id' in data.columns and 'throughput' in data.columns:
                ax.plot(data['measurement_id'], data['throughput'], 
                       marker='o', linewidth=2, markersize=4, color='#2e7d32')
                
                # Add average line
                avg_throughput = data['throughput'].mean()
                ax.axhline(y=avg_throughput, color='red', linestyle='--', 
                          label=f'Average: {avg_throughput:.2f} ops/s')
                
                ax.set_xlabel('Measurement ID')
                ax.set_ylabel('Throughput (ops/s)')
                ax.set_title(title)
                ax.legend()
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if save_path is None:
                save_path = os.path.join(self.output_dir, 'pipeline_throughput.png')
            
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✓ Saved figure: {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot pipeline throughput: {e}")
            return ""
    
    def plot_latency_distribution(self, latencies: List[float],
                                 title: str = "Latency Distribution",
                                 save_path: str = None) -> str:
        """
        Plot latency distribution histogram
        
        Args:
            latencies: List of latency measurements
            title: Plot title
            save_path: Path to save figure
            
        Returns:
            Path to saved figure
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            ax.hist(latencies, bins=50, color='#1976d2', alpha=0.7, edgecolor='black')
            
            # Add statistics
            mean_lat = np.mean(latencies)
            median_lat = np.median(latencies)
            p95_lat = np.percentile(latencies, 95)
            
            ax.axvline(mean_lat, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_lat:.2f} ms')
            ax.axvline(median_lat, color='green', linestyle='--', linewidth=2, label=f'Median: {median_lat:.2f} ms')
            ax.axvline(p95_lat, color='orange', linestyle='--', linewidth=2, label=f'P95: {p95_lat:.2f} ms')
            
            ax.set_xlabel('Latency (ms)')
            ax.set_ylabel('Frequency')
            ax.set_title(title)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if save_path is None:
                save_path = os.path.join(self.output_dir, 'latency_distribution.png')
            
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✓ Saved figure: {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot latency distribution: {e}")
            return ""
    
    def plot_database_comparison(self, data: pd.DataFrame,
                                title: str = "Database Performance Comparison",
                                save_path: str = None) -> str:
        """
        Plot database performance comparison
        
        Args:
            data: DataFrame with database results
            title: Plot title
            save_path: Path to save figure
            
        Returns:
            Path to saved figure
        """
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            if 'Database' in data.columns and 'Avg Time (ms)' in data.columns:
                # Query time comparison
                databases = data['Database']
                times = data['Avg Time (ms)']
                colors = ['#1976d2', '#388e3c', '#f57c00', '#d32f2f']
                
                bars1 = ax1.bar(databases, times, color=colors[:len(databases)], alpha=0.8, edgecolor='black')
                ax1.set_ylabel('Average Query Time (ms)')
                ax1.set_title('Query Time Comparison')
                ax1.grid(True, alpha=0.3, axis='y')
                
                # Add value labels
                for bar in bars1:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.2f}', ha='center', va='bottom')
                
                # Throughput comparison
                if 'Throughput (ops/s)' in data.columns:
                    throughputs = data['Throughput (ops/s)']
                    
                    bars2 = ax2.bar(databases, throughputs, color=colors[:len(databases)], alpha=0.8, edgecolor='black')
                    ax2.set_ylabel('Throughput (ops/s)')
                    ax2.set_title('Throughput Comparison')
                    ax2.grid(True, alpha=0.3, axis='y')
                    
                    # Add value labels
                    for bar in bars2:
                        height = bar.get_height()
                        ax2.text(bar.get_x() + bar.get_width()/2., height,
                                f'{height:.2f}', ha='center', va='bottom')
            
            plt.suptitle(title, fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            if save_path is None:
                save_path = os.path.join(self.output_dir, 'database_comparison.png')
            
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✓ Saved figure: {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot database comparison: {e}")
            return ""
    
    def plot_model_comparison(self, data: pd.DataFrame,
                             title: str = "Model Performance Comparison",
                             save_path: str = None) -> str:
        """
        Plot model performance comparison
        
        Args:
            data: DataFrame with model results
            title: Plot title
            save_path: Path to save figure
            
        Returns:
            Path to saved figure
        """
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
            
            if 'Model' in data.columns:
                models = data['Model']
                colors = ['#1976d2', '#388e3c', '#f57c00', '#d32f2f', '#7b1fa2']
                
                # Training time
                if 'Training Time (s)' in data.columns:
                    train_times = data['Training Time (s)']
                    bars1 = ax1.bar(models, train_times, color=colors[:len(models)], alpha=0.8, edgecolor='black')
                    ax1.set_ylabel('Training Time (s)')
                    ax1.set_title('Training Time')
                    ax1.grid(True, alpha=0.3, axis='y')
                    ax1.tick_params(axis='x', rotation=45)
                    
                    for bar in bars1:
                        height = bar.get_height()
                        ax1.text(bar.get_x() + bar.get_width()/2., height,
                                f'{height:.2f}', ha='center', va='bottom', fontsize=8)
                
                # Prediction time
                if 'Prediction Time (s)' in data.columns:
                    pred_times = data['Prediction Time (s)']
                    bars2 = ax2.bar(models, pred_times, color=colors[:len(models)], alpha=0.8, edgecolor='black')
                    ax2.set_ylabel('Prediction Time (s)')
                    ax2.set_title('Prediction Time')
                    ax2.grid(True, alpha=0.3, axis='y')
                    ax2.tick_params(axis='x', rotation=45)
                    
                    for bar in bars2:
                        height = bar.get_height()
                        ax2.text(bar.get_x() + bar.get_width()/2., height,
                                f'{height:.4f}', ha='center', va='bottom', fontsize=8)
                
                # Memory usage
                if 'Memory (MB)' in data.columns:
                    memory = data['Memory (MB)']
                    bars3 = ax3.bar(models, memory, color=colors[:len(models)], alpha=0.8, edgecolor='black')
                    ax3.set_ylabel('Memory (MB)')
                    ax3.set_title('Memory Usage')
                    ax3.grid(True, alpha=0.3, axis='y')
                    ax3.tick_params(axis='x', rotation=45)
                    
                    for bar in bars3:
                        height = bar.get_height()
                        ax3.text(bar.get_x() + bar.get_width()/2., height,
                                f'{height:.2f}', ha='center', va='bottom', fontsize=8)
                
                # Accuracy
                if 'Accuracy' in data.columns:
                    accuracy = data['Accuracy']
                    bars4 = ax4.bar(models, accuracy, color=colors[:len(models)], alpha=0.8, edgecolor='black')
                    ax4.set_ylabel('Accuracy')
                    ax4.set_title('Model Accuracy')
                    ax4.set_ylim([0, 1.1])
                    ax4.grid(True, alpha=0.3, axis='y')
                    ax4.tick_params(axis='x', rotation=45)
                    
                    for bar in bars4:
                        height = bar.get_height()
                        ax4.text(bar.get_x() + bar.get_width()/2., height,
                                f'{height:.3f}', ha='center', va='bottom', fontsize=8)
            
            plt.suptitle(title, fontsize=16, fontweight='bold', y=1.00)
            plt.tight_layout()
            
            if save_path is None:
                save_path = os.path.join(self.output_dir, 'model_comparison.png')
            
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✓ Saved figure: {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot model comparison: {e}")
            return ""
    
    def plot_scalability_curve(self, data: pd.DataFrame,
                              title: str = "System Scalability",
                              save_path: str = None) -> str:
        """
        Plot scalability curve
        
        Args:
            data: DataFrame with scalability data
            title: Plot title
            save_path: Path to save figure
            
        Returns:
            Path to saved figure
        """
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            if 'load_size' in data.columns:
                load_sizes = data['load_size']
                
                # Throughput vs Load
                if 'throughput' in data.columns:
                    throughputs = data['throughput']
                    ax1.plot(load_sizes, throughputs, marker='o', linewidth=2, 
                            markersize=6, color='#2e7d32')
                    ax1.set_xlabel('Load Size (operations)')
                    ax1.set_ylabel('Throughput (ops/s)')
                    ax1.set_title('Throughput vs Load')
                    ax1.grid(True, alpha=0.3)
                    ax1.set_xscale('log')
                
                # Latency vs Load
                if 'avg_latency' in data.columns:
                    latencies = data['avg_latency']
                    ax2.plot(load_sizes, latencies, marker='s', linewidth=2, 
                            markersize=6, color='#d32f2f')
                    ax2.set_xlabel('Load Size (operations)')
                    ax2.set_ylabel('Average Latency (ms)')
                    ax2.set_title('Latency vs Load')
                    ax2.grid(True, alpha=0.3)
                    ax2.set_xscale('log')
            
            plt.suptitle(title, fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            if save_path is None:
                save_path = os.path.join(self.output_dir, 'scalability_curve.png')
            
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✓ Saved figure: {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot scalability curve: {e}")
            return ""
    
    def plot_resource_usage(self, data: Dict[str, Any],
                           title: str = "Resource Usage Over Time",
                           save_path: str = None) -> str:
        """
        Plot resource usage over time
        
        Args:
            data: Dictionary with resource usage data
            title: Plot title
            save_path: Path to save figure
            
        Returns:
            Path to saved figure
        """
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Extract data
            if 'detailed_results' in data:
                results = data['detailed_results']
                timestamps = [datetime.fromisoformat(r['timestamp']) for r in results]
                cpu_values = [r.get('cpu_avg', 0) for r in results]
                memory_values = [r.get('memory_avg', 0) for r in results]
                
                # CPU usage
                ax1.plot(timestamps, cpu_values, linewidth=2, color='#1976d2', label='CPU')
                ax1.set_ylabel('CPU Usage (%)')
                ax1.set_title('CPU Usage Over Time')
                ax1.grid(True, alpha=0.3)
                ax1.legend()
                
                # Memory usage
                ax2.plot(timestamps, memory_values, linewidth=2, color='#388e3c', label='Memory')
                ax2.set_ylabel('Memory Usage (%)')
                ax2.set_xlabel('Time')
                ax2.set_title('Memory Usage Over Time')
                ax2.grid(True, alpha=0.3)
                ax2.legend()
            
            plt.suptitle(title, fontsize=16, fontweight='bold', y=1.00)
            plt.tight_layout()
            
            if save_path is None:
                save_path = os.path.join(self.output_dir, 'resource_usage.png')
            
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✓ Saved figure: {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot resource usage: {e}")
            return ""
    
    def plot_radar_chart(self, models: Dict[str, Dict[str, float]],
                        metrics: List[str],
                        title: str = "Model Comparison Radar Chart",
                        save_path: str = None) -> str:
        """
        Plot radar chart for model comparison
        
        Args:
            models: Dictionary of model names to metric values
            metrics: List of metric names
            title: Plot title
            save_path: Path to save figure
            
        Returns:
            Path to saved figure
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            
            # Number of variables
            N = len(metrics)
            
            # Angle for each axis
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]  # Complete the loop
            
            # Colors for different models
            colors = plt.cm.Set3(np.linspace(0, 1, len(models)))
            
            # Plot each model
            for idx, (model_name, model_metrics) in enumerate(models.items()):
                values = [model_metrics.get(metric, 0) for metric in metrics]
                values += values[:1]  # Complete the loop
                
                ax.plot(angles, values, 'o-', linewidth=2, label=model_name, color=colors[idx])
                ax.fill(angles, values, alpha=0.15, color=colors[idx])
            
            # Set axis labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics)
            
            # Add legend
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
            
            plt.title(title, fontsize=16, fontweight='bold', pad=20)
            plt.tight_layout()
            
            if save_path is None:
                save_path = os.path.join(self.output_dir, 'radar_chart.png')
            
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✓ Saved figure: {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot radar chart: {e}")
            return ""
    
    def plot_correlation_matrix(self, data: pd.DataFrame,
                               title: str = "Sensor Correlation Matrix",
                               save_path: str = None) -> str:
        """
        Plot correlation matrix heatmap
        
        Args:
            data: DataFrame with sensor data
            title: Plot title
            save_path: Path to save figure
            
        Returns:
            Path to saved figure
        """
        try:
            fig, ax = plt.subplots(figsize=(12, 10))
            
            # Calculate correlation matrix
            pivot_df = data.pivot_table(
                index='timestamp',
                columns='sensor_type',
                values='value',
                aggfunc='mean'
            )
            
            corr_matrix = pivot_df.corr()
            
            # Plot heatmap
            im = ax.imshow(corr_matrix, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label('Correlation', rotation=270, labelpad=20)
            
            # Set ticks
            ax.set_xticks(np.arange(len(corr_matrix.columns)))
            ax.set_yticks(np.arange(len(corr_matrix.index)))
            ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
            ax.set_yticklabels(corr_matrix.index)
            
            # Add correlation values
            for i in range(len(corr_matrix)):
                for j in range(len(corr_matrix)):
                    text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                                  ha="center", va="center", color="black" if abs(corr_matrix.iloc[i, j]) < 0.5 else "white")
            
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            plt.tight_layout()
            
            if save_path is None:
                save_path = os.path.join(self.output_dir, 'correlation_matrix.png')
            
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✓ Saved figure: {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot correlation matrix: {e}")
            return ""
    
    def generate_all_figures(self, data: Dict[str, Any]) -> List[str]:
        """
        Generate all standard figures
        
        Args:
            data: Dictionary containing all benchmark data
            
        Returns:
            List of generated figure paths
        """
        try:
            logger.info("Generating all figures...")
            
            figure_paths = []
            
            # Pipeline throughput
            if 'throughput' in data:
                df = pd.DataFrame(data['throughput'].get('detailed_results', []))
                if not df.empty:
                    path = self.plot_pipeline_throughput(df)
                    if path:
                        figure_paths.append(path)
            
            # Database comparison
            if 'database' in data:
                df = pd.DataFrame(data['database'].get('detailed_results', []))
                if not df.empty:
                    path = self.plot_database_comparison(df)
                    if path:
                        figure_paths.append(path)
            
            # Model comparison
            if 'models' in data:
                df = pd.DataFrame(data['models'].get('detailed_results', []))
                if not df.empty:
                    path = self.plot_model_comparison(df)
                    if path:
                        figure_paths.append(path)
            
            # Scalability
            if 'scalability' in data:
                df = pd.DataFrame(data['scalability'].get('detailed_results', []))
                if not df.empty:
                    path = self.plot_scalability_curve(df)
                    if path:
                        figure_paths.append(path)
            
            # Resource usage
            if 'resources' in data:
                path = self.plot_resource_usage(data['resources'])
                if path:
                    figure_paths.append(path)
            
            logger.info(f"✓ Generated {len(figure_paths)} figures")
            
            return figure_paths
            
        except Exception as e:
            logger.error(f"Failed to generate figures: {e}")
            return []


def generate_all_figures(results_dir: str = "results", 
                        output_dir: str = "results/figures") -> List[str]:
    """
    Convenience function to generate all figures
    
    Args:
        results_dir: Directory with benchmark results
        output_dir: Directory to save figures
        
    Returns:
        List of generated figure paths
    """
    try:
        # Load all results
        data = {}
        
        result_files = [
            'pipeline_benchmark.json',
            'database_benchmark.json',
            'model_benchmark.json',
            'resource_benchmark.json',
            'scalability_test.json',
            'latency_test.json',
            'throughput_test.json'
        ]
        
        for filename in result_files:
            filepath = os.path.join(results_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    key = filename.replace('_benchmark.json', '').replace('_test.json', '')
                    data[key] = json.load(f)
        
        # Generate figures
        generator = FigureGenerator(output_dir)
        return generator.generate_all_figures(data)
        
    except Exception as e:
        logger.error(f"Failed to generate figures: {e}")
        return []


if __name__ == "__main__":
    # Generate figures
    print("Generating Figures...")
    print("="*80)
    
    generator = FigureGenerator()
    
    # Load results
    data = {}
    
    # Try to load sample data
    try:
        with open('results/pipeline_benchmark.json', 'r') as f:
            data['pipeline'] = json.load(f)
    except:
        pass
    
    try:
        with open('results/database_benchmark.json', 'r') as f:
            data['database'] = json.load(f)
    except:
        pass
    
    try:
        with open('results/model_benchmark.json', 'r') as f:
            data['models'] = json.load(f)
    except:
        pass
    
    if data:
        print("\nGenerating figures from loaded data...")
        figure_paths = generator.generate_all_figures(data)
        
        print(f"\n✓ Generated {len(figure_paths)} figures:")
        for path in figure_paths:
            print(f"  - {path}")
    else:
        print("\nNo data available. Please run benchmarks first.")
        print("Generating sample figures...")
        
        # Generate sample figures
        sample_data = pd.DataFrame({
            'measurement_id': range(10),
            'throughput': np.random.normal(1000, 100, 10)
        })
        
        generator.plot_pipeline_throughput(sample_data)
        
        sample_latencies = np.random.normal(50, 10, 1000)
        generator.plot_latency_distribution(sample_latencies)
        
        print("\n✓ Sample figures generated in results/figures/")
    
    print("\n✓ Figure generation complete!")