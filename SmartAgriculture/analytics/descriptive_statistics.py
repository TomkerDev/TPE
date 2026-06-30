"""
Descriptive Statistics Module
Computes comprehensive descriptive statistics for sensor data
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
from scipy import stats

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DescriptiveStatistics:
    """Computes descriptive statistics for sensor data"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with DataFrame
        
        Args:
            df: DataFrame with sensor data
        """
        self.df = df.copy()
        self.stats_results = {}
        
    def compute_basic_statistics(self) -> Dict[str, Any]:
        """
        Compute basic descriptive statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            # Overall statistics
            basic_stats = {
                'total_observations': len(self.df),
                'total_sensors': self.df['sensor_id'].nunique() if 'sensor_id' in self.df.columns else 0,
                'sensor_types': self.df['sensor_type'].unique().tolist() if 'sensor_type' in self.df.columns else [],
                'date_range': {
                    'start': self.df['timestamp'].min() if 'timestamp' in self.df.columns else None,
                    'end': self.df['timestamp'].max() if 'timestamp' in self.df.columns else None
                },
                'missing_values': self.df.isnull().sum().to_dict(),
                'data_types': self.df.dtypes.astype(str).to_dict()
            }
            
            self.stats_results['basic'] = basic_stats
            return basic_stats
            
        except Exception as e:
            logger.error(f"Failed to compute basic statistics: {e}")
            return {}
    
    def compute_numeric_statistics(self, column: str = 'value') -> Dict[str, Any]:
        """
        Compute numeric statistics for a column
        
        Args:
            column: Column name to analyze
            
        Returns:
            Dictionary with numeric statistics
        """
        try:
            if column not in self.df.columns:
                logger.error(f"Column {column} not found")
                return {}
            
            data = self.df[column].dropna()
            
            numeric_stats = {
                'count': len(data),
                'mean': float(data.mean()),
                'median': float(data.median()),
                'mode': float(data.mode().iloc[0]) if not data.mode().empty else None,
                'std': float(data.std()),
                'variance': float(data.var()),
                'min': float(data.min()),
                'max': float(data.max()),
                'range': float(data.max() - data.min()),
                'q1': float(data.quantile(0.25)),
                'q2': float(data.quantile(0.50)),
                'q3': float(data.quantile(0.75)),
                'iqr': float(data.quantile(0.75) - data.quantile(0.25)),
                'skewness': float(data.skew()),
                'kurtosis': float(data.kurtosis()),
                'cv': float(data.std() / data.mean()) if data.mean() != 0 else None  # Coefficient of variation
            }
            
            # Percentiles
            percentiles = [5, 10, 25, 50, 75, 90, 95, 99]
            numeric_stats['percentiles'] = {
                f'p{p}': float(data.quantile(p/100)) for p in percentiles
            }
            
            self.stats_results['numeric'] = numeric_stats
            return numeric_stats
            
        except Exception as e:
            logger.error(f"Failed to compute numeric statistics: {e}")
            return {}
    
    def compute_by_sensor_type(self, column: str = 'value') -> pd.DataFrame:
        """
        Compute statistics grouped by sensor type
        
        Args:
            column: Column to analyze
            
        Returns:
            DataFrame with statistics by sensor type
        """
        try:
            if 'sensor_type' not in self.df.columns:
                logger.error("sensor_type column not found")
                return pd.DataFrame()
            
            # Group by sensor type
            grouped = self.df.groupby('sensor_type')[column].agg([
                'count',
                'mean',
                'median',
                'std',
                'var',
                'min',
                'max',
                'sum'
            ]).round(4)
            
            # Add additional statistics
            grouped['range'] = grouped['max'] - grouped['min']
            grouped['cv'] = (grouped['std'] / grouped['mean']).round(4)
            
            # Rename columns for clarity
            grouped.columns = [
                'Count', 'Mean', 'Median', 'Std Dev', 'Variance',
                'Min', 'Max', 'Sum', 'Range', 'CV'
            ]
            
            self.stats_results['by_sensor_type'] = grouped
            return grouped
            
        except Exception as e:
            logger.error(f"Failed to compute statistics by sensor type: {e}")
            return pd.DataFrame()
    
    def compute_by_sensor(self, column: str = 'value') -> pd.DataFrame:
        """
        Compute statistics grouped by sensor ID
        
        Args:
            column: Column to analyze
            
        Returns:
            DataFrame with statistics by sensor
        """
        try:
            if 'sensor_id' not in self.df.columns:
                logger.error("sensor_id column not found")
                return pd.DataFrame()
            
            # Group by sensor
            grouped = self.df.groupby('sensor_id')[column].agg([
                'count',
                'mean',
                'median',
                'std',
                'min',
                'max'
            ]).round(4)
            
            grouped.columns = ['Count', 'Mean', 'Median', 'Std Dev', 'Min', 'Max']
            
            self.stats_results['by_sensor'] = grouped
            return grouped
            
        except Exception as e:
            logger.error(f"Failed to compute statistics by sensor: {e}")
            return pd.DataFrame()
    
    def detect_outliers_iqr(self, column: str = 'value', 
                           multiplier: float = 1.5) -> Dict[str, Any]:
        """
        Detect outliers using IQR method
        
        Args:
            column: Column to analyze
            multiplier: IQR multiplier for outlier detection
            
        Returns:
            Dictionary with outlier information
        """
        try:
            if column not in self.df.columns:
                return {}
            
            data = self.df[column].dropna()
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            
            lower_bound = q1 - multiplier * iqr
            upper_bound = q3 + multiplier * iqr
            
            outliers = self.df[(self.df[column] < lower_bound) | (self.df[column] > upper_bound)]
            
            outlier_stats = {
                'total_outliers': len(outliers),
                'outlier_percentage': (len(outliers) / len(self.df)) * 100,
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound),
                'q1': float(q1),
                'q3': float(q3),
                'iqr': float(iqr)
            }
            
            if 'sensor_type' in self.df.columns:
                outlier_stats['outliers_by_type'] = outliers.groupby('sensor_type').size().to_dict()
            
            self.stats_results['outliers_iqr'] = outlier_stats
            return outlier_stats
            
        except Exception as e:
            logger.error(f"Failed to detect outliers: {e}")
            return {}
    
    def detect_outliers_zscore(self, column: str = 'value', 
                              threshold: float = 3.0) -> Dict[str, Any]:
        """
        Detect outliers using Z-score method
        
        Args:
            column: Column to analyze
            threshold: Z-score threshold
            
        Returns:
            Dictionary with outlier information
        """
        try:
            if column not in self.df.columns:
                return {}
            
            data = self.df[column].dropna()
            z_scores = np.abs(stats.zscore(data))
            
            outliers = self.df.iloc[np.where(z_scores > threshold)]
            
            outlier_stats = {
                'total_outliers': len(outliers),
                'outlier_percentage': (len(outliers) / len(self.df)) * 100,
                'threshold': threshold,
                'max_zscore': float(z_scores.max())
            }
            
            if 'sensor_type' in self.df.columns:
                outlier_stats['outliers_by_type'] = outliers.groupby('sensor_type').size().to_dict()
            
            self.stats_results['outliers_zscore'] = outlier_stats
            return outlier_stats
            
        except Exception as e:
            logger.error(f"Failed to detect outliers using Z-score: {e}")
            return {}
    
    def compute_correlation_matrix(self, numeric_columns: list = None) -> pd.DataFrame:
        """
        Compute correlation matrix
        
        Args:
            numeric_columns: List of numeric columns (if None, auto-detect)
            
        Returns:
            Correlation matrix DataFrame
        """
        try:
            if numeric_columns is None:
                numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
            
            corr_matrix = self.df[numeric_columns].corr()
            
            self.stats_results['correlation'] = corr_matrix
            return corr_matrix
            
        except Exception as e:
            logger.error(f"Failed to compute correlation matrix: {e}")
            return pd.DataFrame()
    
    def get_summary_report(self) -> str:
        """
        Generate text summary report
        
        Returns:
            Formatted summary report
        """
        try:
            report = []
            report.append("=" * 70)
            report.append("DESCRIPTIVE STATISTICS REPORT")
            report.append("=" * 70)
            
            # Basic statistics
            if 'basic' in self.stats_results:
                basic = self.stats_results['basic']
                report.append(f"\nTotal Observations: {basic.get('total_observations', 'N/A')}")
                report.append(f"Total Sensors: {basic.get('total_sensors', 'N/A')}")
                report.append(f"Sensor Types: {', '.join(basic.get('sensor_types', []))}")
            
            # Numeric statistics
            if 'numeric' in self.stats_results:
                numeric = self.stats_results['numeric']
                report.append(f"\n--- Value Statistics ---")
                report.append(f"Mean: {numeric.get('mean', 'N/A'):.2f}")
                report.append(f"Median: {numeric.get('median', 'N/A'):.2f}")
                report.append(f"Std Dev: {numeric.get('std', 'N/A'):.2f}")
                report.append(f"Min: {numeric.get('min', 'N/A'):.2f}")
                report.append(f"Max: {numeric.get('max', 'N/A'):.2f}")
            
            # By sensor type
            if 'by_sensor_type' in self.stats_results:
                report.append(f"\n--- Statistics by Sensor Type ---")
                by_type = self.stats_results['by_sensor_type']
                report.append(by_type.to_string())
            
            # Outliers
            if 'outliers_iqr' in self.stats_results:
                outliers = self.stats_results['outliers_iqr']
                report.append(f"\n--- Outlier Detection (IQR) ---")
                report.append(f"Total Outliers: {outliers.get('total_outliers', 'N/A')}")
                report.append(f"Outlier Percentage: {outliers.get('outlier_percentage', 'N/A'):.2f}%")
            
            report.append("\n" + "=" * 70)
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Failed to generate summary report: {e}")
            return "Error generating report"
    
    def get_all_statistics(self) -> Dict[str, Any]:
        """
        Compute all statistics
        
        Returns:
            Dictionary with all statistics
        """
        self.compute_basic_statistics()
        self.compute_numeric_statistics()
        self.compute_by_sensor_type()
        self.compute_by_sensor()
        self.detect_outliers_iqr()
        self.detect_outliers_zscore()
        
        return self.stats_results


def compute_descriptive_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Convenience function to compute all descriptive statistics
    
    Args:
        df: DataFrame with sensor data
        
    Returns:
        Dictionary with all statistics
    """
    stats = DescriptiveStatistics(df)
    return stats.get_all_statistics()


def print_descriptive_statistics(df: pd.DataFrame):
    """
    Print descriptive statistics report
    
    Args:
        df: DataFrame with sensor data
    """
    stats = DescriptiveStatistics(df)
    print(stats.get_summary_report())


if __name__ == "__main__":
    # Test with sample data
    from analytics.load_data import load_sample_data
    
    print("Loading sample data...")
    df = load_sample_data()
    
    print("\nComputing descriptive statistics...")
    stats = DescriptiveStatistics(df)
    
    # Compute all statistics
    results = stats.get_all_statistics()
    
    # Print summary
    print(stats.get_summary_report())
    
    # Print by sensor type
    if 'by_sensor_type' in results:
        print("\n--- Statistics by Sensor Type ---")
        print(results['by_sensor_type'])