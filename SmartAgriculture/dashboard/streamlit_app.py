"""
Streamlit Dashboard for Smart Agriculture Platform
"""
import streamlit as st
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# Configure page
st.set_page_config(
    page_title="Smart Agriculture Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2e7d32;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f4f0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2e7d32;
    }
    .alert-critical {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #c62828;
    }
    .alert-warning {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ef6c00;
    }
    .alert-info {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1565c0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_sensor_data(hours=24):
    """Load sensor data from database"""
    try:
        from api.database import get_sensor_data
        from datetime import datetime
        
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        data = get_sensor_data(
            start_time=start_time,
            limit=10000
        )
        
        if data:
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        return pd.DataFrame()
        
    except Exception as e:
        logger.error(f"Failed to load sensor data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=60)
def load_latest_readings():
    """Load latest sensor readings"""
    try:
        from api.database import get_latest_readings
        
        data = get_latest_readings()
        
        if data:
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        return pd.DataFrame()
        
    except Exception as e:
        logger.error(f"Failed to load latest readings: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=60)
def load_sensors():
    """Load sensor list"""
    try:
        from api.database import get_sensors
        
        data = get_sensors()
        
        if data:
            return pd.DataFrame(data)
        return pd.DataFrame()
        
    except Exception as e:
        logger.error(f"Failed to load sensors: {e}")
        return pd.DataFrame()


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
                        'message': f'High temperature detected: {temp:.1f}°C',
                        'value': temp,
                        'threshold': 35
                    })
                elif temp > 30:
                    alerts.append({
                        'severity': 'warning',
                        'sensor_id': sensor_id,
                        'type': 'Temperature',
                        'message': f'Elevated temperature: {temp:.1f}°C',
                        'value': temp,
                        'threshold': 30
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
                        'message': f'Low humidity: {humidity:.1f}% - Irrigation recommended',
                        'value': humidity,
                        'threshold': 40
                    })
    
    # Soil moisture alerts
    if 'soil_moisture' in df['sensor_type'].values:
        soil_data = df[df['sensor_type'] == 'soil_moisture']
        if not soil_data.empty:
            latest_soil = soil_data.groupby('sensor_id')['value'].last()
            for sensor_id, soil in latest_soil.items():
                if soil < 30:
                    alerts.append({
                        'severity': 'critical',
                        'sensor_id': sensor_id,
                        'type': 'Soil Moisture',
                        'message': f'Very low soil moisture: {soil:.1f}%',
                        'value': soil,
                        'threshold': 30
                    })
    
    return alerts


def display_alerts(alerts):
    """Display alerts in dashboard"""
    if not alerts:
        st.success("✓ No active alerts")
        return
    
    critical_alerts = [a for a in alerts if a['severity'] == 'critical']
    warning_alerts = [a for a in alerts if a['severity'] == 'warning']
    
    if critical_alerts:
        st.error(f"⚠️ {len(critical_alerts)} Critical Alert(s)")
        for alert in critical_alerts:
            st.markdown(f"""
            <div class="alert-critical">
                <strong>{alert['type']} - {alert['sensor_id']}</strong><br>
                {alert['message']}
            </div>
            """, unsafe_allow_html=True)
    
    if warning_alerts:
        st.warning(f"⚡ {len(warning_alerts)} Warning(s)")
        for alert in warning_alerts:
            st.markdown(f"""
            <div class="alert-warning">
                <strong>{alert['type']} - {alert['sensor_id']}</strong><br>
                {alert['message']}
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main dashboard function"""
    # Header
    st.markdown('<div class="main-header">🌾 Smart Agriculture Dashboard</div>', 
                unsafe_allow_html=True)
    st.markdown(f"**Last updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Time range selector
        time_range = st.selectbox(
            "Time Range",
            options=[1, 6, 12, 24, 48, 72],
            index=3,
            format_func=lambda x: f"Last {x} hours"
        )
        
        # Auto-refresh
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        refresh_interval = st.slider("Refresh interval (seconds)", 5, 60, 10)
        
        st.divider()
        
        # Sensor filters
        st.subheader("Sensor Filters")
        show_temperature = st.checkbox("Temperature", value=True)
        show_humidity = st.checkbox("Humidity", value=True)
        show_soil_moisture = st.checkbox("Soil Moisture", value=True)
        show_ph = st.checkbox("pH", value=True)
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_sensor_data(hours=time_range)
        latest_df = load_latest_readings()
        sensors_df = load_sensors()
    
    if df.empty:
        st.warning("No data available. Please check database connection.")
        return
    
    # Check alerts
    alerts = check_alerts(df)
    
    # Alerts section
    st.header("🚨 Active Alerts")
    display_alerts(alerts)
    
    st.divider()
    
    # KPI Metrics
    st.header("📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        num_sensors = latest_df['sensor_id'].nunique() if not latest_df.empty else 0
        st.metric(
            label="Active Sensors",
            value=num_sensors,
            delta=None
        )
    
    with col2:
        num_observations = len(df)
        st.metric(
            label="Total Observations",
            value=f"{num_observations:,}",
            delta=None
        )
    
    with col3:
        if 'temperature' in df['sensor_type'].values:
            avg_temp = df[df['sensor_type'] == 'temperature']['value'].mean()
            st.metric(
                label="Avg Temperature",
                value=f"{avg_temp:.1f}°C",
                delta=None
            )
        else:
            st.metric(label="Avg Temperature", value="N/A")
    
    with col4:
        if 'humidity' in df['sensor_type'].values:
            avg_humidity = df[df['sensor_type'] == 'humidity']['value'].mean()
            st.metric(
                label="Avg Humidity",
                value=f"{avg_humidity:.1f}%",
                delta=None
            )
        else:
            st.metric(label="Avg Humidity", value="N/A")
    
    st.divider()
    
    # Time Series Charts
    st.header("📈 Real-Time Monitoring")
    
    # Temperature chart
    if show_temperature and 'temperature' in df['sensor_type'].values:
        st.subheader("Temperature")
        temp_df = df[df['sensor_type'] == 'temperature']
        
        fig = px.line(
            temp_df,
            x='timestamp',
            y='value',
            color='sensor_id',
            title="Temperature Over Time",
            labels={'value': 'Temperature (°C)', 'timestamp': 'Time'},
            template='plotly_white'
        )
        
        fig.update_layout(
            hovermode='x unified',
            xaxis_title="Time",
            yaxis_title="Temperature (°C)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Humidity chart
    if show_humidity and 'humidity' in df['sensor_type'].values:
        st.subheader("Humidity")
        humidity_df = df[df['sensor_type'] == 'humidity']
        
        fig = px.line(
            humidity_df,
            x='timestamp',
            y='value',
            color='sensor_id',
            title="Humidity Over Time",
            labels={'value': 'Humidity (%)', 'timestamp': 'Time'},
            template='plotly_white'
        )
        
        fig.update_layout(
            hovermode='x unified',
            xaxis_title="Time",
            yaxis_title="Humidity (%)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Soil Moisture chart
    if show_soil_moisture and 'soil_moisture' in df['sensor_type'].values:
        st.subheader("Soil Moisture")
        soil_df = df[df['sensor_type'] == 'soil_moisture']
        
        fig = px.line(
            soil_df,
            x='timestamp',
            y='value',
            color='sensor_id',
            title="Soil Moisture Over Time",
            labels={'value': 'Soil Moisture (%)', 'timestamp': 'Time'},
            template='plotly_white'
        )
        
        fig.update_layout(
            hovermode='x unified',
            xaxis_title="Time",
            yaxis_title="Soil Moisture (%)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # pH Boxplot
    if show_ph and 'ph' in df['sensor_type'].values:
        st.subheader("pH Distribution")
        ph_df = df[df['sensor_type'] == 'ph']
        
        fig = px.box(
            ph_df,
            y='value',
            title="pH Distribution",
            labels={'value': 'pH'},
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # GPS Map
    if not latest_df.empty and 'latitude' in latest_df.columns and 'longitude' in latest_df.columns:
        st.header("🗺️ Sensor Locations")
        
        gps_df = latest_df[latest_df['latitude'].notna() & latest_df['longitude'].notna()]
        
        if not gps_df.empty:
            st.map(gps_df[['latitude', 'longitude']])
    
    st.divider()
    
    # Latest Readings Table
    st.header("📋 Latest Readings")
    
    if not latest_df.empty:
        display_df = latest_df[['sensor_id', 'sensor_type', 'value', 'unit', 'timestamp', 'location']].copy()
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(display_df, use_container_width=True)
    
    st.divider()
    
    # Statistics
    st.header("📊 Statistics")
    
    if not df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("By Sensor Type")
            stats = df.groupby('sensor_type').agg({
                'value': ['count', 'mean', 'std', 'min', 'max']
            }).round(2)
            stats.columns = ['Count', 'Mean', 'Std', 'Min', 'Max']
            st.dataframe(stats, use_container_width=True)
        
        with col2:
            st.subheader("By Location")
            location_stats = df.groupby('location').agg({
                'value': ['count', 'mean']
            }).round(2)
            location_stats.columns = ['Count', 'Mean Value']
            st.dataframe(location_stats, use_container_width=True)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


def main_old():
    """Legacy main function"""
    st.title("Smart Agriculture Dashboard")
    st.write("Real-time monitoring")
    
    # Load data
    try:
        from api.database import get_db
        
        db = get_db()
        
        # Read from PostgreSQL
        import pandas as pd
        df = pd.read_sql("SELECT * FROM sensor_data", db.postgres_engine)
        
        st.dataframe(df.head())
        
        # Temperature chart
        if 'sensor_type' in df.columns and 'temperature' in df['sensor_type'].values:
            temperature = df[df.sensor_type == "temperature"]
            
            fig = px.line(
                temperature,
                x="timestamp",
                y="value",
                title="Temperature Over Time"
            )
            
            st.plotly_chart(fig)
        
        # Humidity chart
        if 'sensor_type' in df.columns and 'humidity' in df['sensor_type'].values:
            humidity = df[df.sensor_type == "humidity"]
            
            fig = px.line(
                humidity,
                x="timestamp",
                y="value",
                title="Humidity Over Time"
            )
            
            st.plotly_chart(fig)
        
        # pH boxplot
        if 'sensor_type' in df.columns and 'ph' in df['sensor_type'].values:
            ph = df[df.sensor_type == "ph"]
            
            fig = px.box(ph, y="value", title="pH Distribution")
            st.plotly_chart(fig)
        
        # GPS Map
        if 'latitude' in df.columns and 'longitude' in df.columns:
            gps = df[['latitude', 'longitude']].dropna()
            if not gps.empty:
                st.map(gps)
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'temperature' in df['sensor_type'].values:
                temp_mean = df[df.sensor_type == "temperature"]['value'].mean()
                st.metric("Average Temperature", f"{temp_mean:.2f}°C")
        
        with col2:
            if 'humidity' in df['sensor_type'].values:
                humidity_mean = df[df.sensor_type == "humidity"]['value'].mean()
                st.metric("Average Humidity", f"{humidity_mean:.2f}%")
        
        with col3:
            num_sensors = df['sensor_id'].nunique()
            st.metric("Number of Sensors", num_sensors)
        
        # Alerts
        st.subheader("Alerts")
        
        if 'temperature' in df['sensor_type'].values:
            temp_max = df[df.sensor_type == "temperature"]['value'].max()
            if temp_max > 35:
                st.error(f"⚠️ Alert: High temperature detected ({temp_max:.1f}°C)")
        
        if 'humidity' in df['sensor_type'].values:
            humidity_mean = df[df.sensor_type == "humidity"]['value'].mean()
            if humidity_mean < 40:
                st.warning(f"💧 Low humidity detected ({humidity_mean:.1f}%) - Irrigation recommended")
        
        # Save to CSV
        if st.button("Export to CSV"):
            df.to_csv("results/dashboard.csv", index=False)
            st.success("Data exported to results/dashboard.csv")
        
    except Exception as e:
        st.error(f"Error loading data: {e}")


if __name__ == "__main__":
    main()