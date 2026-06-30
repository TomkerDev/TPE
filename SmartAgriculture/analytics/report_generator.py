"""
Report Generator Module
Generates comprehensive analysis reports in various formats
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates analysis reports"""
    
    def __init__(self, df: pd.DataFrame, output_dir: str = 'reports'):
        """
        Initialize report generator
        
        Args:
            df: DataFrame with sensor data
            output_dir: Directory to save reports
        """
        self.df = df.copy()
        self.output_dir = output_dir
        self.report_data = {}
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_summary_report(self) -> str:
        """
        Generate summary report
        
        Returns:
            Formatted summary report
        """
        try:
            report = []
            report.append("=" * 80)
            report.append("SMART AGRICULTURE - EXPLORATORY DATA ANALYSIS REPORT")
            report.append("=" * 80)
            report.append(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Dataset overview
            report.append("\n" + "=" * 80)
            report.append("1. DATASET OVERVIEW")
            report.append("=" * 80)
            
            report.append(f"\nTotal Observations: {len(self.df):,}")
            
            if 'sensor_id' in self.df.columns:
                report.append(f"Total Sensors: {self.df['sensor_id'].nunique()}")
            
            if 'sensor_type' in self.df.columns:
                report.append(f"Sensor Types: {self.df['sensor_type'].nunique()}")
                report.append(f"Types: {', '.join(self.df['sensor_type'].unique())}")
            
            if 'timestamp' in self.df.columns:
                report.append(f"\nTime Range:")
                report.append(f"  Start: {self.df['timestamp'].min()}")
                report.append(f"  End: {self.df['timestamp'].max()}")
                report.append(f"  Duration: {self.df['timestamp'].max() - self.df['timestamp'].min()}")
            
            # Data quality
            report.append("\n" + "=" * 80)
            report.append("2. DATA QUALITY")
            report.append("=" * 80)
            
            missing_values = self.df.isnull().sum()
            report.append(f"\nMissing Values:")
            for col, count in missing_values.items():
                if count > 0:
                    pct = (count / len(self.df)) * 100
                    report.append(f"  {col}: {count} ({pct:.2f}%)")
            
            if 'quality' in self.df.columns:
                report.append(f"\nQuality Score:")
                report.append(f"  Mean: {self.df['quality'].mean():.2f}")
                report.append(f"  Min: {self.df['quality'].min():.2f}")
                report.append(f"  Max: {self.df['quality'].max():.2f}")
            
            if 'is_outlier' in self.df.columns:
                outlier_count = self.df['is_outlier'].sum()
                outlier_pct = (outlier_count / len(self.df)) * 100
                report.append(f"\nOutliers:")
                report.append(f"  Count: {outlier_count}")
                report.append(f"  Percentage: {outlier_pct:.2f}%")
            
            # Descriptive statistics
            report.append("\n" + "=" * 80)
            report.append("3. DESCRIPTIVE STATISTICS")
            report.append("=" * 80)
            
            if 'value' in self.df.columns:
                report.append(f"\nOverall Value Statistics:")
                report.append(f"  Mean: {self.df['value'].mean():.4f}")
                report.append(f"  Median: {self.df['value'].median():.4f}")
                report.append(f"  Std Dev: {self.df['value'].std():.4f}")
                report.append(f"  Min: {self.df['value'].min():.4f}")
                report.append(f"  Max: {self.df['value'].max():.4f}")
            
            if 'sensor_type' in self.df.columns and 'value' in self.df.columns:
                report.append(f"\nBy Sensor Type:")
                by_type = self.df.groupby('sensor_type')['value'].agg(['count', 'mean', 'std', 'min', 'max'])
                report.append(by_type.to_string())
            
            # Sensor analysis
            report.append("\n" + "=" * 80)
            report.append("4. SENSOR ANALYSIS")
            report.append("=" * 80)
            
            if 'sensor_id' in self.df.columns:
                sensor_stats = self.df.groupby('sensor_id').agg({
                    'value': 'count',
                    'sensor_type': 'first'
                }).reset_index()
                
                report.append(f"\nSensor Statistics:")
                report.append(f"  Total Sensors: {len(sensor_stats)}")
                report.append(f"  Avg Readings per Sensor: {sensor_stats['value'].mean():.2f}")
                report.append(f"  Min Readings: {sensor_stats['value'].min()}")
                report.append(f"  Max Readings: {sensor_stats['value'].max()}")
            
            # Temporal patterns
            report.append("\n" + "=" * 80)
            report.append("5. TEMPORAL PATTERNS")
            report.append("=" * 80)
            
            if 'timestamp' in self.df.columns:
                df_time = self.df.copy()
                df_time['timestamp'] = pd.to_datetime(df_time['timestamp'])
                df_time['hour'] = df_time['timestamp'].dt.hour
                
                hourly_avg = df_time.groupby('hour')['value'].mean()
                peak_hour = hourly_avg.idxmax()
                low_hour = hourly_avg.idxmin()
                
                report.append(f"\nHourly Patterns:")
                report.append(f"  Peak Hour: {peak_hour}:00 (avg: {hourly_avg[peak_hour]:.4f})")
                report.append(f"  Lowest Hour: {low_hour}:00 (avg: {hourly_avg[low_hour]:.4f})")
            
            # Correlation insights
            report.append("\n" + "=" * 80)
            report.append("6. CORRELATION INSIGHTS")
            report.append("=" * 80)
            
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) > 1:
                corr_matrix = self.df[numeric_cols].corr()
                
                # Find high correlations
                high_corr = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i + 1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) > 0.7:
                            high_corr.append({
                                'var1': corr_matrix.columns[i],
                                'var2': corr_matrix.columns[j],
                                'corr': corr_val
                            })
                
                if high_corr:
                    report.append(f"\nHigh Correlations (|r| > 0.7):")
                    for corr in high_corr[:5]:
                        report.append(f"  {corr['var1']} <-> {corr['var2']}: r = {corr['corr']:.3f}")
                else:
                    report.append(f"\nNo high correlations found (threshold: 0.7)")
            
            # Recommendations
            report.append("\n" + "=" * 80)
            report.append("7. RECOMMENDATIONS")
            report.append("=" * 80)
            
            recommendations = []
            
            # Check data quality
            if 'quality' in self.df.columns:
                low_quality_pct = (self.df['quality'] < 70).mean() * 100
                if low_quality_pct > 10:
                    recommendations.append(f"• Investigate {low_quality_pct:.1f}% low-quality readings")
            
            # Check outliers
            if 'is_outlier' in self.df.columns:
                outlier_pct = self.df['is_outlier'].mean() * 100
                if outlier_pct > 10:
                    recommendations.append(f"• Review {outlier_pct:.1f}% outlier readings")
            
            # Check sensor coverage
            if 'sensor_id' in self.df.columns:
                sensor_counts = self.df.groupby('sensor_id').size()
                low_data_sensors = (sensor_counts < 100).sum()
                if low_data_sensors > 0:
                    recommendations.append(f"• {low_data_sensors} sensors have insufficient data (<100 readings)")
            
            if recommendations:
                for rec in recommendations:
                    report.append(rec)
            else:
                report.append("✓ No critical issues detected")
            
            report.append("\n" + "=" * 80)
            report.append("END OF REPORT")
            report.append("=" * 80)
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Failed to generate summary report: {e}")
            return f"Error generating report: {e}"
    
    def generate_detailed_report(self) -> Dict[str, Any]:
        """
        Generate detailed report with all analysis results
        
        Returns:
            Dictionary with complete report data
        """
        try:
            report = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_observations': len(self.df),
                    'total_sensors': self.df['sensor_id'].nunique() if 'sensor_id' in self.df.columns else 0,
                    'sensor_types': self.df['sensor_type'].unique().tolist() if 'sensor_type' in self.df.columns else []
                },
                'data_quality': self._generate_data_quality_section(),
                'descriptive_statistics': self._generate_descriptive_stats_section(),
                'sensor_analysis': self._generate_sensor_analysis_section(),
                'temporal_analysis': self._generate_temporal_section(),
                'correlations': self._generate_correlation_section()
            }
            
            self.report_data = report
            logger.info("✓ Generated detailed report")
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate detailed report: {e}")
            return {}
    
    def _generate_data_quality_section(self) -> Dict[str, Any]:
        """Generate data quality section"""
        section = {
            'missing_values': {},
            'quality_scores': {},
            'outliers': {}
        }
        
        # Missing values
        missing = self.df.isnull().sum()
        section['missing_values'] = {
            col: {
                'count': int(count),
                'percentage': float((count / len(self.df)) * 100)
            }
            for col, count in missing.items() if count > 0
        }
        
        # Quality scores
        if 'quality' in self.df.columns:
            section['quality_scores'] = {
                'mean': float(self.df['quality'].mean()),
                'min': float(self.df['quality'].min()),
                'max': float(self.df['quality'].max()),
                'low_quality_count': int(len(self.df[self.df['quality'] < 70]))
            }
        
        # Outliers
        if 'is_outlier' in self.df.columns:
            section['outliers'] = {
                'total': int(self.df['is_outlier'].sum()),
                'percentage': float(self.df['is_outlier'].mean() * 100)
            }
        
        return section
    
    def _generate_descriptive_stats_section(self) -> Dict[str, Any]:
        """Generate descriptive statistics section"""
        section = {
            'overall': {},
            'by_sensor_type': {}
        }
        
        # Overall statistics
        if 'value' in self.df.columns:
            section['overall'] = {
                'mean': float(self.df['value'].mean()),
                'median': float(self.df['value'].median()),
                'std': float(self.df['value'].std()),
                'min': float(self.df['value'].min()),
                'max': float(self.df['value'].max()),
                'count': len(self.df)
            }
        
        # By sensor type
        if 'sensor_type' in self.df.columns and 'value' in self.df.columns:
            by_type = self.df.groupby('sensor_type')['value'].agg([
                'count', 'mean', 'median', 'std', 'min', 'max'
            ]).round(4)
            
            section['by_sensor_type'] = by_type.to_dict('index')
        
        return section
    
    def _generate_sensor_analysis_section(self) -> Dict[str, Any]:
        """Generate sensor analysis section"""
        section = {
            'total_sensors': 0,
            'sensors': {}
        }
        
        if 'sensor_id' not in self.df.columns:
            return section
        
        section['total_sensors'] = self.df['sensor_id'].nunique()
        
        # Analyze each sensor
        for sensor_id in self.df['sensor_id'].unique()[:10]:  # Limit to 10 for report
            sensor_data = self.df[self.df['sensor_id'] == sensor_id]
            
            sensor_info = {
                'type': sensor_data['sensor_type'].iloc[0] if 'sensor_type' in sensor_data.columns else 'unknown',
                'total_readings': len(sensor_data),
                'value_stats': {}
            }
            
            if 'value' in sensor_data.columns:
                values = sensor_data['value'].dropna()
                sensor_info['value_stats'] = {
                    'mean': float(values.mean()),
                    'std': float(values.std()),
                    'min': float(values.min()),
                    'max': float(values.max())
                }
            
            section['sensors'][sensor_id] = sensor_info
        
        return section
    
    def _generate_temporal_section(self) -> Dict[str, Any]:
        """Generate temporal analysis section"""
        section = {
            'hourly_patterns': {},
            'daily_patterns': {}
        }
        
        if 'timestamp' not in self.df.columns:
            return section
        
        df_time = self.df.copy()
        df_time['timestamp'] = pd.to_datetime(df_time['timestamp'])
        df_time['hour'] = df_time['timestamp'].dt.hour
        
        # Hourly patterns
        if 'value' in df_time.columns:
            hourly = df_time.groupby('hour')['value'].agg(['mean', 'std', 'count'])
            section['hourly_patterns'] = {
                str(hour): {
                    'mean': float(row['mean']),
                    'std': float(row['std']),
                    'count': int(row['count'])
                }
                for hour, row in hourly.iterrows()
            }
        
        return section
    
    def _generate_correlation_section(self) -> Dict[str, Any]:
        """Generate correlation section"""
        section = {
            'correlation_matrix': {},
            'high_correlations': []
        }
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) > 1:
            corr_matrix = self.df[numeric_cols].corr()
            section['correlation_matrix'] = corr_matrix.to_dict()
            
            # Find high correlations
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        section['high_correlations'].append({
                            'variable1': corr_matrix.columns[i],
                            'variable2': corr_matrix.columns[j],
                            'correlation': float(corr_val)
                        })
        
        return section
    
    def save_report(self, filename: str = None, format: str = 'txt') -> str:
        """
        Save report to file
        
        Args:
            filename: Output filename (if None, auto-generated)
            format: Report format ('txt', 'json', 'md')
            
        Returns:
            Path to saved report
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"eda_report_{timestamp}.{format}"
            
            filepath = os.path.join(self.output_dir, filename)
            
            if format == 'txt':
                report_content = self.generate_summary_report()
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(report_content)
            
            elif format == 'json':
                report_content = self.generate_detailed_report()
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(report_content, f, indent=2, default=str)
            
            elif format == 'md':
                report_content = self._generate_markdown_report()
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(report_content)
            
            logger.info(f"✓ Saved report to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return ""
    
    def _generate_markdown_report(self) -> str:
        """Generate markdown formatted report"""
        report = []
        
        report.append("# Smart Agriculture - Exploratory Data Analysis Report\n")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Overview
        report.append("## 1. Dataset Overview\n")
        report.append(f"- **Total Observations:** {len(self.df):,}")
        
        if 'sensor_id' in self.df.columns:
            report.append(f"- **Total Sensors:** {self.df['sensor_id'].nunique()}")
        
        if 'sensor_type' in self.df.columns:
            report.append(f"- **Sensor Types:** {self.df['sensor_type'].nunique()}")
        
        # Data Quality
        report.append("\n## 2. Data Quality\n")
        
        if 'quality' in self.df.columns:
            report.append(f"- **Average Quality:** {self.df['quality'].mean():.2f}%")
        
        if 'is_outlier' in self.df.columns:
            outlier_pct = self.df['is_outlier'].mean() * 100
            report.append(f"- **Outliers:** {outlier_pct:.2f}%")
        
        # Statistics
        report.append("\n## 3. Descriptive Statistics\n")
        
        if 'value' in self.df.columns:
            report.append(f"- **Mean:** {self.df['value'].mean():.4f}")
            report.append(f"- **Median:** {self.df['value'].median():.4f}")
            report.append(f"- **Std Dev:** {self.df['value'].std():.4f}")
        
        # Sensor Analysis
        report.append("\n## 4. Sensor Analysis\n")
        
        if 'sensor_id' in self.df.columns:
            sensor_counts = self.df.groupby('sensor_id').size()
            report.append(f"- **Total Sensors:** {len(sensor_counts)}")
            report.append(f"- **Average Readings per Sensor:** {sensor_counts.mean():.2f}")
        
        return "\n".join(report)
    
    def save_all_formats(self, base_filename: str = None) -> List[str]:
        """
        Save report in all formats
        
        Args:
            base_filename: Base filename (if None, auto-generated)
            
        Returns:
            List of saved file paths
        """
        try:
            if base_filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_filename = f"eda_report_{timestamp}"
            
            saved_files = []
            
            # Save in all formats
            for fmt in ['txt', 'json', 'md']:
                filename = f"{base_filename}.{fmt}"
                filepath = self.save_report(filename, format=fmt)
                if filepath:
                    saved_files.append(filepath)
            
            logger.info(f"✓ Saved report in {len(saved_files)} formats")
            
            return saved_files
            
        except Exception as e:
            logger.error(f"Failed to save all formats: {e}")
            return []


def generate_eda_report(df: pd.DataFrame, output_dir: str = 'reports') -> str:
    """
    Convenience function to generate EDA report
    
    Args:
        df: DataFrame with sensor data
        output_dir: Directory to save reports
        
    Returns:
        Path to saved report
    """
    generator = ReportGenerator(df, output_dir)
    return generator.save_report(format='txt')


def generate_detailed_eda_report(df: pd.DataFrame, output_dir: str = 'reports') -> Dict[str, Any]:
    """
    Convenience function to generate detailed EDA report
    
    Args:
        df: DataFrame with sensor data
        output_dir: Directory to save reports
        
    Returns:
        Dictionary with report data
    """
    generator = ReportGenerator(df, output_dir)
    return generator.generate_detailed_report()


if __name__ == "__main__":
    # Test with sample data
    from analytics.load_data import load_sample_data
    
    print("Loading sample data...")
    df = load_sample_data()
    
    print("\nGenerating reports...")
    generator = ReportGenerator(df)
    
    # Generate summary report
    summary = generator.generate_summary_report()
    print("\n" + summary)
    
    # Save in all formats
    saved_files = generator.save_all_formats()
    print(f"\n✓ Saved {len(saved_files)} report files:")
    for filepath in saved_files:
        print(f"  - {filepath}")
    
    # Generate detailed report
    detailed = generator.generate_detailed_report()
    print(f"\nDetailed report sections: {list(detailed.keys())}")