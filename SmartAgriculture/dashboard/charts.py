"""
Chart Generation Module for Smart Agriculture Dashboard
"""
import pandas as pd
import numpy as np
import logging
from typing import Optional, List
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generate various charts for the dashboard"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize chart generator
        
        Args:
            df: DataFrame with sensor data
        """
        self.df = df
        self.color_scheme = {
            'temperature': '#ff6b6b',
            'humidity': '#4ecdc4',
            'soil_moisture': '#45b7d1',
            'ph': '#96ceb4',
            'rainfall': '#74b9ff',
            'light': '#fdcb6e',
            'wind': '#e17055',
            'water_quality': '#00b894',
            'gps': '#6c5ce7',
            'animal': '#fd79a8'
        }
    
    def create_time_series_chart(self, sensor_type: str, 
                                 title: str = None,
                                 y_label: str = None,
                                 color: str = None) -> go.Figure:
        """
        Create time series chart for a sensor type
        
        Args:
            sensor_type: Type of sensor
            title: Chart title
            y_label: Y-axis label
            color: Line color
            
        Returns:
            Plotly figure
        """
        try:
            if sensor_type not in self.df['sensor_type'].values:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"No {sensor_type} data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16)
                )
                return fig
            
            sensor_df = self.df[self.df['sensor_type'] == sensor_type].copy()
            sensor_df = sensor_df.sort_values('timestamp')
            
            if title is None:
                title = f"{sensor_type.replace('_', ' ').title()} Over Time"
            
            if y_label is None:
                y_label = sensor_type.replace('_', ' ').title()
            
            if color is None:
                color = self.color_scheme.get(sensor_type, '#2e7d32')
            
            fig = px.line(
                sensor_df,
                x='timestamp',
                y='value',
                color='sensor_id',
                title=title,
                labels={'value': y_label, 'timestamp': 'Time'},
                template='plotly_white',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(
                hovermode='x unified',
                xaxis_title="Time",
                yaxis_title=y_label,
                height=400,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create time series chart: {e}")
            return go.Figure()
    
    def create_multi_sensor_chart(self, sensor_types: List[str],
                                  title: str = "Multi-Sensor Comparison",
                                  normalize: bool = False) -> go.Figure:
        """
        Create chart comparing multiple sensor types
        
        Args:
            sensor_types: List of sensor types to compare
            title: Chart title
            normalize: Whether to normalize values
            
        Returns:
            Plotly figure
        """
        try:
            fig = make_subplots(
                rows=len(sensor_types),
                cols=1,
                subplot_titles=sensor_types,
                vertical_spacing=0.05
            )
            
            for idx, sensor_type in enumerate(sensor_types, 1):
                if sensor_type not in self.df['sensor_type'].values:
                    continue
                
                sensor_df = self.df[self.df['sensor_type'] == sensor_type].copy()
                sensor_df = sensor_df.sort_values('timestamp')
                
                values = sensor_df['value'].values
                
                if normalize:
                    values = (values - values.min()) / (values.max() - values.min())
                
                for sensor_id in sensor_df['sensor_id'].unique():
                    sensor_data = sensor_df[sensor_df['sensor_id'] == sensor_id]
                    fig.add_trace(
                        go.Scatter(
                            x=sensor_data['timestamp'],
                            y=sensor_data['value'],
                            name=sensor_id,
                            mode='lines',
                            line=dict(width=2)
                        ),
                        row=idx, col=1
                    )
            
            fig.update_layout(
                title=title,
                height=300 * len(sensor_types),
                showlegend=False,
                template='plotly_white'
            )
            
            fig.update_xaxes(title_text="Time")
            fig.update_yaxes(title_text="Value")
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create multi-sensor chart: {e}")
            return go.Figure()
    
    def create_boxplot_chart(self, sensor_type: str,
                            title: str = None,
                            color: str = None) -> go.Figure:
        """
        Create boxplot for sensor data distribution
        
        Args:
            sensor_type: Type of sensor
            title: Chart title
            color: Box color
            
        Returns:
            Plotly figure
        """
        try:
            if sensor_type not in self.df['sensor_type'].values:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"No {sensor_type} data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16)
                )
                return fig
            
            sensor_df = self.df[self.df['sensor_type'] == sensor_type]
            
            if title is None:
                title = f"{sensor_type.replace('_', ' ').title()} Distribution"
            
            if color is None:
                color = self.color_scheme.get(sensor_type, '#2e7d32')
            
            fig = px.box(
                sensor_df,
                y='value',
                title=title,
                template='plotly_white',
                points='outliers'
            )
            
            fig.update_layout(
                yaxis_title=sensor_type.replace('_', ' ').title(),
                height=400,
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create boxplot: {e}")
            return go.Figure()
    
    def create_histogram_chart(self, sensor_type: str,
                              title: str = None,
                              bins: int = 30) -> go.Figure:
        """
        Create histogram for sensor data
        
        Args:
            sensor_type: Type of sensor
            title: Chart title
            bins: Number of bins
            
        Returns:
            Plotly figure
        """
        try:
            if sensor_type not in self.df['sensor_type'].values:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"No {sensor_type} data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16)
                )
                return fig
            
            sensor_df = self.df[self.df['sensor_type'] == sensor_type]
            
            if title is None:
                title = f"{sensor_type.replace('_', ' ').title()} Distribution (Histogram)"
            
            fig = px.histogram(
                sensor_df,
                x='value',
                title=title,
                nbins=bins,
                template='plotly_white',
                color_discrete_sequence=[self.color_scheme.get(sensor_type, '#2e7d32')]
            )
            
            fig.update_layout(
                xaxis_title=sensor_type.replace('_', ' ').title(),
                yaxis_title="Frequency",
                height=400,
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create histogram: {e}")
            return go.Figure()
    
    def create_scatter_chart(self, x_sensor: str, y_sensor: str,
                            title: str = None) -> go.Figure:
        """
        Create scatter plot between two sensor types
        
        Args:
            x_sensor: X-axis sensor type
            y_sensor: Y-axis sensor type
            title: Chart title
            
        Returns:
            Plotly figure
        """
        try:
            if x_sensor not in self.df['sensor_type'].values or y_sensor not in self.df['sensor_type'].values:
                fig = go.Figure()
                fig.add_annotation(
                    text="Data not available for one or both sensors",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16)
                )
                return fig
            
            # Merge data on timestamp
            x_df = self.df[self.df['sensor_type'] == x_sensor][['timestamp', 'value']].rename(
                columns={'value': 'x_value'}
            )
            y_df = self.df[self.df['sensor_type'] == y_sensor][['timestamp', 'value']].rename(
                columns={'value': 'y_value'}
            )
            
            merged_df = pd.merge(x_df, y_df, on='timestamp', how='inner')
            
            if title is None:
                title = f"{y_sensor.replace('_', ' ').title()} vs {x_sensor.replace('_', ' ').title()}"
            
            fig = px.scatter(
                merged_df,
                x='x_value',
                y='y_value',
                title=title,
                labels={'x_value': x_sensor.replace('_', ' ').title(),
                       'y_value': y_sensor.replace('_', ' ').title()},
                template='plotly_white',
                opacity=0.6
            )
            
            # Add trend line
            z = np.polyfit(merged_df['x_value'], merged_df['y_value'], 1)
            p = np.poly1d(z)
            fig.add_trace(
                go.Scatter(
                    x=merged_df['x_value'],
                    y=p(merged_df['x_value']),
                    mode='lines',
                    name='Trend',
                    line=dict(color='red', dash='dash')
                )
            )
            
            fig.update_layout(height=500)
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create scatter chart: {e}")
            return go.Figure()
    
    def create_heatmap_chart(self, sensor_type: str,
                            hours: int = 24,
                            title: str = None) -> go.Figure:
        """
        Create heatmap showing sensor activity by hour and day
        
        Args:
            sensor_type: Type of sensor
            hours: Number of hours to show
            title: Chart title
            
        Returns:
            Plotly figure
        """
        try:
            if sensor_type not in self.df['sensor_type'].values:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"No {sensor_type} data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16)
                )
                return fig
            
            sensor_df = self.df[self.df['sensor_type'] == sensor_type].copy()
            sensor_df = sensor_df.sort_values('timestamp')
            
            # Filter by hours
            start_time = datetime.now() - timedelta(hours=hours)
            sensor_df = sensor_df[sensor_df['timestamp'] >= start_time]
            
            if title is None:
                title = f"{sensor_type.replace('_', ' ').title()} Activity Heatmap"
            
            # Create pivot table
            sensor_df['hour'] = sensor_df['timestamp'].dt.hour
            sensor_df['minute'] = sensor_df['timestamp'].dt.minute
            
            # Aggregate by hour
            hourly_data = sensor_df.groupby(['hour', 'sensor_id'])['value'].mean().reset_index()
            
            fig = px.density_heatmap(
                hourly_data,
                x='hour',
                y='sensor_id',
                z='value',
                title=title,
                labels={'hour': 'Hour of Day', 'sensor_id': 'Sensor ID', 'value': 'Value'},
                template='plotly_white',
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(height=400)
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create heatmap: {e}")
            return go.Figure()
    
    def create_correlation_matrix(self, sensor_types: List[str] = None,
                                 title: str = "Sensor Correlation Matrix") -> go.Figure:
        """
        Create correlation matrix between sensor types
        
        Args:
            sensor_types: List of sensor types (None for all)
            title: Chart title
            
        Returns:
            Plotly figure
        """
        try:
            if sensor_types is None:
                sensor_types = self.df['sensor_type'].unique().tolist()
            
            # Pivot data
            pivot_df = self.df[self.df['sensor_type'].isin(sensor_types)].pivot_table(
                index='timestamp',
                columns='sensor_type',
                values='value',
                aggfunc='mean'
            )
            
            # Calculate correlation
            corr_matrix = pivot_df.corr()
            
            fig = px.imshow(
                corr_matrix,
                title=title,
                template='plotly_white',
                color_continuous_scale='RdBu_r',
                aspect='auto',
                labels=dict(color='Correlation')
            )
            
            fig.update_layout(
                height=600,
                xaxis_title="Sensor Type",
                yaxis_title="Sensor Type"
            )
            
            # Add correlation values
            for i in range(len(corr_matrix)):
                for j in range(len(corr_matrix)):
                    fig.add_annotation(
                        x=i, y=j,
                        text=f"{corr_matrix.iloc[i, j]:.2f}",
                        showarrow=False,
                        font=dict(color='white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black')
                    )
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create correlation matrix: {e}")
            return go.Figure()
    
    def create_gauge_chart(self, sensor_type: str, sensor_id: str,
                          min_val: float, max_val: float,
                          title: str = None) -> go.Figure:
        """
        Create gauge chart for current sensor value
        
        Args:
            sensor_type: Type of sensor
            sensor_id: Sensor ID
            min_val: Minimum value for gauge
            max_val: Maximum value for gauge
            title: Chart title
            
        Returns:
            Plotly figure
        """
        try:
            sensor_df = self.df[
                (self.df['sensor_type'] == sensor_type) & 
                (self.df['sensor_id'] == sensor_id)
            ].copy()
            
            if sensor_df.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="No data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16)
                )
                return fig
            
            latest_value = sensor_df.sort_values('timestamp')['value'].iloc[-1]
            
            if title is None:
                title = f"{sensor_type.replace('_', ' ').title()} - {sensor_id}"
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=latest_value,
                title={'text': title},
                delta={'reference': sensor_df['value'].mean()},
                gauge={
                    'axis': {'range': [min_val, max_val]},
                    'bar': {'color': self.color_scheme.get(sensor_type, '#2e7d32')},
                    'steps': [
                        {'range': [min_val, min_val + (max_val - min_val) * 0.33], 
                         'color': "lightgray"},
                        {'range': [min_val + (max_val - min_val) * 0.33, 
                                  min_val + (max_val - min_val) * 0.66], 
                         'color': "gray"},
                        {'range': [min_val + (max_val - min_val) * 0.66, max_val], 
                         'color': "darkgray"}
                    ],
                    'threshold': {
                        'line': {'color': 'red', 'width': 4},
                        'thickness': 0.75,
                        'value': max_val * 0.9
                    }
                }
            ))
            
            fig.update_layout(height=400)
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create gauge chart: {e}")
            return go.Figure()
    
    def create_bar_chart(self, sensor_type: str,
                        aggregation: str = 'mean',
                        title: str = None) -> go.Figure:
        """
        Create bar chart for sensor data by location or sensor_id
        
        Args:
            sensor_type: Type of sensor
            aggregation: Aggregation function ('mean', 'sum', 'count', 'min', 'max')
            title: Chart title
            
        Returns:
            Plotly figure
        """
        try:
            if sensor_type not in self.df['sensor_type'].values:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"No {sensor_type} data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16)
                )
                return fig
            
            sensor_df = self.df[self.df['sensor_type'] == sensor_type]
            
            # Aggregate by location
            agg_df = sensor_df.groupby('location').agg({
                'value': aggregation
            }).reset_index()
            
            if title is None:
                title = f"{sensor_type.replace('_', ' ').title()} by Location ({aggregation})"
            
            fig = px.bar(
                agg_df,
                x='location',
                y='value',
                title=title,
                template='plotly_white',
                color='value',
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(
                xaxis_title="Location",
                yaxis_title=sensor_type.replace('_', ' ').title(),
                height=400,
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create bar chart: {e}")
            return go.Figure()


def create_dashboard_charts(df: pd.DataFrame) -> dict:
    """
    Create all dashboard charts
    
    Args:
        df: DataFrame with sensor data
        
    Returns:
        Dictionary of chart figures
    """
    try:
        generator = ChartGenerator(df)
        charts = {}
        
        # Time series charts
        sensor_types = df['sensor_type'].unique() if not df.empty else []
        
        for sensor_type in sensor_types:
            charts[f'{sensor_type}_timeseries'] = generator.create_time_series_chart(sensor_type)
            charts[f'{sensor_type}_boxplot'] = generator.create_boxplot_chart(sensor_type)
            charts[f'{sensor_type}_histogram'] = generator.create_histogram_chart(sensor_type)
        
        # Correlation matrix
        if len(sensor_types) > 1:
            charts['correlation_matrix'] = generator.create_correlation_matrix()
        
        return charts
        
    except Exception as e:
        logger.error(f"Failed to create dashboard charts: {e}")
        return {}


if __name__ == "__main__":
    # Test chart generation
    print("Testing Chart Generator...")
    print("="*80)
    
    # Create sample data
    from datetime import datetime, timedelta
    
    np.random.seed(42)
    
    timestamps = [datetime.now() - timedelta(hours=i) for i in range(100, 0, -1)]
    
    data = []
    
    # Temperature data
    for i, ts in enumerate(timestamps):
        data.append({
            'sensor_id': 'TEMP_001',
            'sensor_type': 'temperature',
            'value': 25 + 5 * np.sin(i / 10) + np.random.normal(0, 1),
            'timestamp': ts,
            'location': 'Field A'
        })
    
    # Humidity data
    for i, ts in enumerate(timestamps):
        data.append({
            'sensor_id': 'HUM_001',
            'sensor_type': 'humidity',
            'value': 70 + 10 * np.cos(i / 10) + np.random.normal(0, 2),
            'timestamp': ts,
            'location': 'Field A'
        })
    
    df = pd.DataFrame(data)
    
    # Create charts
    generator = ChartGenerator(df)
    
    print("\n1. Temperature Time Series:")
    fig1 = generator.create_time_series_chart('temperature')
    fig1.show()
    
    print("\n2. Humidity Boxplot:")
    fig2 = generator.create_boxplot_chart('humidity')
    fig2.show()
    
    print("\n3. Temperature Histogram:")
    fig3 = generator.create_histogram_chart('temperature')
    fig3.show()
    
    print("\n4. Scatter Plot (Temperature vs Humidity):")
    fig4 = generator.create_scatter_chart('temperature', 'humidity')
    fig4.show()
    
    print("\n5. Correlation Matrix:")
    fig5 = generator.create_correlation_matrix()
    fig5.show()
    
    print("\n✓ Chart generation test complete!")