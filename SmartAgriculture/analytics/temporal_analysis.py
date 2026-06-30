"""
Temporal Analysis Module
Analyzes time-based patterns and trends in sensor data
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TemporalAnalysis:
    """Performs temporal analysis on sensor data"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with DataFrame
        
        Args:
            df: DataFrame with sensor data
        """
        self.df = df.copy()
        self.temporal_results = {}
        
        # Ensure timestamp is datetime
        if 'timestamp' in self.df.columns:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df = self.df.sort_values('timestamp')
        
    def extract_time_features(self) -> pd.DataFrame:
        """
        Extract time-based features from timestamp
        
        Returns:
            DataFrame with added time features
        """
        try:
            if 'timestamp' not in self.df.columns:
                logger.error("timestamp column not found")
                return self.df
            
            df = self.df.copy()
            
            # Basic time features
            df['hour'] = df['timestamp'].dt.hour
            df['day'] = df['timestamp'].dt.day
            df['day_of_week'] = df['timestamp'].dt.dayofweek  # Monday=0, Sunday=6
            df['day_name'] = df['timestamp'].dt.day_name()
            df['month'] = df['timestamp'].dt.month
            df['month_name'] = df['timestamp'].dt.month_name()
            df['year'] = df['timestamp'].dt.year
            df['quarter'] = df['timestamp'].dt.quarter
            df['week_of_year'] = df['timestamp'].dt.isocalendar().week
            
            # Derived features
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            df['is_morning'] = ((df['hour'] >= 6) & (df['hour'] < 12)).astype(int)
            df['is_afternoon'] = ((df['hour'] >= 12) & (df['hour'] < 18)).astype(int)
            df['is_evening'] = ((df['hour'] >= 18) & (df['hour'] < 22)).astype(int)
            df['is_night'] = ((df['hour'] >= 22) | (df['hour'] < 6)).astype(int)
            
            # Season (Northern hemisphere)
            df['season'] = df['month'].apply(self._get_season)
            
            # Time of day categories
            df['time_of_day'] = pd.cut(
                df['hour'],
                bins=[0, 6, 12, 18, 22, 24],
                labels=['Night', 'Morning', 'Afternoon', 'Evening', 'Night'],
                include_lowest=True
            )
            
            self.df = df
            self.temporal_results['time_features'] = df
            
            logger.info("✓ Extracted time features")
            return df
            
        except Exception as e:
            logger.error(f"Failed to extract time features: {e}")
            return self.df
    
    def _get_season(self, month: int) -> str:
        """Get season from month (Northern hemisphere)"""
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'
    
    def compute_hourly_statistics(self, column: str = 'value') -> pd.DataFrame:
        """
        Compute statistics by hour of day
        
        Args:
            column: Column to analyze
            
        Returns:
            DataFrame with hourly statistics
        """
        try:
            if 'hour' not in self.df.columns:
                self.extract_time_features()
            
            hourly_stats = self.df.groupby('hour')[column].agg([
                'mean',
                'median',
                'std',
                'min',
                'max',
                'count'
            ]).round(4)
            
            hourly_stats.columns = ['Mean', 'Median', 'Std', 'Min', 'Max', 'Count']
            
            self.temporal_results['hourly'] = hourly_stats
            logger.info("✓ Computed hourly statistics")
            
            return hourly_stats
            
        except Exception as e:
            logger.error(f"Failed to compute hourly statistics: {e}")
            return pd.DataFrame()
    
    def compute_daily_statistics(self, column: str = 'value') -> pd.DataFrame:
        """
        Compute statistics by day of week
        
        Args:
            column: Column to analyze
            
        Returns:
            DataFrame with daily statistics
        """
        try:
            if 'day_of_week' not in self.df.columns:
                self.extract_time_features()
            
            daily_stats = self.df.groupby('day_of_week')[column].agg([
                'mean',
                'median',
                'std',
                'min',
                'max',
                'count'
            ]).round(4)
            
            daily_stats.columns = ['Mean', 'Median', 'Std', 'Min', 'Max', 'Count']
            daily_stats.index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                                'Friday', 'Saturday', 'Sunday']
            
            self.temporal_results['daily'] = daily_stats
            logger.info("✓ Computed daily statistics")
            
            return daily_stats
            
        except Exception as e:
            logger.error(f"Failed to compute daily statistics: {e}")
            return pd.DataFrame()
    
    def compute_monthly_statistics(self, column: str = 'value') -> pd.DataFrame:
        """
        Compute statistics by month
        
        Args:
            column: Column to analyze
            
        Returns:
            DataFrame with monthly statistics
        """
        try:
            if 'month' not in self.df.columns:
                self.extract_time_features()
            
            monthly_stats = self.df.groupby('month')[column].agg([
                'mean',
                'median',
                'std',
                'min',
                'max',
                'count'
            ]).round(4)
            
            monthly_stats.columns = ['Mean', 'Median', 'Std', 'Min', 'Max', 'Count']
            monthly_stats.index = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            self.temporal_results['monthly'] = monthly_stats
            logger.info("✓ Computed monthly statistics")
            
            return monthly_stats
            
        except Exception as e:
            logger.error(f"Failed to compute monthly statistics: {e}")
            return pd.DataFrame()
    
    def compute_seasonal_statistics(self, column: str = 'value') -> pd.DataFrame:
        """
        Compute statistics by season
        
        Args:
            column: Column to analyze
            
        Returns:
            DataFrame with seasonal statistics
        """
        try:
            if 'season' not in self.df.columns:
                self.extract_time_features()
            
            seasonal_stats = self.df.groupby('season')[column].agg([
                'mean',
                'median',
                'std',
                'min',
                'max',
                'count'
            ]).round(4)
            
            seasonal_stats.columns = ['Mean', 'Median', 'Std', 'Min', 'Max', 'Count']
            
            # Reorder seasons
            season_order = ['Winter', 'Spring', 'Summer', 'Fall']
            seasonal_stats = seasonal_stats.reindex([s for s in season_order if s in seasonal_stats.index])
            
            self.temporal_results['seasonal'] = seasonal_stats
            logger.info("✓ Computed seasonal statistics")
            
            return seasonal_stats
            
        except Exception as e:
            logger.error(f"Failed to compute seasonal statistics: {e}")
            return pd.DataFrame()
    
    def detect_trends(self, sensor_id: str, column: str = 'value') -> Dict[str, Any]:
        """
        Detect trends in time series data
        
        Args:
            sensor_id: Sensor ID
            column: Column to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        try:
            if 'sensor_id' not in self.df.columns:
                return {}
            
            # Get sensor data
            sensor_data = self.df[self.df['sensor_id'] == sensor_id].copy()
            sensor_data = sensor_data.sort_values('timestamp')
            
            if len(sensor_data) < 10:
                logger.warning(f"Not enough data for trend analysis")
                return {}
            
            # Create time index
            sensor_data['time_index'] = range(len(sensor_data))
            
            # Linear regression for trend
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                sensor_data['time_index'],
                sensor_data[column].dropna()
            )
            
            trend_info = {
                'sensor_id': sensor_id,
                'slope': float(slope),
                'intercept': float(intercept),
                'r_squared': float(r_value ** 2),
                'p_value': float(p_value),
                'std_err': float(std_err),
                'trend_direction': 'Increasing' if slope > 0 else 'Decreasing' if slope < 0 else 'Stable',
                'trend_significant': p_value < 0.05,
                'data_points': len(sensor_data)
            }
            
            self.temporal_results[f'trend_{sensor_id}'] = trend_info
            logger.info(f"✓ Detected trend for {sensor_id}: {trend_info['trend_direction']}")
            
            return trend_info
            
        except Exception as e:
            logger.error(f"Failed to detect trends: {e}")
            return {}
    
    def detect_seasonality(self, sensor_id: str, column: str = 'value',
                          period: int = 24) -> Dict[str, Any]:
        """
        Detect seasonality in time series
        
        Args:
            sensor_id: Sensor ID
            column: Column to analyze
            period: Seasonality period (e.g., 24 for hourly, 7 for weekly)
            
        Returns:
            Dictionary with seasonality analysis
        """
        try:
            if 'sensor_id' not in self.df.columns:
                return {}
            
            # Get sensor data
            sensor_data = self.df[self.df['sensor_id'] == sensor_id].copy()
            sensor_data = sensor_data.sort_values('timestamp')
            
            if len(sensor_data) < period * 2:
                logger.warning(f"Not enough data for seasonality detection")
                return {}
            
            # Set timestamp as index
            sensor_data = sensor_data.set_index('timestamp')
            series = sensor_data[column].dropna()
            
            # Check stationarity
            adf_result = adfuller(series)
            
            seasonality_info = {
                'sensor_id': sensor_id,
                'period': period,
                'adf_statistic': float(adf_result[0]),
                'adf_p_value': float(adf_result[1]),
                'stationary': adf_result[1] < 0.05,
                'data_points': len(series)
            }
            
            # Try seasonal decomposition if enough data
            try:
                if len(series) >= period * 2:
                    decomposition = seasonal_decompose(series, model='additive', period=period)
                    
                    seasonality_info['trend_strength'] = float(np.std(decomposition.trend.dropna()) / np.std(series))
                    seasonality_info['seasonal_strength'] = float(np.std(decomposition.seasonal) / np.std(series))
                    seasonality_info['residual_strength'] = float(np.std(decomposition.resid.dropna()) / np.std(series))
            except:
                logger.warning("Could not perform seasonal decomposition")
            
            self.temporal_results[f'seasonality_{sensor_id}'] = seasonality_info
            logger.info(f"✓ Analyzed seasonality for {sensor_id}")
            
            return seasonality_info
            
        except Exception as e:
            logger.error(f"Failed to detect seasonality: {e}")
            return {}
    
    def compute_daily_averages(self, column: str = 'value') -> pd.DataFrame:
        """
        Compute daily averages
        
        Args:
            column: Column to analyze
            
        Returns:
            DataFrame with daily averages
        """
        try:
            if 'timestamp' not in self.df.columns:
                return pd.DataFrame()
            
            # Group by date
            daily_avg = self.df.groupby(self.df['timestamp'].dt.date)[column].mean()
            
            daily_df = pd.DataFrame({
                'date': daily_avg.index,
                'daily_average': daily_avg.values
            })
            
            self.temporal_results['daily_averages'] = daily_df
            logger.info("✓ Computed daily averages")
            
            return daily_df
            
        except Exception as e:
            logger.error(f"Failed to compute daily averages: {e}")
            return pd.DataFrame()
    
    def compute_hourly_averages(self, column: str = 'value') -> pd.DataFrame:
        """
        Compute hourly averages
        
        Args:
            column: Column to analyze
            
        Returns:
            DataFrame with hourly averages
        """
        try:
            if 'timestamp' not in self.df.columns:
                return pd.DataFrame()
            
            # Group by hour
            hourly_avg = self.df.groupby(self.df['timestamp'].dt.hour)[column].mean()
            
            hourly_df = pd.DataFrame({
                'hour': hourly_avg.index,
                'hourly_average': hourly_avg.values
            })
            
            self.temporal_results['hourly_averages'] = hourly_df
            logger.info("✓ Computed hourly averages")
            
            return hourly_df
            
        except Exception as e:
            logger.error(f"Failed to compute hourly averages: {e}")
            return pd.DataFrame()
    
    def detect_anomalies_temporal(self, column: str = 'value', 
                                  window: int = 24,
                                  threshold: float = 3.0) -> pd.DataFrame:
        """
        Detect temporal anomalies using rolling statistics
        
        Args:
            column: Column to analyze
            window: Rolling window size
            threshold: Z-score threshold
            
        Returns:
            DataFrame with anomalies
        """
        try:
            if 'timestamp' not in self.df.columns:
                return pd.DataFrame()
            
            df = self.df.copy()
            
            # Compute rolling statistics
            df['rolling_mean'] = df[column].rolling(window=window, min_periods=1).mean()
            df['rolling_std'] = df[column].rolling(window=window, min_periods=1).std()
            
            # Compute Z-score
            df['z_score'] = np.abs((df[column] - df['rolling_mean']) / df['rolling_std'])
            
            # Identify anomalies
            anomalies = df[df['z_score'] > threshold].copy()
            
            self.temporal_results['temporal_anomalies'] = anomalies
            logger.info(f"✓ Detected {len(anomalies)} temporal anomalies")
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect temporal anomalies: {e}")
            return pd.DataFrame()
    
    def plot_time_series(self, sensor_id: str = None, column: str = 'value',
                        figsize: Tuple[int, int] = (15, 6),
                        save_path: Optional[str] = None):
        """
        Plot time series
        
        Args:
            sensor_id: Optional sensor ID to filter
            column: Column to plot
            figsize: Figure size
            save_path: Optional path to save figure
        """
        try:
            if 'timestamp' not in self.df.columns:
                logger.error("timestamp column not found")
                return
            
            df = self.df.copy()
            
            if sensor_id:
                df = df[df['sensor_id'] == sensor_id]
            
            plt.figure(figsize=figsize)
            plt.plot(df['timestamp'], df[column], linewidth=1)
            
            title = f"Time Series: {column}"
            if sensor_id:
                title += f" (Sensor: {sensor_id})"
            
            plt.title(title, fontsize=14, fontweight='bold')
            plt.xlabel('Timestamp', fontsize=12)
            plt.ylabel(column, fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"✓ Saved time series plot to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Failed to plot time series: {e}")
    
    def plot_hourly_pattern(self, column: str = 'value',
                           figsize: Tuple[int, int] = (12, 6),
                           save_path: Optional[str] = None):
        """
        Plot hourly pattern
        
        Args:
            column: Column to plot
            figsize: Figure size
            save_path: Optional path to save figure
        """
        try:
            if 'hour' not in self.df.columns:
                self.extract_time_features()
            
            hourly = self.compute_hourly_statistics(column)
            
            if hourly.empty:
                return
            
            plt.figure(figsize=figsize)
            plt.plot(hourly.index, hourly['Mean'], marker='o', linewidth=2)
            plt.fill_between(hourly.index, 
                           hourly['Mean'] - hourly['Std'], 
                           hourly['Mean'] + hourly['Std'], 
                           alpha=0.3)
            
            plt.title('Hourly Pattern', fontsize=14, fontweight='bold')
            plt.xlabel('Hour of Day', fontsize=12)
            plt.ylabel(f'Average {column}', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xticks(range(0, 24))
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"✓ Saved hourly pattern plot to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Failed to plot hourly pattern: {e}")
    
    def plot_daily_pattern(self, column: str = 'value',
                          figsize: Tuple[int, int] = (12, 6),
                          save_path: Optional[str] = None):
        """
        Plot daily pattern
        
        Args:
            column: Column to plot
            figsize: Figure size
            save_path: Optional path to save figure
        """
        try:
            if 'day_of_week' not in self.df.columns:
                self.extract_time_features()
            
            daily = self.compute_daily_statistics(column)
            
            if daily.empty:
                return
            
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                   'Friday', 'Saturday', 'Sunday']
            
            plt.figure(figsize=figsize)
            plt.plot(days, daily['Mean'], marker='o', linewidth=2)
            plt.fill_between(range(len(days)), 
                           daily['Mean'] - daily['Std'], 
                           daily['Mean'] + daily['Std'], 
                           alpha=0.3)
            
            plt.title('Daily Pattern', fontsize=14, fontweight='bold')
            plt.xlabel('Day of Week', fontsize=12)
            plt.ylabel(f'Average {column}', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xticks(range(len(days)), days, rotation=45)
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"✓ Saved daily pattern plot to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Failed to plot daily pattern: {e}")
    
    def get_temporal_summary(self) -> str:
        """
        Generate temporal analysis summary
        
        Returns:
            Formatted summary report
        """
        try:
            report = []
            report.append("=" * 70)
            report.append("TEMPORAL ANALYSIS REPORT")
            report.append("=" * 70)
            
            # Time range
            if 'timestamp' in self.df.columns:
                report.append(f"\nTime Range:")
                report.append(f"  Start: {self.df['timestamp'].min()}")
                report.append(f"  End: {self.df['timestamp'].max()}")
                report.append(f"  Duration: {self.df['timestamp'].max() - self.df['timestamp'].min()}")
            
            # Hourly patterns
            if 'hourly' in self.temporal_results:
                report.append(f"\n--- Hourly Patterns ---")
                hourly = self.temporal_results['hourly']
                peak_hour = hourly['Mean'].idxmax()
                low_hour = hourly['Mean'].idxmin()
                report.append(f"  Peak hour: {peak_hour}:00 (avg: {hourly.loc[peak_hour, 'Mean']:.2f})")
                report.append(f"  Lowest hour: {low_hour}:00 (avg: {hourly.loc[low_hour, 'Mean']:.2f})")
            
            # Daily patterns
            if 'daily' in self.temporal_results:
                report.append(f"\n--- Daily Patterns ---")
                daily = self.temporal_results['daily']
                peak_day = daily['Mean'].idxmax()
                low_day = daily['Mean'].idxmin()
                report.append(f"  Peak day: {peak_day} (avg: {daily.loc[peak_day, 'Mean']:.2f})")
                report.append(f"  Lowest day: {low_day} (avg: {daily.loc[low_day, 'Mean']:.2f})")
            
            # Trends
            report.append(f"\n--- Trends ---")
            trend_keys = [k for k in self.temporal_results.keys() if k.startswith('trend_')]
            if trend_keys:
                for key in trend_keys[:5]:  # Show first 5
                    trend = self.temporal_results[key]
                    report.append(f"  {trend['sensor_id']}: {trend['trend_direction']} "
                                f"(R²={trend['r_squared']:.3f}, p={trend['p_value']:.3f})")
            else:
                report.append("  No trends detected")
            
            report.append("\n" + "=" * 70)
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Failed to generate temporal summary: {e}")
            return "Error generating report"


def analyze_temporal_patterns(df: pd.DataFrame, sensor_id: str = None) -> Dict[str, Any]:
    """
    Convenience function to perform temporal analysis
    
    Args:
        df: DataFrame with sensor data
        sensor_id: Optional specific sensor ID
        
    Returns:
        Dictionary with temporal analysis results
    """
    analysis = TemporalAnalysis(df)
    
    # Extract time features
    analysis.extract_time_features()
    
    # Compute statistics
    analysis.compute_hourly_statistics()
    analysis.compute_daily_statistics()
    analysis.compute_monthly_statistics()
    analysis.compute_seasonal_statistics()
    
    # Detect trends for specific sensor or all
    if sensor_id:
        analysis.detect_trends(sensor_id)
    elif 'sensor_id' in df.columns:
        for sid in df['sensor_id'].unique()[:5]:  # First 5 sensors
            analysis.detect_trends(sid)
    
    return analysis.temporal_results


def print_temporal_summary(df: pd.DataFrame):
    """
    Print temporal analysis summary
    
    Args:
        df: DataFrame with sensor data
    """
    analysis = TemporalAnalysis(df)
    analysis.extract_time_features()
    analysis.compute_hourly_statistics()
    analysis.compute_daily_statistics()
    print(analysis.get_temporal_summary())


if __name__ == "__main__":
    # Test with sample data
    from analytics.load_data import load_sample_data
    
    print("Loading sample data...")
    df = load_sample_data()
    
    print("\nPerforming temporal analysis...")
    analysis = TemporalAnalysis(df)
    
    # Extract features
    df_with_features = analysis.extract_time_features()
    print("\nTime features added:")
    print(df_with_features[['timestamp', 'hour', 'day_of_week', 'month', 'season']].head())
    
    # Compute statistics
    hourly = analysis.compute_hourly_statistics()
    print("\nHourly Statistics:")
    print(hourly)
    
    # Plot
    analysis.plot_hourly_pattern(save_path='results/hourly_pattern.png')
    analysis.plot_daily_pattern(save_path='results/daily_pattern.png')