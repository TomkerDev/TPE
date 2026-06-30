"""
Dashboard Data Module
Prepares data for dashboard visualization and monitoring
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DashboardData:
    """Prepares data for dashboard visualization"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with DataFrame
        
        Args:
            df: DataFrame with sensor data
        """
        self.df = df.copy()
        self.dashboard_data = {}
        
    def prepare_kpi_data(self) -> Dict[str, Any]:
        """
        Prepare Key Performance Indicators data
        
        Returns:
            Dictionary with KPI data
        """
        try:
            kpi_data = {
                'total_sensors': self.df['sensor_id'].nunique() if 'sensor_id' in self.df.columns else 0,
                'total_readings': len(self.df),
                'sensor_types': self.df['sensor_type'].nunique() if 'sensor_type' in self.df.columns else 0,
                'date_range': {
                    'start': str(self.df['timestamp'].min()) if 'timestamp' in self.df.columns else None,
                    'end': str(self.df['timestamp'].max()) if 'timestamp' in self.df.columns else None
                }
            }
            
            # Data quality metrics
            if 'quality' in self.df.columns:
                kpi_data['avg_quality'] = float(self.df['quality'].mean())
                kpi_data['low_quality_count'] = int(len(self.df[self.df['quality'] < 70]))
            
            # Outlier metrics
            if 'is_outlier' in self.df.columns:
                kpi_data['outlier_count'] = int(self.df['is_outlier'].sum())
                kpi_data['outlier_percentage'] = float(self.df['is_outlier'].mean() * 100)
            
            self.dashboard_data['kpi'] = kpi_data
            logger.info("✓ Prepared KPI data")
            
            return kpi_data
            
        except Exception as e:
            logger.error(f"Failed to prepare KPI data: {e}")
            return {}
    
    def prepare_sensor_summary(self) -> pd.DataFrame:
        """
        Prepare sensor summary for dashboard
        
        Returns:
            DataFrame with sensor summaries
        """
        try:
            if 'sensor_id' not in self.df.columns:
                return pd.DataFrame()
            
            summary = self.df.groupby('sensor_id').agg({
                'sensor_type': 'first',
                'value': ['count', 'mean', 'std', 'min', 'max'],
                'timestamp': ['min', 'max']
            }).round(4)
            
            # Flatten column names
            summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
            summary = summary.reset_index()
            
            # Rename columns
            summary.columns = [
                'sensor_id',
                'sensor_type',
                'reading_count',
                'avg_value',
                'std_value',
                'min_value',
                'max_value',
                'first_reading',
                'last_reading'
            ]
            
            # Add quality if available
            if 'quality' in self.df.columns:
                quality = self.df.groupby('sensor_id')['quality'].mean().reset_index()
                quality.columns = ['sensor_id', 'avg_quality']
                summary = summary.merge(quality, on='sensor_id')
            
            # Add outlier count if available
            if 'is_outlier' in self.df.columns:
                outliers = self.df.groupby('sensor_id')['is_outlier'].sum().reset_index()
                outliers.columns = ['sensor_id', 'outlier_count']
                summary = summary.merge(outliers, on='sensor_id')
            
            self.dashboard_data['sensor_summary'] = summary
            logger.info("✓ Prepared sensor summary")
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to prepare sensor summary: {e}")
            return pd.DataFrame()
    
    def prepare_time_series_data(self, sensor_id: str = None, 
                                 sensor_type: str = None,
                                 hours: int = 24) -> pd.DataFrame:
        """
        Prepare time series data for charts
        
        Args:
            sensor_id: Optional sensor ID filter
            sensor_type: Optional sensor type filter
            hours: Number of hours to include
            
        Returns:
            DataFrame with time series data
        """
        try:
            if 'timestamp' not in self.df.columns:
                return pd.DataFrame()
            
            df = self.df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter by time
            cutoff_time = datetime.now() - timedelta(hours=hours)
            df = df[df['timestamp'] >= cutoff_time]
            
            # Filter by sensor
            if sensor_id:
                df = df[df['sensor_id'] == sensor_id]
            elif sensor_type:
                df = df[df['sensor_type'] == sensor_type]
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            # Resample to regular intervals
            if not df.empty:
                df = df.set_index('timestamp')
                df = df.resample('1min').mean(numeric_only=True)
                df = df.reset_index()
            
            self.dashboard_data['time_series'] = df
            logger.info(f"✓ Prepared time series data ({len(df)} points)")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to prepare time series data: {e}")
            return pd.DataFrame()
    
    def prepare_distribution_data(self) -> Dict[str, pd.DataFrame]:
        """
        Prepare distribution data by sensor type
        
        Returns:
            Dictionary of DataFrames by sensor type
        """
        try:
            if 'sensor_type' not in self.df.columns or 'value' not in self.df.columns:
                return {}
            
            distribution_data = {}
            
            for sensor_type in self.df['sensor_type'].unique():
                subset = self.df[self.df['sensor_type'] == sensor_type]['value'].dropna()
                
                # Compute histogram
                counts, bins = np.histogram(subset, bins=30)
                
                distribution_data[sensor_type] = pd.DataFrame({
                    'bin_center': (bins[:-1] + bins[1:]) / 2,
                    'count': counts,
                    'sensor_type': sensor_type
                })
            
            self.dashboard_data['distribution'] = distribution_data
            logger.info(f"✓ Prepared distribution data for {len(distribution_data)} sensor types")
            
            return distribution_data
            
        except Exception as e:
            logger.error(f"Failed to prepare distribution data: {e}")
            return {}
    
    def prepare_alerts_data(self, quality_threshold: float = 70.0,
                           outlier_threshold: float = 10.0) -> pd.DataFrame:
        """
        Prepare alerts data for dashboard
        
        Args:
            quality_threshold: Quality threshold
            outlier_threshold: Outlier percentage threshold
            
        Returns:
            DataFrame with alerts
        """
        try:
            if 'sensor_id' not in self.df.columns:
                return pd.DataFrame()
            
            alerts = []
            
            # Group by sensor
            for sensor_id in self.df['sensor_id'].unique():
                sensor_data = self.df[self.df['sensor_id'] == sensor_id]
                issues = []
                
                # Check quality
                if 'quality' in sensor_data.columns:
                    avg_quality = sensor_data['quality'].mean()
                    if avg_quality < quality_threshold:
                        issues.append({
                            'type': 'quality',
                            'severity': 'high' if avg_quality < 50 else 'medium',
                            'message': f'Low quality: {avg_quality:.1f}%',
                            'sensor_id': sensor_id,
                            'sensor_type': sensor_data['sensor_type'].iloc[0] if 'sensor_type' in sensor_data.columns else 'unknown'
                        })
                
                # Check outliers
                if 'is_outlier' in sensor_data.columns:
                    outlier_pct = sensor_data['is_outlier'].mean() * 100
                    if outlier_pct > outlier_threshold:
                        issues.append({
                            'type': 'outliers',
                            'severity': 'medium',
                            'message': f'High outliers: {outlier_pct:.1f}%',
                            'sensor_id': sensor_id,
                            'sensor_type': sensor_data['sensor_type'].iloc[0] if 'sensor_type' in sensor_data.columns else 'unknown'
                        })
                
                alerts.extend(issues)
            
            if not alerts:
                return pd.DataFrame()
            
            alerts_df = pd.DataFrame(alerts)
            
            self.dashboard_data['alerts'] = alerts_df
            logger.info(f"✓ Prepared {len(alerts_df)} alerts")
            
            return alerts_df
            
        except Exception as e:
            logger.error(f"Failed to prepare alerts data: {e}")
            return pd.DataFrame()
    
    def prepare_statistics_by_type(self) -> pd.DataFrame:
        """
        Prepare statistics grouped by sensor type
        
        Returns:
            DataFrame with statistics by sensor type
        """
        try:
            if 'sensor_type' not in self.df.columns or 'value' not in self.df.columns:
                return pd.DataFrame()
            
            stats = self.df.groupby('sensor_type').agg({
                'value': ['count', 'mean', 'median', 'std', 'min', 'max'],
                'sensor_id': 'nunique'
            }).round(4)
            
            # Flatten column names
            stats.columns = ['_'.join(col).strip() for col in stats.columns.values]
            stats = stats.reset_index()
            
            # Rename columns
            stats.columns = [
                'sensor_type',
                'reading_count',
                'mean_value',
                'median_value',
                'std_value',
                'min_value',
                'max_value',
                'sensor_count'
            ]
            
            self.dashboard_data['stats_by_type'] = stats
            logger.info("✓ Prepared statistics by type")
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to prepare statistics by type: {e}")
            return pd.DataFrame()
    
    def prepare_hourly_data(self) -> pd.DataFrame:
        """
        Prepare hourly aggregated data
        
        Returns:
            DataFrame with hourly data
        """
        try:
            if 'timestamp' not in self.df.columns:
                return pd.DataFrame()
            
            df = self.df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            
            hourly = df.groupby('hour').agg({
                'value': ['mean', 'std', 'count'],
                'sensor_id': 'nunique'
            }).round(4)
            
            # Flatten column names
            hourly.columns = ['_'.join(col).strip() for col in hourly.columns.values]
            hourly = hourly.reset_index()
            
            # Rename columns
            hourly.columns = [
                'hour',
                'avg_value',
                'std_value',
                'reading_count',
                'active_sensors'
            ]
            
            self.dashboard_data['hourly'] = hourly
            logger.info("✓ Prepared hourly data")
            
            return hourly
            
        except Exception as e:
            logger.error(f"Failed to prepare hourly data: {e}")
            return pd.DataFrame()
    
    def prepare_daily_data(self) -> pd.DataFrame:
        """
        Prepare daily aggregated data
        
        Returns:
            DataFrame with daily data
        """
        try:
            if 'timestamp' not in self.df.columns:
                return pd.DataFrame()
            
            df = self.df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            
            daily = df.groupby('date').agg({
                'value': ['mean', 'std', 'min', 'max', 'count'],
                'sensor_id': 'nunique'
            }).round(4)
            
            # Flatten column names
            daily.columns = ['_'.join(col).strip() for col in daily.columns.values]
            daily = daily.reset_index()
            
            # Rename columns
            daily.columns = [
                'date',
                'avg_value',
                'std_value',
                'min_value',
                'max_value',
                'reading_count',
                'active_sensors'
            ]
            
            self.dashboard_data['daily'] = daily
            logger.info("✓ Prepared daily data")
            
            return daily
            
        except Exception as e:
            logger.error(f"Failed to prepare daily data: {e}")
            return pd.DataFrame()
    
    def prepare_all_dashboard_data(self) -> Dict[str, Any]:
        """
        Prepare all dashboard data
        
        Returns:
            Dictionary with all dashboard data
        """
        try:
            logger.info("Preparing all dashboard data...")
            
            self.prepare_kpi_data()
            self.prepare_sensor_summary()
            self.prepare_distribution_data()
            self.prepare_alerts_data()
            self.prepare_statistics_by_type()
            self.prepare_hourly_data()
            self.prepare_daily_data()
            
            logger.info("✓ All dashboard data prepared")
            
            return self.dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to prepare dashboard data: {e}")
            return {}
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all prepared dashboard data"""
        if not self.dashboard_data:
            self.prepare_all_dashboard_data()
        return self.dashboard_data
    
    def to_json(self) -> str:
        """
        Convert dashboard data to JSON
        
        Returns:
            JSON string
        """
        try:
            import json
            
            # Convert DataFrames to dict
            json_data = {}
            for key, value in self.dashboard_data.items():
                if isinstance(value, pd.DataFrame):
                    json_data[key] = value.to_dict(orient='records')
                else:
                    json_data[key] = value
            
            return json.dumps(json_data, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Failed to convert to JSON: {e}")
            return "{}"


def prepare_dashboard_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Convenience function to prepare all dashboard data
    
    Args:
        df: DataFrame with sensor data
        
    Returns:
        Dictionary with all dashboard data
    """
    dashboard = DashboardData(df)
    return dashboard.prepare_all_dashboard_data()


if __name__ == "__main__":
    # Test with sample data
    from analytics.load_data import load_sample_data
    
    print("Loading sample data...")
    df = load_sample_data()
    
    print("\nPreparing dashboard data...")
    dashboard = DashboardData(df)
    
    # Prepare all data
    data = dashboard.prepare_all_dashboard_data()
    
    # Print KPI
    if 'kpi' in data:
        print("\nKPI Data:")
        for key, value in data['kpi'].items():
            print(f"  {key}: {value}")
    
    # Print sensor summary
    if 'sensor_summary' in data:
        print(f"\nSensor Summary ({len(data['sensor_summary'])} sensors):")
        print(data['sensor_summary'].head())
    
    # Export to JSON
    json_data = dashboard.to_json()
    print(f"\nJSON export length: {len(json_data)} characters")