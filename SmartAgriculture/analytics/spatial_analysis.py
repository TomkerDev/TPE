"""
Spatial Analysis Module
Analyzes spatial patterns and geographic distribution of sensors
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
import matplotlib.pyplot as plt
from math import radians, cos, sin, asin, sqrt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpatialAnalysis:
    """Performs spatial analysis on sensor data"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with DataFrame
        
        Args:
            df: DataFrame with sensor data
        """
        self.df = df.copy()
        self.spatial_results = {}
        
    def filter_gps_sensors(self) -> pd.DataFrame:
        """
        Filter DataFrame to only GPS sensors
        
        Returns:
            DataFrame with GPS sensor data
        """
        try:
            if 'sensor_type' in self.df.columns:
                gps_df = self.df[self.df['sensor_type'] == 'gps'].copy()
            else:
                # Assume all data has lat/long
                gps_df = self.df.copy()
            
            if gps_df.empty:
                logger.warning("No GPS data found")
                return pd.DataFrame()
            
            self.spatial_results['gps_data'] = gps_df
            logger.info(f"✓ Found {len(gps_df)} GPS records")
            
            return gps_df
            
        except Exception as e:
            logger.error(f"Failed to filter GPS sensors: {e}")
            return pd.DataFrame()
    
    def compute_bounds(self) -> Dict[str, float]:
        """
        Compute geographic bounds
        
        Returns:
            Dictionary with min/max lat/long
        """
        try:
            gps_df = self.filter_gps_sensors()
            
            if gps_df.empty:
                return {}
            
            bounds = {
                'min_lat': float(gps_df['latitude'].min()),
                'max_lat': float(gps_df['latitude'].max()),
                'min_long': float(gps_df['longitude'].min()),
                'max_long': float(gps_df['longitude'].max()),
                'center_lat': float(gps_df['latitude'].mean()),
                'center_long': float(gps_df['longitude'].mean())
            }
            
            self.spatial_results['bounds'] = bounds
            logger.info("✓ Computed geographic bounds")
            
            return bounds
            
        except Exception as e:
            logger.error(f"Failed to compute bounds: {e}")
            return {}
    
    def compute_sensor_density(self, grid_size: float = 0.01) -> pd.DataFrame:
        """
        Compute sensor density in grid cells
        
        Args:
            grid_size: Grid cell size in degrees
            
        Returns:
            DataFrame with density by grid cell
        """
        try:
            gps_df = self.filter_gps_sensors()
            
            if gps_df.empty:
                return pd.DataFrame()
            
            # Create grid cells
            gps_df['lat_grid'] = (gps_df['latitude'] // grid_size) * grid_size
            gps_df['long_grid'] = (gps_df['longitude'] // grid_size) * grid_size
            
            # Count sensors per grid cell
            density = gps_df.groupby(['lat_grid', 'long_grid']).agg({
                'sensor_id': 'nunique',
                'value': 'mean'
            }).reset_index()
            
            density.columns = ['latitude', 'longitude', 'sensor_count', 'avg_value']
            
            self.spatial_results['density'] = density
            logger.info(f"✓ Computed density for {len(density)} grid cells")
            
            return density
            
        except Exception as e:
            logger.error(f"Failed to compute sensor density: {e}")
            return pd.DataFrame()
    
    def find_nearby_sensors(self, sensor_id: str, radius_km: float = 1.0) -> List[Dict]:
        """
        Find sensors within radius of a given sensor
        
        Args:
            sensor_id: Reference sensor ID
            radius_km: Radius in kilometers
            
        Returns:
            List of nearby sensors
        """
        try:
            if 'sensor_id' not in self.df.columns:
                return []
            
            # Get reference sensor location
            ref_sensor = self.df[self.df['sensor_id'] == sensor_id].iloc[0]
            ref_lat = ref_sensor['latitude']
            ref_long = ref_sensor['longitude']
            
            # Get all unique sensors with locations
            sensors = self.df.groupby('sensor_id').agg({
                'latitude': 'first',
                'longitude': 'first',
                'sensor_type': 'first'
            }).reset_index()
            
            # Calculate distances
            nearby = []
            for _, sensor in sensors.iterrows():
                if sensor['sensor_id'] != sensor_id:
                    distance = self._haversine_distance(
                        ref_lat, ref_long,
                        sensor['latitude'], sensor['longitude']
                    )
                    
                    if distance <= radius_km:
                        nearby.append({
                            'sensor_id': sensor['sensor_id'],
                            'sensor_type': sensor['sensor_type'],
                            'distance_km': distance,
                            'latitude': sensor['latitude'],
                            'longitude': sensor['longitude']
                        })
            
            # Sort by distance
            nearby.sort(key=lambda x: x['distance_km'])
            
            logger.info(f"✓ Found {len(nearby)} sensors within {radius_km}km of {sensor_id}")
            
            return nearby
            
        except Exception as e:
            logger.error(f"Failed to find nearby sensors: {e}")
            return []
    
    def _haversine_distance(self, lat1: float, long1: float, 
                           lat2: float, long2: float) -> float:
        """
        Calculate haversine distance between two points
        
        Args:
            lat1, long1: First point coordinates
            lat2, long2: Second point coordinates
            
        Returns:
            Distance in kilometers
        """
        try:
            # Convert to radians
            lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2, long2])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlong = long2 - long1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlong/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371  # Earth radius in kilometers
            
            return c * r
            
        except Exception as e:
            logger.error(f"Failed to calculate distance: {e}")
            return 0.0
    
    def compute_spatial_statistics(self) -> Dict[str, Any]:
        """
        Compute spatial statistics
        
        Returns:
            Dictionary with spatial statistics
        """
        try:
            gps_df = self.filter_gps_sensors()
            
            if gps_df.empty:
                return {}
            
            stats = {
                'total_sensors': gps_df['sensor_id'].nunique(),
                'latitude_range': {
                    'min': float(gps_df['latitude'].min()),
                    'max': float(gps_df['latitude'].max()),
                    'span': float(gps_df['latitude'].max() - gps_df['latitude'].min())
                },
                'longitude_range': {
                    'min': float(gps_df['longitude'].min()),
                    'max': float(gps_df['longitude'].max()),
                    'span': float(gps_df['longitude'].max() - gps_df['longitude'].min())
                },
                'center': {
                    'lat': float(gps_df['latitude'].mean()),
                    'long': float(gps_df['longitude'].mean())
                }
            }
            
            # Compute sensor type distribution
            if 'sensor_type' in gps_df.columns:
                stats['sensor_type_distribution'] = gps_df.groupby('sensor_type')['sensor_id'].nunique().to_dict()
            
            self.spatial_results['statistics'] = stats
            logger.info("✓ Computed spatial statistics")
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to compute spatial statistics: {e}")
            return {}
    
    def detect_spatial_outliers(self, threshold_std: float = 2.0) -> pd.DataFrame:
        """
        Detect spatially outlier sensors (far from others)
        
        Args:
            threshold_std: Standard deviation threshold
            
        Returns:
            DataFrame with outlier sensors
        """
        try:
            gps_df = self.filter_gps_sensors()
            
            if gps_df.empty:
                return pd.DataFrame()
            
            # Get unique sensor locations
            sensors = gps_df.groupby('sensor_id').agg({
                'latitude': 'first',
                'longitude': 'first',
                'sensor_type': 'first'
            }).reset_index()
            
            # Compute mean and std of coordinates
            mean_lat = sensors['latitude'].mean()
            std_lat = sensors['latitude'].std()
            mean_long = sensors['longitude'].mean()
            std_long = sensors['longitude'].std()
            
            # Find outliers
            outliers = sensors[
                ((sensors['latitude'] < mean_lat - threshold_std * std_lat) |
                 (sensors['latitude'] > mean_lat + threshold_std * std_lat) |
                 (sensors['longitude'] < mean_long - threshold_std * std_long) |
                 (sensors['longitude'] > mean_long + threshold_std * std_long))
            ]
            
            self.spatial_results['outliers'] = outliers
            logger.info(f"✓ Detected {len(outliers)} spatial outliers")
            
            return outliers
            
        except Exception as e:
            logger.error(f"Failed to detect spatial outliers: {e}")
            return pd.DataFrame()
    
    def plot_sensor_map(self, figsize: Tuple[int, int] = (10, 10),
                       save_path: Optional[str] = None):
        """
        Plot sensor locations on map
        
        Args:
            figsize: Figure size
            save_path: Optional path to save figure
        """
        try:
            gps_df = self.filter_gps_sensors()
            
            if gps_df.empty:
                logger.warning("No GPS data to plot")
                return
            
            # Get unique sensors
            sensors = gps_df.groupby('sensor_id').agg({
                'latitude': 'first',
                'longitude': 'first',
                'sensor_type': 'first'
            }).reset_index()
            
            plt.figure(figsize=figsize)
            
            # Color by sensor type
            sensor_types = sensors['sensor_type'].unique()
            colors = plt.cm.Set1(np.linspace(0, 1, len(sensor_types)))
            color_map = dict(zip(sensor_types, colors))
            
            for sensor_type in sensor_types:
                subset = sensors[sensors['sensor_type'] == sensor_type]
                plt.scatter(
                    subset['longitude'],
                    subset['latitude'],
                    c=[color_map[sensor_type]],
                    label=sensor_type,
                    s=100,
                    alpha=0.6,
                    edgecolors='black',
                    linewidth=1
                )
            
            plt.xlabel('Longitude', fontsize=12)
            plt.ylabel('Latitude', fontsize=12)
            plt.title('Sensor Locations', fontsize=14, fontweight='bold')
            plt.legend(loc='best')
            plt.grid(True, alpha=0.3)
            plt.axis('equal')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"✓ Saved sensor map to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Failed to plot sensor map: {e}")
    
    def plot_spatial_heatmap(self, column: str = 'value',
                            figsize: Tuple[int, int] = (10, 10),
                            save_path: Optional[str] = None):
        """
        Plot spatial heatmap
        
        Args:
            column: Column to visualize
            figsize: Figure size
            save_path: Optional path to save figure
        """
        try:
            gps_df = self.filter_gps_sensors()
            
            if gps_df.empty:
                logger.warning("No GPS data to plot")
                return
            
            plt.figure(figsize=figsize)
            
            # Create scatter plot with color based on value
            scatter = plt.scatter(
                gps_df['longitude'],
                gps_df['latitude'],
                c=gps_df[column],
                cmap='viridis',
                s=50,
                alpha=0.6,
                edgecolors='black',
                linewidth=0.5
            )
            
            plt.colorbar(scatter, label=column)
            plt.xlabel('Longitude', fontsize=12)
            plt.ylabel('Latitude', fontsize=12)
            plt.title(f'Spatial Heatmap: {column}', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3)
            plt.axis('equal')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"✓ Saved spatial heatmap to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Failed to plot spatial heatmap: {e}")
    
    def get_spatial_summary(self) -> str:
        """
        Generate spatial analysis summary
        
        Returns:
            Formatted summary report
        """
        try:
            report = []
            report.append("=" * 70)
            report.append("SPATIAL ANALYSIS REPORT")
            report.append("=" * 70)
            
            # Bounds
            if 'bounds' in self.spatial_results:
                bounds = self.spatial_results['bounds']
                report.append(f"\nGeographic Bounds:")
                report.append(f"  Latitude: {bounds['min_lat']:.4f} to {bounds['max_lat']:.4f}")
                report.append(f"  Longitude: {bounds['min_long']:.4f} to {bounds['max_long']:.4f}")
                report.append(f"  Center: ({bounds['center_lat']:.4f}, {bounds['center_long']:.4f})")
            
            # Statistics
            if 'statistics' in self.spatial_results:
                stats = self.spatial_results['statistics']
                report.append(f"\n--- Sensor Distribution ---")
                report.append(f"Total GPS Sensors: {stats.get('total_sensors', 'N/A')}")
                
                if 'sensor_type_distribution' in stats:
                    report.append(f"\nBy Type:")
                    for sensor_type, count in stats['sensor_type_distribution'].items():
                        report.append(f"  {sensor_type}: {count}")
            
            # Outliers
            if 'outliers' in self.spatial_results:
                outliers = self.spatial_results['outliers']
                report.append(f"\n--- Spatial Outliers ---")
                report.append(f"Total outliers: {len(outliers)}")
                if not outliers.empty:
                    for _, row in outliers.iterrows():
                        report.append(f"  {row['sensor_id']} ({row['sensor_type']})")
            
            report.append("\n" + "=" * 70)
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Failed to generate spatial summary: {e}")
            return "Error generating report"


def analyze_spatial_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Convenience function to perform spatial analysis
    
    Args:
        df: DataFrame with sensor data
        
    Returns:
        Dictionary with spatial analysis results
    """
    analysis = SpatialAnalysis(df)
    
    # Compute spatial analysis
    analysis.filter_gps_sensors()
    analysis.compute_bounds()
    analysis.compute_sensor_density()
    analysis.compute_spatial_statistics()
    analysis.detect_spatial_outliers()
    
    return analysis.spatial_results


def print_spatial_summary(df: pd.DataFrame):
    """
    Print spatial analysis summary
    
    Args:
        df: DataFrame with sensor data
    """
    analysis = SpatialAnalysis(df)
    analysis.filter_gps_sensors()
    analysis.compute_bounds()
    analysis.compute_spatial_statistics()
    print(analysis.get_spatial_summary())


if __name__ == "__main__":
    # Test with sample data
    from analytics.load_data import load_sample_data
    
    print("Loading sample data...")
    df = load_sample_data()
    
    # Add GPS coordinates for testing
    df['latitude'] = np.random.uniform(36.7, 36.8, len(df))
    df['longitude'] = np.random.uniform(10.2, 10.3, len(df))
    
    print("\nPerforming spatial analysis...")
    analysis = SpatialAnalysis(df)
    
    # Compute bounds
    bounds = analysis.compute_bounds()
    print(f"\nBounds: {bounds}")
    
    # Find nearby sensors
    nearby = analysis.find_nearby_sensors('sensor_000', radius_km=5.0)
    print(f"\nNearby sensors: {len(nearby)}")
    
    # Plot
    analysis.plot_sensor_map(save_path='results/sensor_map.png')
    analysis.plot_spatial_heatmap(column='value', save_path='results/spatial_heatmap.png')