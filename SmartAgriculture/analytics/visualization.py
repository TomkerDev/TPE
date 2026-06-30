"""
Visualization Module
Creates comprehensive visualizations for sensor data analysis
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set default style
sns.set_style("whitegrid")
rcParams['figure.figsize'] = (12, 6)
rcParams['font.size'] = 10


class Visualizer:
    """Creates visualizations for sensor data"""
    
    def __init__(self, df: pd.DataFrame, output_dir: str = 'results'):
        """
        Initialize visualizer
        
        Args:
            df: DataFrame with sensor data
            output_dir: Directory to save plots
        """
        self.df = df.copy()
        self.output_dir = output_dir
        self.plots_created = []
        
        # Create output directory
        import os
        os.makedirs(output_dir, exist_ok=True)
        
    def plot_histogram(self, column: str = 'value', 
                      bins: int = 40,
                      figsize: Tuple[int, int] = (12, 6),
                      save_path: Optional[str] = None) -> str:
        """
        Plot histogram of values
        
        Args:
            column: Column to plot
            bins: Number of bins
            figsize: Figure size
            save_path: Optional custom save path
            
        Returns:
            Path to saved figure
        """
        try:
            if column not in self.df.columns:
                logger.error(f"Column {column} not found")
                return ""
            
            plt.figure(figsize=figsize)
            plt.hist(self.df[column].dropna(), bins=bins, edgecolor='black', alpha=0.7)
            plt.title(f'Distribution of {column}', fontsize=14, fontweight='bold')
            plt.xlabel(column, fontsize=12)
            plt.ylabel('Frequency', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save
            if save_path is None:
                save_path = f"{self.output_dir}/histogram_{column}.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.plots_created.append(save_path)
            logger.info(f"✓ Saved histogram to {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot histogram: {e}")
            return ""
    
    def plot_boxplot_by_sensor(self, column: str = 'value',
                              figsize: Tuple[int, int] = (14, 6),
                              save_path: Optional[str] = None) -> str:
        """
        Plot boxplot by sensor type
        
        Args:
            column: Column to plot
            figsize: Figure size
            save_path: Optional custom save path
            
        Returns:
            Path to saved figure
        """
        try:
            if column not in self.df.columns or 'sensor_type' not in self.df.columns:
                logger.error("Required columns not found")
                return ""
            
            plt.figure(figsize=figsize)
            self.df.boxplot(column=column, by='sensor_type')
            plt.title(f'{column} by Sensor Type', fontsize=14, fontweight='bold')
            plt.suptitle('')  # Remove automatic title
            plt.xlabel('Sensor Type', fontsize=12)
            plt.ylabel(column, fontsize=12)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save
            if save_path is None:
                save_path = f"{self.output_dir}/boxplot_by_sensor.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.plots_created.append(save_path)
            logger.info(f"✓ Saved boxplot to {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot boxplot: {e}")
            return ""
    
    def plot_time_series(self, sensor_id: str = None, column: str = 'value',
                        figsize: Tuple[int, int] = (15, 6),
                        save_path: Optional[str] = None) -> str:
        """
        Plot time series
        
        Args:
            sensor_id: Optional sensor ID to filter
            column: Column to plot
            figsize: Figure size
            save_path: Optional custom save path
            
        Returns:
            Path to saved figure
        """
        try:
            if 'timestamp' not in self.df.columns or column not in self.df.columns:
                logger.error("Required columns not found")
                return ""
            
            df = self.df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
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
            
            # Save
            if save_path is None:
                sensor_suffix = f"_{sensor_id}" if sensor_id else ""
                save_path = f"{self.output_dir}/timeseries{sensor_suffix}_{column}.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.plots_created.append(save_path)
            logger.info(f"✓ Saved time series to {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot time series: {e}")
            return ""
    
    def plot_correlation_heatmap(self, figsize: Tuple[int, int] = (12, 10),
                                save_path: Optional[str] = None) -> str:
        """
        Plot correlation heatmap
        
        Args:
            figsize: Figure size
            save_path: Optional custom save path
            
        Returns:
            Path to saved figure
        """
        try:
            # Select numeric columns
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) < 2:
                logger.warning("Not enough numeric columns for correlation")
                return ""
            
            corr_matrix = self.df[numeric_cols].corr()
            
            plt.figure(figsize=figsize)
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
            
            # Save
            if save_path is None:
                save_path = f"{self.output_dir}/correlation_heatmap.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.plots_created.append(save_path)
            logger.info(f"✓ Saved correlation heatmap to {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot correlation heatmap: {e}")
            return ""
    
    def plot_scatter(self, x_column: str, y_column: str,
                    hue_column: str = None,
                    figsize: Tuple[int, int] = (10, 8),
                    save_path: Optional[str] = None) -> str:
        """
        Plot scatter plot
        
        Args:
            x_column: X-axis column
            y_column: Y-axis column
            hue_column: Optional column for coloring
            figsize: Figure size
            save_path: Optional custom save path
            
        Returns:
            Path to saved figure
        """
        try:
            if x_column not in self.df.columns or y_column not in self.df.columns:
                logger.error("Required columns not found")
                return ""
            
            plt.figure(figsize=figsize)
            
            if hue_column and hue_column in self.df.columns:
                for hue_value in self.df[hue_column].unique():
                    subset = self.df[self.df[hue_column] == hue_value]
                    plt.scatter(subset[x_column], subset[y_column], 
                              label=str(hue_value), alpha=0.6)
                plt.legend()
            else:
                plt.scatter(self.df[x_column], self.df[y_column], alpha=0.6)
            
            plt.title(f'{y_column} vs {x_column}', fontsize=14, fontweight='bold')
            plt.xlabel(x_column, fontsize=12)
            plt.ylabel(y_column, fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save
            if save_path is None:
                save_path = f"{self.output_dir}/scatter_{x_column}_vs_{y_column}.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.plots_created.append(save_path)
            logger.info(f"✓ Saved scatter plot to {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot scatter: {e}")
            return ""
    
    def plot_sensor_distribution(self, column: str = 'value',
                                figsize: Tuple[int, int] = (12, 6),
                                save_path: Optional[str] = None) -> str:
        """
        Plot distribution by sensor type
        
        Args:
            column: Column to plot
            figsize: Figure size
            save_path: Optional custom save path
            
        Returns:
            Path to saved figure
        """
        try:
            if column not in self.df.columns or 'sensor_type' not in self.df.columns:
                logger.error("Required columns not found")
                return ""
            
            plt.figure(figsize=figsize)
            
            sensor_types = self.df['sensor_type'].unique()
            for sensor_type in sensor_types:
                subset = self.df[self.df['sensor_type'] == sensor_type]
                plt.hist(subset[column].dropna(), bins=30, alpha=0.6, label=sensor_type)
            
            plt.legend()
            plt.title(f'{column} Distribution by Sensor Type', fontsize=14, fontweight='bold')
            plt.xlabel(column, fontsize=12)
            plt.ylabel('Frequency', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save
            if save_path is None:
                save_path = f"{self.output_dir}/distribution_by_sensor.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.plots_created.append(save_path)
            logger.info(f"✓ Saved distribution plot to {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot distribution: {e}")
            return ""
    
    def plot_hourly_pattern(self, column: str = 'value',
                           figsize: Tuple[int, int] = (12, 6),
                           save_path: Optional[str] = None) -> str:
        """
        Plot hourly pattern
        
        Args:
            column: Column to plot
            figsize: Figure size
            save_path: Optional custom save path
            
        Returns:
            Path to saved figure
        """
        try:
            if 'timestamp' not in self.df.columns:
                logger.error("timestamp column not found")
                return ""
            
            df = self.df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            
            hourly = df.groupby('hour')[column].agg(['mean', 'std']).reset_index()
            
            plt.figure(figsize=figsize)
            plt.plot(hourly['hour'], hourly['mean'], marker='o', linewidth=2)
            plt.fill_between(hourly['hour'], 
                           hourly['mean'] - hourly['std'], 
                           hourly['mean'] + hourly['std'], 
                           alpha=0.3)
            
            plt.title('Hourly Pattern', fontsize=14, fontweight='bold')
            plt.xlabel('Hour of Day', fontsize=12)
            plt.ylabel(f'Average {column}', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xticks(range(0, 24))
            plt.tight_layout()
            
            # Save
            if save_path is None:
                save_path = f"{self.output_dir}/hourly_pattern.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.plots_created.append(save_path)
            logger.info(f"✓ Saved hourly pattern to {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot hourly pattern: {e}")
            return ""
    
    def plot_daily_pattern(self, column: str = 'value',
                          figsize: Tuple[int, int] = (12, 6),
                          save_path: Optional[str] = None) -> str:
        """
        Plot daily pattern
        
        Args:
            column: Column to plot
            figsize: Figure size
            save_path: Optional custom save path
            
        Returns:
            Path to saved figure
        """
        try:
            if 'timestamp' not in self.df.columns:
                logger.error("timestamp column not found")
                return ""
            
            df = self.df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            daily = df.groupby('day_of_week')[column].agg(['mean', 'std']).reset_index()
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            plt.figure(figsize=figsize)
            plt.plot(daily['day_of_week'], daily['mean'], marker='o', linewidth=2)
            plt.fill_between(daily['day_of_week'], 
                           daily['mean'] - daily['std'], 
                           daily['mean'] + daily['std'], 
                           alpha=0.3)
            
            plt.title('Daily Pattern', fontsize=14, fontweight='bold')
            plt.xlabel('Day of Week', fontsize=12)
            plt.ylabel(f'Average {column}', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xticks(range(7), days, rotation=45)
            plt.tight_layout()
            
            # Save
            if save_path is None:
                save_path = f"{self.output_dir}/daily_pattern.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.plots_created.append(save_path)
            logger.info(f"✓ Saved daily pattern to {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot daily pattern: {e}")
            return ""
    
    def plot_anomalies_scatter(self, column: str = 'value',
                              figsize: Tuple[int, int] = (15, 6),
                              save_path: Optional[str] = None) -> str:
        """
        Plot anomalies as scatter plot
        
        Args:
            column: Column to plot
            figsize: Figure size
            save_path: Optional custom save path
            
        Returns:
            Path to saved figure
        """
        try:
            if 'timestamp' not in self.df.columns or column not in self.df.columns:
                logger.error("Required columns not found")
                return ""
            
            df = self.df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            plt.figure(figsize=figsize)
            
            # Color by outlier status if available
            if 'is_outlier' in df.columns:
                normal = df[df['is_outlier'] == False]
                outliers = df[df['is_outlier'] == True]
                
                plt.scatter(normal['timestamp'], normal[column], 
                          c='blue', s=3, alpha=0.6, label='Normal')
                plt.scatter(outliers['timestamp'], outliers[column], 
                          c='red', s=20, alpha=0.8, label='Outlier')
                plt.legend()
            else:
                plt.scatter(df['timestamp'], df[column], s=3, alpha=0.6)
            
            plt.title('Observed Values with Anomalies', fontsize=14, fontweight='bold')
            plt.xlabel('Timestamp', fontsize=12)
            plt.ylabel(column, fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save
            if save_path is None:
                save_path = f"{self.output_dir}/anomalies_scatter.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.plots_created.append(save_path)
            logger.info(f"✓ Saved anomalies scatter plot to {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to plot anomalies: {e}")
            return ""
    
    def create_dashboard_plots(self) -> List[str]:
        """
        Create all standard dashboard plots
        
        Returns:
            List of paths to created plots
        """
        try:
            logger.info("Creating dashboard plots...")
            
            # 1. Histogram
            self.plot_histogram()
            
            # 2. Boxplot by sensor
            self.plot_boxplot_by_sensor()
            
            # 3. Time series
            self.plot_time_series()
            
            # 4. Correlation heatmap
            self.plot_correlation_heatmap()
            
            # 5. Distribution by sensor
            self.plot_sensor_distribution()
            
            # 6. Hourly pattern
            self.plot_hourly_pattern()
            
            # 7. Daily pattern
            self.plot_daily_pattern()
            
            # 8. Anomalies
            self.plot_anomalies_scatter()
            
            logger.info(f"✓ Created {len(self.plots_created)} dashboard plots")
            
            return self.plots_created
            
        except Exception as e:
            logger.error(f"Failed to create dashboard plots: {e}")
            return []
    
    def get_plots_created(self) -> List[str]:
        """Get list of created plot paths"""
        return self.plots_created


def create_standard_visualizations(df: pd.DataFrame, output_dir: str = 'results') -> List[str]:
    """
    Convenience function to create all standard visualizations
    
    Args:
        df: DataFrame with sensor data
        output_dir: Directory to save plots
        
    Returns:
        List of paths to created plots
    """
    visualizer = Visualizer(df, output_dir)
    return visualizer.create_dashboard_plots()


if __name__ == "__main__":
    # Test with sample data
    from analytics.load_data import load_sample_data
    
    print("Loading sample data...")
    df = load_sample_data()
    
    print("\nCreating visualizations...")
    visualizer = Visualizer(df)
    
    # Create all dashboard plots
    plots = visualizer.create_dashboard_plots()
    
    print(f"\nCreated {len(plots)} plots:")
    for plot in plots:
        print(f"  - {plot}")