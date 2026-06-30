"""
Sensor Analysis Module
Analyzes individual sensor performance and health
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
from scipy import stats

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SensorAnalysis:
    """Analyzes sensor performance and health"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with DataFrame
        
        Args:
            df: DataFrame with sensor data
        """
        self.df = df.copy()
        self.sensor_results = {}
        
    def get_all_sensors(self) -> List[str]:
        """Get list of all unique sensors"""
        if 'sensor_id' in self.df.columns:
            return self.df['sensor_id'].unique().tolist()
        return []
    
    def get_sensor_types(self) -> List[str]:
        """Get list of all sensor types"""
        if 'sensor_type' in self.df.columns:
            return self.df['sensor_type'].unique().tolist()
        return []
    
    def analyze_sensor(self, sensor_id: str) -> Dict[str, Any]:
        """
        Analyze individual sensor performance
        
        Args:
            sensor_id: Sensor ID to analyze
            
        Returns:
            Dictionary with sensor analysis
        """
        try:
            if 'sensor_id' not in self.df.columns:
                return {}
            
            sensor_data = self.df[self.df['sensor_id'] == sensor_id].copy()
            
            if sensor_data.empty:
                logger.warning(f"No data found for sensor {sensor_id}")
                return {}
            
            analysis = {
                'sensor_id': sensor_id,
                'sensor_type': sensor_data['sensor_type'].iloc[0] if 'sensor_type' in sensor_data.columns else 'unknown',
                'total_readings': len(sensor_data),
                'date_range': {
                    'start': sensor_data['timestamp'].min() if 'timestamp' in sensor_data.columns else None,
                    'end': sensor_data['timestamp'].max() if 'timestamp' in sensor_data.columns else None
                }
            }
            
            # Value statistics
            if 'value' in sensor_data.columns:
                values = sensor_data['value'].dropna()
                
                analysis['value_stats'] = {
                    'mean': float(values.mean()),
                    'median': float(values.median()),
                    'std': float(values.std()),
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'range': float(values.max() - values.min())
                }
                
                # Data quality
                if 'quality' in sensor_data.columns:
                    analysis['quality_stats'] = {
                        'mean_quality': float(sensor_data['quality'].mean()),
                        'min_quality': float(sensor_data['quality'].min()),
                        'max_quality': float(sensor_data['quality'].max()),
                        'low_quality_count': len(sensor_data[sensor_data['quality'] < 70])
                    }
                
                # Outliers
                if 'is_outlier' in sensor_data.columns:
                    analysis['outlier_stats'] = {
                        'total_outliers': int(sensor_data['is_outlier'].sum()),
                        'outlier_percentage': float(sensor_data['is_outlier'].mean() * 100)
                    }
                
                # Completeness
                analysis['completeness'] = {
                    'total_expected': None,  # Would need expected frequency
                    'actual_readings': len(sensor_data),
                    'missing_readings': None,
                    'completeness_pct': None
                }
            
            # Frequency analysis
            if 'timestamp' in sensor_data.columns:
                sensor_data = sensor_data.sort_values('timestamp')
                time_diffs = sensor_data['timestamp'].diff().dropna()
                
                if not time_diffs.empty:
                    analysis['frequency'] = {
                        'mean_interval_seconds': float(time_diffs.mean().total_seconds()),
                        'median_interval_seconds': float(time_diffs.median().total_seconds()),
                        'std_interval_seconds': float(time_diffs.std().total_seconds()),
                        'min_interval_seconds': float(time_diffs.min().total_seconds()),
                        'max_interval_seconds': float(time_diffs.max().total_seconds())
                    }
            
            self.sensor_results[sensor_id] = analysis
            logger.info(f"✓ Analyzed sensor {sensor_id}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze sensor {sensor_id}: {e}")
            return {}
    
    def analyze_all_sensors(self) -> pd.DataFrame:
        """
        Analyze all sensors
        
        Returns:
            DataFrame with analysis for all sensors
        """
        try:
            sensors = self.get_all_sensors()
            
            analyses = []
            for sensor_id in sensors:
                analysis = self.analyze_sensor(sensor_id)
                if analysis:
                    analyses.append(analysis)
            
            if not analyses:
                return pd.DataFrame()
            
            # Convert to DataFrame
            summary_df = pd.DataFrame(analyses)
            
            self.sensor_results['all'] = summary_df
            logger.info(f"✓ Analyzed {len(analyses)} sensors")
            
            return summary_df
            
        except Exception as e:
            logger.error(f"Failed to analyze all sensors: {e}")
            return pd.DataFrame()
    
    def rank_sensors_by_quality(self, metric: str = 'mean_quality') -> pd.DataFrame:
        """
        Rank sensors by quality metric
        
        Args:
            metric: Quality metric to rank by
            
        Returns:
            DataFrame with ranked sensors
        """
        try:
            if 'all' not in self.sensor_results:
                self.analyze_all_sensors()
            
            summary_df = self.sensor_results.get('all')
            
            if summary_df is None or summary_df.empty:
                return pd.DataFrame()
            
            # Extract quality stats
            quality_data = []
            for _, row in summary_df.iterrows():
                sensor_id = row['sensor_id']
                if 'quality_stats' in row and row['quality_stats']:
                    quality_data.append({
                        'sensor_id': sensor_id,
                        'sensor_type': row['sensor_type'],
                        'mean_quality': row['quality_stats'].get('mean_quality', 0),
                        'total_readings': row['total_readings']
                    })
            
            if not quality_data:
                return pd.DataFrame()
            
            quality_df = pd.DataFrame(quality_data)
            quality_df = quality_df.sort_values('mean_quality', ascending=False)
            
            logger.info("✓ Ranked sensors by quality")
            
            return quality_df
            
        except Exception as e:
            logger.error(f"Failed to rank sensors: {e}")
            return pd.DataFrame()
    
    def identify_problematic_sensors(self, 
                                     quality_threshold: float = 70.0,
                                     outlier_threshold: float = 10.0,
                                     min_readings: int = 100) -> pd.DataFrame:
        """
        Identify problematic sensors
        
        Args:
            quality_threshold: Minimum acceptable quality score
            outlier_threshold: Maximum acceptable outlier percentage
            min_readings: Minimum number of readings required
            
        Returns:
            DataFrame with problematic sensors
        """
        try:
            if 'all' not in self.sensor_results:
                self.analyze_all_sensors()
            
            summary_df = self.sensor_results.get('all')
            
            if summary_df is None or summary_df.empty:
                return pd.DataFrame()
            
            problematic = []
            
            for _, row in summary_df.iterrows():
                issues = []
                
                # Check quality
                if 'quality_stats' in row and row['quality_stats']:
                    mean_quality = row['quality_stats'].get('mean_quality', 100)
                    if mean_quality < quality_threshold:
                        issues.append(f"Low quality ({mean_quality:.1f}%)")
                
                # Check outliers
                if 'outlier_stats' in row and row['outlier_stats']:
                    outlier_pct = row['outlier_stats'].get('outlier_percentage', 0)
                    if outlier_pct > outlier_threshold:
                        issues.append(f"High outliers ({outlier_pct:.1f}%)")
                
                # Check data volume
                if row['total_readings'] < min_readings:
                    issues.append(f"Low data volume ({row['total_readings']} readings)")
                
                if issues:
                    problematic.append({
                        'sensor_id': row['sensor_id'],
                        'sensor_type': row['sensor_type'],
                        'issues': issues,
                        'issue_count': len(issues)
                    })
            
            if not problematic:
                return pd.DataFrame()
            
            problematic_df = pd.DataFrame(problematic)
            problematic_df = problematic_df.sort_values('issue_count', ascending=False)
            
            logger.info(f"✓ Identified {len(problematic)} problematic sensors")
            
            return problematic_df
            
        except Exception as e:
            logger.error(f"Failed to identify problematic sensors: {e}")
            return pd.DataFrame()
    
    def compute_sensor_correlation_matrix(self) -> Dict[str, pd.DataFrame]:
        """
        Compute correlation matrix between sensors
        
        Returns:
            Dictionary of correlation matrices by sensor type
        """
        try:
            if 'sensor_id' not in self.df.columns or 'timestamp' not in self.df.columns:
                return {}
            
            correlation_matrices = {}
            
            for sensor_type in self.df['sensor_type'].unique():
                # Filter by sensor type
                df_type = self.df[self.df['sensor_type'] == sensor_type]
                
                # Pivot to get sensors as columns
                pivot_df = df_type.pivot_table(
                    index='timestamp',
                    columns='sensor_id',
                    values='value',
                    aggfunc='mean'
                )
                
                # Compute correlation
                if not pivot_df.empty and len(pivot_df.columns) > 1:
                    corr = pivot_df.corr()
                    correlation_matrices[sensor_type] = corr
            
            self.sensor_results['correlation_matrices'] = correlation_matrices
            logger.info(f"✓ Computed correlation matrices for {len(correlation_matrices)} sensor types")
            
            return correlation_matrices
            
        except Exception as e:
            logger.error(f"Failed to compute sensor correlation matrix: {e}")
            return {}
    
    def detect_sensor_drift(self, sensor_id: str, window: int = 100) -> Dict[str, Any]:
        """
        Detect sensor drift over time
        
        Args:
            sensor_id: Sensor ID
            window: Rolling window size
            
        Returns:
            Dictionary with drift analysis
        """
        try:
            if 'sensor_id' not in self.df.columns:
                return {}
            
            sensor_data = self.df[self.df['sensor_id'] == sensor_id].copy()
            sensor_data = sensor_data.sort_values('timestamp')
            
            if len(sensor_data) < window:
                logger.warning(f"Not enough data for drift detection")
                return {}
            
            # Compute rolling statistics
            sensor_data['rolling_mean'] = sensor_data['value'].rolling(window=window).mean()
            sensor_data['rolling_std'] = sensor_data['value'].rolling(window=window).std()
            
            # Detect drift (significant change in mean)
            mean_change = sensor_data['rolling_mean'].diff().abs()
            drift_threshold = sensor_data['value'].std() * 0.5
            
            drift_points = sensor_data[mean_change > drift_threshold]
            
            drift_analysis = {
                'sensor_id': sensor_id,
                'window': window,
                'drift_points': len(drift_points),
                'drift_percentage': (len(drift_points) / len(sensor_data)) * 100,
                'mean_drift_magnitude': float(mean_change.mean()),
                'max_drift_magnitude': float(mean_change.max())
            }
            
            self.sensor_results[f'drift_{sensor_id}'] = drift_analysis
            logger.info(f"✓ Analyzed drift for {sensor_id}")
            
            return drift_analysis
            
        except Exception as e:
            logger.error(f"Failed to detect sensor drift: {e}")
            return {}
    
    def plot_sensor_timeseries(self, sensor_id: str, column: str = 'value',
                              figsize: Tuple[int, int] = (15, 6),
                              save_path: Optional[str] = None):
        """
        Plot sensor time series
        
        Args:
            sensor_id: Sensor ID
            column: Column to plot
            figsize: Figure size
            save_path: Optional path to save figure
        """
        try:
            if 'sensor_id' not in self.df.columns or 'timestamp' not in self.df.columns:
                return
            
            sensor_data = self.df[self.df['sensor_id'] == sensor_id].copy()
            sensor_data = sensor_data.sort_values('timestamp')
            
            if sensor_data.empty:
                return
            
            plt.figure(figsize=figsize)
            plt.plot(sensor_data['timestamp'], sensor_data[column], linewidth=1)
            
            plt.title(f'Sensor {sensor_id}: {column} Over Time', fontsize=14, fontweight='bold')
            plt.xlabel('Timestamp', fontsize=12)
            plt.ylabel(column, fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"✓ Saved sensor timeseries to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Failed to plot sensor timeseries: {e}")
    
    def plot_sensor_distribution(self, sensor_type: str = None,
                                figsize: Tuple[int, int] = (12, 6),
                                save_path: Optional[str] = None):
        """
        Plot sensor value distribution
        
        Args:
            sensor_type: Optional sensor type filter
            figsize: Figure size
            save_path: Optional path to save figure
        """
        try:
            df = self.df.copy()
            
            if sensor_type:
                df = df[df['sensor_type'] == sensor_type]
            
            if df.empty or 'value' not in df.columns:
                return
            
            plt.figure(figsize=figsize)
            
            # Plot histogram for each sensor type
            if sensor_type is None and 'sensor_type' in df.columns:
                for sensor_type in df['sensor_type'].unique():
                    subset = df[df['sensor_type'] == sensor_type]
                    plt.hist(subset['value'], bins=30, alpha=0.6, label=sensor_type)
                
                plt.legend()
                title = 'Value Distribution by Sensor Type'
            else:
                plt.hist(df['value'], bins=30, alpha=0.7)
                title = f'Value Distribution: {sensor_type}' if sensor_type else 'Value Distribution'
            
            plt.title(title, fontsize=14, fontweight='bold')
            plt.xlabel('Value', fontsize=12)
            plt.ylabel('Frequency', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"✓ Saved distribution plot to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Failed to plot sensor distribution: {e}")
    
    def get_sensor_summary(self) -> str:
        """
        Generate sensor analysis summary
        
        Returns:
            Formatted summary report
        """
        try:
            report = []
            report.append("=" * 70)
            report.append("SENSOR ANALYSIS REPORT")
            report.append("=" * 70)
            
            # Overview
            sensors = self.get_all_sensors()
            sensor_types = self.get_sensor_types()
            
            report.append(f"\nTotal Sensors: {len(sensors)}")
            report.append(f"Sensor Types: {len(sensor_types)}")
            report.append(f"Types: {', '.join(sensor_types)}")
            
            # Problematic sensors
            problematic = self.identify_problematic_sensors()
            if not problematic.empty:
                report.append(f"\n--- Problematic Sensors ---")
                report.append(f"Total: {len(problematic)}")
                for _, row in problematic.head(10).iterrows():
                    report.append(f"  {row['sensor_id']} ({row['sensor_type']}): {', '.join(row['issues'])}")
            
            # Quality ranking
            quality_ranking = self.rank_sensors_by_quality()
            if not quality_ranking.empty:
                report.append(f"\n--- Top 5 Sensors by Quality ---")
                for _, row in quality_ranking.head(5).iterrows():
                    report.append(f"  {row['sensor_id']}: {row['mean_quality']:.1f}%")
            
            report.append("\n" + "=" * 70)
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Failed to generate sensor summary: {e}")
            return "Error generating report"


def analyze_sensors(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Convenience function to analyze all sensors
    
    Args:
        df: DataFrame with sensor data
        
    Returns:
        Dictionary with sensor analysis results
    """
    analysis = SensorAnalysis(df)
    analysis.analyze_all_sensors()
    analysis.identify_problematic_sensors()
    analysis.rank_sensors_by_quality()
    
    return analysis.sensor_results


def print_sensor_summary(df: pd.DataFrame):
    """
    Print sensor analysis summary
    
    Args:
        df: DataFrame with sensor data
    """
    analysis = SensorAnalysis(df)
    analysis.analyze_all_sensors()
    print(analysis.get_sensor_summary())


if __name__ == "__main__":
    # Test with sample data
    from analytics.load_data import load_sample_data
    
    print("Loading sample data...")
    df = load_sample_data()
    
    print("\nAnalyzing sensors...")
    analysis = SensorAnalysis(df)
    
    # Analyze all sensors
    summary = analysis.analyze_all_sensors()
    print(f"\nAnalyzed {len(summary)} sensors")
    
    # Identify problematic sensors
    problematic = analysis.identify_problematic_sensors()
    if not problematic.empty:
        print(f"\nProblematic sensors: {len(problematic)}")
        print(problematic[['sensor_id', 'sensor_type', 'issues']].head())
    
    # Print summary
    print(analysis.get_sensor_summary())
    
    # Plot
    analysis.plot_sensor_distribution(save_path='results/sensor_distribution.png')