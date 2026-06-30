"""
Dash Dashboard for Smart Agriculture Platform
"""
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(
    __name__,
    title="Smart Agriculture Dashboard",
    update_title="Loading...",
    suppress_callback_exceptions=True
)

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #f5f5f5;
                font-family: Arial, sans-serif;
            }
            .main-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background-color: #2e7d32;
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
            }
            .card {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .alert-critical {
                background-color: #ffebee;
                border-left: 4px solid #c62828;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            .alert-warning {
                background-color: #fff3e0;
                border-left: 4px solid #ef6c00;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            .metric-value {
                font-size: 2rem;
                font-weight: bold;
                color: #2e7d32;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


# Layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🌾 Smart Agriculture Dashboard", className="header"),
        html.P(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
               style={'textAlign': 'center', 'color': '#666'})
    ]),
    
    # Auto-refresh interval
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # 10 seconds in milliseconds
        n_intervals=0
    ),
    
    # Time range selector
    html.Div([
        html.Label("Time Range:"),
        dcc.Dropdown(
            id='time-range',
            options=[
                {'label': 'Last 1 hour', 'value': 1},
                {'label': 'Last 6 hours', 'value': 6},
                {'label': 'Last 12 hours', 'value': 12},
                {'label': 'Last 24 hours', 'value': 24},
                {'label': 'Last 48 hours', 'value': 48},
                {'label': 'Last 72 hours', 'value': 72}
            ],
            value=24,
            clearable=False,
            style={'width': '200px', 'display': 'inline-block', 'margin-right': '20px'}
        ),
        
        html.Label("Refresh Interval (seconds):"),
        dcc.Slider(
            id='refresh-interval',
            min=5,
            max=60,
            step=5,
            value=10,
            marks={i: str(i) for i in range(5, 61, 5)},
            style={'width': '300px', 'display': 'inline-block', 'vertical-align': 'middle'}
        )
    ], className="card", style={'display': 'flex', 'alignItems': 'center', 'gap': '20px'}),
    
    # Alerts Section
    html.Div([
        html.H3("🚨 Active Alerts"),
        html.Div(id='alerts-container')
    ], className="card"),
    
    # KPI Metrics
    html.Div([
        html.H3("📊 Key Performance Indicators"),
        html.Div([
            html.Div([
                html.H4("Active Sensors"),
                html.H2(id='kpi-sensors', className="metric-value")
            ], className="card", style={'width': '23%', 'display': 'inline-block', 'textAlign': 'center'}),
            
            html.Div([
                html.H4("Total Observations"),
                html.H2(id='kpi-observations', className="metric-value")
            ], className="card", style={'width': '23%', 'display': 'inline-block', 'textAlign': 'center'}),
            
            html.Div([
                html.H4("Avg Temperature"),
                html.H2(id='kpi-temperature', className="metric-value")
            ], className="card", style={'width': '23%', 'display': 'inline-block', 'textAlign': 'center'}),
            
            html.Div([
                html.H4("Avg Humidity"),
                html.H2(id='kpi-humidity', className="metric-value")
            ], className="card", style={'width': '23%', 'display': 'inline-block', 'textAlign': 'center'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
    ]),
    
    # Time Series Charts
    html.Div([
        html.H3("📈 Real-Time Monitoring"),
        
        # Temperature Chart
        html.Div([
            dcc.Graph(id='temperature-chart')
        ], className="card"),
        
        # Humidity Chart
        html.Div([
            dcc.Graph(id='humidity-chart')
        ], className="card"),
        
        # Soil Moisture Chart
        html.Div([
            dcc.Graph(id='soil-moisture-chart')
        ], className="card"),
        
        # pH Chart
        html.Div([
            dcc.Graph(id='ph-chart')
        ], className="card")
    ]),
    
    # GPS Map and Statistics
    html.Div([
        html.Div([
            html.H3("🗺️ Sensor Locations"),
            dcc.Graph(id='gps-map')
        ], className="card", style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.H3("📊 Statistics by Sensor Type"),
            html.Div(id='statistics-table')
        ], className="card", style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    
    # Footer
    html.Div([
        html.P("Smart Agriculture IoT Platform © 2024", 
               style={'textAlign': 'center', 'color': '#666', 'padding': '20px'})
    ])
], className="main-container")


# Callbacks
@app.callback(
    [Output('alerts-container', 'children'),
     Output('kpi-sensors', 'children'),
     Output('kpi-observations', 'children'),
     Output('kpi-temperature', 'children'),
     Output('kpi-humidity', 'children'),
     Output('temperature-chart', 'figure'),
     Output('humidity-chart', 'figure'),
     Output('soil-moisture-chart', 'figure'),
     Output('ph-chart', 'figure'),
     Output('gps-map', 'figure'),
     Output('statistics-table', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('time-range', 'value')]
)
def update_dashboard(n_intervals, time_range):
    """Update dashboard with latest data"""
    try:
        # Load data
        from api.database import get_sensor_data, get_latest_readings
        
        start_time = (datetime.now() - timedelta(hours=time_range)).isoformat()
        df = get_sensor_data(start_time=start_time, limit=10000)
        latest_df = get_latest_readings()
        
        if not df:
            return [html.P("No data available")] + ["N/A"] * 4 + [go.Figure()] * 5
        
        df = pd.DataFrame(df)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        if not latest_df:
            latest_df = pd.DataFrame()
        else:
            latest_df = pd.DataFrame(latest_df)
            latest_df['timestamp'] = pd.to_datetime(latest_df['timestamp'])
        
        # Check alerts
        alerts = check_alerts(df)
        alerts_components = display_alerts_dash(alerts)
        
        # KPIs
        num_sensors = latest_df['sensor_id'].nunique() if not latest_df.empty else 0
        num_observations = len(df)
        
        avg_temp = "N/A"
        if 'temperature' in df['sensor_type'].values:
            avg_temp = f"{df[df['sensor_type'] == 'temperature']['value'].mean():.1f}°C"
        
        avg_humidity = "N/A"
        if 'humidity' in df['sensor_type'].values:
            avg_humidity = f"{df[df['sensor_type'] == 'humidity']['value'].mean():.1f}%"
        
        # Temperature chart
        temp_fig = create_time_series_chart(
            df[df['sensor_type'] == 'temperature'] if 'temperature' in df['sensor_type'].values else pd.DataFrame(),
            'Temperature (°C)',
            'Temperature Over Time',
            '#ff6b6b'
        )
        
        # Humidity chart
        humidity_fig = create_time_series_chart(
            df[df['sensor_type'] == 'humidity'] if 'humidity' in df['sensor_type'].values else pd.DataFrame(),
            'Humidity (%)',
            'Humidity Over Time',
            '#4ecdc4'
        )
        
        # Soil moisture chart
        soil_fig = create_time_series_chart(
            df[df['sensor_type'] == 'soil_moisture'] if 'soil_moisture' in df['sensor_type'].values else pd.DataFrame(),
            'Soil Moisture (%)',
            'Soil Moisture Over Time',
            '#45b7d1'
        )
        
        # pH chart
        ph_fig = create_boxplot_chart(
            df[df['sensor_type'] == 'ph'] if 'ph' in df['sensor_type'].values else pd.DataFrame(),
            'pH Distribution',
            '#96ceb4'
        )
        
        # GPS Map
        gps_fig = create_map_chart(latest_df)
        
        # Statistics table
        stats_table = create_statistics_table(df)
        
        return (alerts_components, num_sensors, f"{num_observations:,}", 
                avg_temp, avg_humidity, temp_fig, humidity_fig, 
                soil_fig, ph_fig, gps_fig, stats_table)
        
    except Exception as e:
        logger.error(f"Dashboard update failed: {e}")
        return [html.P(f"Error: {str(e)}")] + ["Error"] * 4 + [go.Figure()] * 5


def check_alerts(df):
    """Check for alert conditions"""
    alerts = []
    
    if df.empty:
        return alerts
    
    # Temperature alerts
    if 'temperature' in df['sensor_type'].values:
        temp_data = df[df['sensor_type'] == 'temperature']
        if not temp_data.empty:
            latest_temp = temp_data.groupby('sensor_id')['value'].last()
            for sensor_id, temp in latest_temp.items():
                if temp > 35:
                    alerts.append({
                        'severity': 'critical',
                        'sensor_id': sensor_id,
                        'type': 'Temperature',
                        'message': f'High temperature detected: {temp:.1f}°C'
                    })
                elif temp > 30:
                    alerts.append({
                        'severity': 'warning',
                        'sensor_id': sensor_id,
                        'type': 'Temperature',
                        'message': f'Elevated temperature: {temp:.1f}°C'
                    })
    
    # Humidity alerts
    if 'humidity' in df['sensor_type'].values:
        humidity_data = df[df['sensor_type'] == 'humidity']
        if not humidity_data.empty:
            latest_humidity = humidity_data.groupby('sensor_id')['value'].last()
            for sensor_id, humidity in latest_humidity.items():
                if humidity < 40:
                    alerts.append({
                        'severity': 'warning',
                        'sensor_id': sensor_id,
                        'type': 'Humidity',
                        'message': f'Low humidity: {humidity:.1f}% - Irrigation recommended'
                    })
    
    return alerts


def display_alerts_dash(alerts):
    """Display alerts in Dash format"""
    if not alerts:
        return html.P("✓ No active alerts", style={'color': 'green'})
    
    components = []
    
    critical_alerts = [a for a in alerts if a['severity'] == 'critical']
    warning_alerts = [a for a in alerts if a['severity'] == 'warning']
    
    for alert in critical_alerts:
        components.append(html.Div([
            html.Strong(f"{alert['type']} - {alert['sensor_id']}"),
            html.Br(),
            alert['message']
        ], className="alert-critical"))
    
    for alert in warning_alerts:
        components.append(html.Div([
            html.Strong(f"{alert['type']} - {alert['sensor_id']}"),
            html.Br(),
            alert['message']
        ], className="alert-warning"))
    
    return components


def create_time_series_chart(df, y_label, title, color):
    """Create time series chart"""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False, font=dict(size=20))
        return fig
    
    fig = px.line(
        df,
        x='timestamp',
        y='value',
        color='sensor_id',
        title=title,
        labels={'value': y_label, 'timestamp': 'Time'},
        template='plotly_white'
    )
    
    fig.update_layout(
        hovermode='x unified',
        xaxis_title="Time",
        yaxis_title=y_label,
        height=400
    )
    
    return fig


def create_boxplot_chart(df, title, color):
    """Create boxplot chart"""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False, font=dict(size=20))
        return fig
    
    fig = px.box(
        df,
        y='value',
        title=title,
        template='plotly_white'
    )
    
    fig.update_layout(height=400)
    
    return fig


def create_map_chart(df):
    """Create GPS map"""
    if df.empty or 'latitude' not in df.columns or 'longitude' not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No GPS data available", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False, font=dict(size=20))
        return fig
    
    gps_df = df[df['latitude'].notna() & df['longitude'].notna()]
    
    if gps_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No GPS data available", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False, font=dict(size=20))
        return fig
    
    fig = px.scatter_mapbox(
        gps_df,
        lat='latitude',
        lon='longitude',
        hover_name='sensor_id',
        hover_data=['sensor_type', 'value'],
        zoom=10,
        height=400,
        template='plotly_white'
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        title="Sensor Locations"
    )
    
    return fig


def create_statistics_table(df):
    """Create statistics table"""
    if df.empty:
        return html.P("No data available")
    
    stats = df.groupby('sensor_type').agg({
        'value': ['count', 'mean', 'std', 'min', 'max']
    }).round(2)
    
    stats.columns = ['Count', 'Mean', 'Std', 'Min', 'Max']
    stats = stats.reset_index()
    
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in stats.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(stats.iloc[i][col]) for col in stats.columns
            ]) for i in range(len(stats))
        ])
    ], style={'width': '100%', 'borderCollapse': 'collapse'})


if __name__ == "__main__":
    print("Starting Dash Dashboard...")
    print("="*80)
    print("Dashboard URL: http://localhost:8050")
    print("="*80)
    
    app.run_server(
        host='0.0.0.0',
        port=8050,
        debug=True
    )