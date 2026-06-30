"""
Correlation Analysis Module
Analyzes correlations between variables and sensor readings
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CorrelationAnalysis:
    """Performs correlation analysis on sensor data"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with DataFrame
        
        Args:
            df: DataFrame with sensor data
        """
        self.df = df.copy()
        self.correlation_results = {}
        
    def compute_correlation_matrix(self, method: str = 'pearson') -> pd.DataFrame:
        """
        Compute correlation matrix
        
        Args:
            method: Correlation method ('pearson', 'kendall', 'spearman')
            
        Returns:
            Correlation matrix DataFrame
        """
        try:
            # Select numeric columns
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_cols:
                logger.warning("No numeric columns found")
                return pd.DataFrame()
            
            # Compute correlation matrix
            corr_matrix = self.df[numeric_cols].corr(method=method)
            
            self.correlation_results['matrix'] = corr_matrix
            logger.info(f"✓ Computed {method} correlation matrix")
            
            return corr_matrix
            
        except Exception as e:
            logger.error(f"Failed to compute correlation matrix: {e}")
            return pd.DataFrame()
    
    def compute_correlation_by_sensor_type(self, column: str = 'value') -> Dict[str, pd.DataFrame]:
        """
        Compute correlation matrices for each sensor type
        
        Args:
            column: Column to pivot on
            
        Returns:
            Dictionary of correlation matrices by sensor type
        """
        try:
            if 'sensor_type' not in self.df.columns:
                logger.error("sensor_type column not found")
                return {}
            
            correlation_by_type = {}
            
            for sensor_type in self.df['sensor_type'].unique():
                # Filter by sensor type
                df_type = self.df[self.df['sensor_type'] == sensor_type]
                
                # Pivot to get sensors as columns
                if 'sensor_id' in df_type.columns and 'timestamp' in df_type.columns:
                    pivot_df = df_type.pivot_table(
                        index='timestamp',
                        columns='sensor_id',
                        values=column,
                        aggfunc='mean'
                    )
                    
                    # Compute correlation
                    if not pivot_df.empty and len(pivot_df.columns) > 1:
                        corr = pivot_df.corr()
                        correlation_by_type[sensor_type] = corr
            
            self.correlation_results['by_sensor_type'] = correlation_by_type
            logger.info(f"✓ Computed correlations for {len(correlation_by_type)} sensor types")
            
            return correlation_by_type
            
        except Exception as e:
            logger.error(f"Failed to compute correlation by sensor type: {e}")
            return {}
    
    def find_high_correlations(self, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Find highly correlated variable pairs
        
        Args:
            threshold: Correlation threshold (absolute value)
            
        Returns:
            List of dictionaries with high correlations
        """
        try:
            if 'matrix' not in self.correlation_results:
                self.compute_correlation_matrix()
            
            corr_matrix = self.correlation_results['matrix']
            
            # Find high correlations
            high_corr = []
            
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    col1 = corr_matrix.columns[i]
                    col2 = corr_matrix.columns[j]
                    corr_value = corr_matrix.iloc[i, j]
                    
                    if abs(corr_value) >= threshold:
                        high_corr.append({
                            'variable1': col1,
                            'variable2': col2,
                            'correlation': float(corr_value),
                            'strength': self._interpret_correlation(corr_value)
                        })
            
            # Sort by absolute correlation
            high_corr.sort(key=lambda x: abs(x['correlation']), reverse=True)
            
            self.correlation_results['high_correlations'] = high_corr
            logger.info(f"✓ Found {len(high_corr)} high correlations (threshold={threshold})")
            
            return high_corr
            
        except Exception as e:
            logger.error(f"Failed to find high correlations: {e}")
            return []
    
    def compute_sensor_correlations(self, sensor_id_1: str, sensor_id_2: str,
                                   column: str = 'value') -> Dict[str, Any]:
        """
        Compute correlation between two specific sensors
        
        Args:
            sensor_id_1: First sensor ID
            sensor_id_2: Second sensor ID
            column: Column to correlate
            
        Returns:
            Dictionary with correlation statistics
        """
        try:
            if 'sensor_id' not in self.df.columns:
                return {}
            
            # Get data for each sensor
            data1 = self.df[self.df['sensor_id'] == sensor_id_1][['timestamp', column]].dropna()
            data2 = self.df[self.df['sensor_id'] == sensor_id_2][['timestamp', column]].dropna()
            
            # Merge on timestamp
            merged = pd.merge(
                data1,
                data2,
                on='timestamp',
                suffixes=('_1', '_2')
            )
            
            if len(merged) < 2:
                logger.warning(f"Not enough overlapping data between {sensor_id_1} and {sensor_id_2}")
                return {}
            
            # Compute correlations
            pearson_r, pearson_p = stats.pearsonr(merged[f'{column}_1'], merged[f'{column}_2'])
            spearman_r, spearman_p = stats.spearmanr(merged[f'{column}_1'], merged[f'{column}_2'])
            
            result = {
                'sensor_1': sensor_id_1,
                'sensor_2': sensor_id_2,
                'sample_size': len(merged),
                'pearson_r': float(pearson_r),
                'pearson_p_value': float(pearson_p),
                'spearman_r': float(spearman_r),
                'spearman_p_value': float(spearman_p),
                'significant': pearson_p < 0.05
            }
            
            logger.info(f"✓ Correlation between {sensor_id_1} and {sensor_id_2}: r={pearson_r:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to compute sensor correlation: {e}")
            return {}
    
    def compute_lagged_correlation(self, sensor_id: str, column: str = 'value',
                                  max_lag: int = 24) -> pd.DataFrame:
        """
        Compute lagged correlations for time series
        
        Args:
            sensor_id: Sensor ID
            column: Column to analyze
            max_lag: Maximum lag periods
            
        Returns:
            DataFrame with lag correlations
        """
        try:
            if 'sensor_id' not in self.df.columns:
                return pd.DataFrame()
            
            # Get sensor data
            sensor_data = self.df[self.df['sensor_id'] == sensor_id].copy()
            sensor_data = sensor_data.sort_values('timestamp')
            
            if len(sensor_data) < max_lag + 1:
                logger.warning(f"Not enough data for lag analysis")
                return pd.DataFrame()
            
            # Compute autocorrelation
            series = sensor_data[column].dropna()
            
            lag_corr = []
            for lag in range(0, max_lag + 1):
                if lag == 0:
                    corr = 1.0
                else:
                    corr = series.autocorr(lag=lag)
                
                lag_corr.append({
                    'lag': lag,
                    'correlation': corr
                })
            
            lag_df = pd.DataFrame(lag_corr)
            
            self.correlation_results[f'lagged_{sensor_id}'] = lag_df
            logger.info(f"✓ Computed lagged correlations for {sensor_id}")
            
            return lag_df
            
        except Exception as e:
            logger.error(f"Failed to compute lagged correlation: {e}")
            return pd.DataFrame()
    
    def _interpret_correlation(self, r: float) -> str:
        """Interpret correlation strength"""
        abs_r = abs(r)
        if abs_r >= 0.9:
            return "Very Strong"
        elif abs_r >= 0.7:
            return "Strong"
        elif abs_r >= 0.5:
            return "Moderate"
        elif abs_r >= 0.3:
            return "Weak"
        else:
            return "Very Weak"
    
    def plot_correlation_heatmap(self, figsize: Tuple[int, int] = (12, 10),
                                save_path: Optional[str] = None):
        """
        Plot correlation heatmap
        
        Args:
            figsize: Figure size
            save_path: Optional path to save figure
        """
        try:
            if 'matrix' not in self.correlation_results:
                self.compute_correlation_matrix()
            
            corr_matrix = self.correlation_results['matrix']
            
            if corr_matrix.empty:
                logger.warning("No correlation matrix to plot")
                return
            
            plt.figure(figsize=figsize)
            
            # Create heatmap
            sns.heatmap(
                corr_matrix,
                annot=True,
                fmt='.2f',
                cmap='coolwarm',
                center=0,
                square=True,
                linewidths=0.5,
                cbar_kws={"shrink": 0.8}
            )
            
            plt.title('Correlation Matrix Heatmap', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"✓ Saved heatmap to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Failed to plot heatmap: {e}")
    
    def plot_scatter_matrix(self, columns: List[str] = None, 
                          figsize: Tuple[int, int] = (12, 12),
                          save_path: Optional[str] = None):
        """
        Plot scatter matrix for selected columns
        
        Args:
            columns: List of columns to plot
            figsize: Figure size
            save_path: Optional path to save figure
        """
        try:
            if columns is None:
                columns = self.df.select_dtypes(include=[np.number]).columns.tolist()[:5]
            
            if len(columns) < 2:
                logger.warning("Need at least 2 columns for scatter matrix")
                return
            
            # Add sensor_type for coloring
            plot_df = self.df[columns].copy()
            if 'sensor_type' in self.df.columns:
                plot_df['sensor_type'] = self.df['sensor_type']
            
            # Create scatter matrix
            pd.plotting.scatter_matrix(
                plot_df[columns],
                figsize=figsize,
                diagonal='hist',
                alpha=0.5
            )
            
            plt.suptitle('Scatter Matrix', fontsize=16, fontweight='bold', y=1.02)
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"✓ Saved scatter matrix to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Failed to plot scatter matrix: {e}")
    
    def get_correlation_summary(self) -> str:
        """
        Generate correlation analysis summary
        
        Returns:
            Formatted summary report
        """
        try:
            report = []
            report.append("=" * 70)
            report.append("CORRELATION ANALYSIS REPORT")
            report.append("=" * 70)
            
            # High correlations
            if 'high_correlations' in self.correlation_results:
                high_corr = self.correlation_results['high_correlations']
                
                report.append(f"\n--- High Correlations (|r| >= 0.7) ---")
                if high_corr:
                    for corr in high_corr[:10]:  # Top 10
                        report.append(
                            f"{corr['variable1']} <-> {corr['variable2']}: "
                            f"r = {corr['correlation']:.3f} ({corr['strength']})"
                        )
                else:
                    report.append("No high correlations found")
            
            # By sensor type
            if 'by_sensor_type' in self.correlation_results:
                report.append(f"\n--- Correlations by Sensor Type ---")
                for sensor_type, corr_matrix in self.correlation_results['by_sensor_type'].items():
                    report.append(f"\n{sensor_type}:")
                    # Get highest correlation
                    if not corr_matrix.empty:
                        corr_values = corr_matrix.where(
                            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
                        ).stack()
                        if not corr_values.empty:
                            max_corr = corr_values.abs().idxmax()
                            max_val = corr_values.loc[max_corr]
                            report.append(
                                f"  Highest: {max_corr[0]} <-> {max_corr[1]}: r = {max_val:.3f}"
                            )
            
            report.append("\n" + "=" * 70)
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Failed to generate correlation summary: {e}")
            return "Error generating report"


def analyze_correlations(df: pd.DataFrame, threshold: float = 0.7) -> Dict[str, Any]:
    """
    Convenience function to perform complete correlation analysis
    
    Args:
        df: DataFrame with sensor data
        threshold: Correlation threshold for high correlations
        
    Returns:
        Dictionary with correlation analysis results
    """
    analysis = CorrelationAnalysis(df)
    
    # Compute all correlations
    analysis.compute_correlation_matrix()
    analysis.compute_correlation_by_sensor_type()
    analysis.find_high_correlations(threshold)
    
    return analysis.correlation_results


def print_correlation_summary(df: pd.DataFrame):
    """
    Print correlation analysis summary
    
    Args:
        df: DataFrame with sensor data
    """
    analysis = CorrelationAnalysis(df)
    analysis.compute_correlation_matrix()
    analysis.find_high_correlations()
    print(analysis.get_correlation_summary())


if __name__ == "__main__":
    # Test with sample data
    from analytics.load_data import load_sample_data
    
    print("Loading sample data...")
    df = load_sample_data()
    
    print("\nPerforming correlation analysis...")
    analysis = CorrelationAnalysis(df)
    
    # Compute correlations
    corr_matrix = analysis.compute_correlation_matrix()
    print("\nCorrelation Matrix:")
    print(corr_matrix)
    
    # Find high correlations
    high_corr = analysis.find_high_correlations(threshold=0.5)
    print(f"\nFound {len(high_corr)} high correlations")
    
    # Print summary
    print(analysis.get_correlation_summary())
    
    # Plot heatmap
    analysis.plot_correlation_heatmap(save_path='results/correlation_heatmap.png')