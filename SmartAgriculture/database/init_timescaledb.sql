-- TimescaleDB Database Initialization Script
-- Creates hypertables for time-series sensor data

-- Enable TimescaleDB extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Drop existing hypertables if needed (for clean setup)
-- DROP TABLE IF EXISTS temperature_metrics CASCADE;
-- DROP TABLE IF EXISTS humidity_metrics CASCADE;
-- DROP TABLE IF EXISTS soil_moisture_metrics CASCADE;
-- DROP TABLE IF EXISTS ph_metrics CASCADE;
-- DROP TABLE IF EXISTS rainfall_metrics CASCADE;
-- DROP TABLE IF EXISTS light_metrics CASCADE;
-- DROP TABLE IF EXISTS wind_metrics CASCADE;
-- DROP TABLE IF EXISTS water_quality_metrics CASCADE;
-- DROP TABLE IF EXISTS gps_metrics CASCADE;
-- DROP TABLE IF EXISTS animal_metrics CASCADE;

-- ============================================
-- TEMPERATURE METRICS
-- ============================================
CREATE TABLE IF NOT EXISTS temperature_metrics (
    time TIMESTAMP NOT NULL,
    sensor_id VARCHAR(255) NOT NULL,
    value FLOAT,
    unit VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT create_hypertable('temperature_metrics', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_temperature_sensor_id 
ON temperature_metrics(sensor_id);

CREATE INDEX IF NOT EXISTS idx_temperature_time 
ON temperature_metrics(time DESC);

CREATE INDEX IF NOT EXISTS idx_temperature_metadata 
ON temperature_metrics USING GIN (metadata);

-- ============================================
-- HUMIDITY METRICS
-- ============================================
CREATE TABLE IF NOT EXISTS humidity_metrics (
    time TIMESTAMP NOT NULL,
    sensor_id VARCHAR(255) NOT NULL,
    value FLOAT,
    unit VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT create_hypertable('humidity_metrics', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_humidity_sensor_id 
ON humidity_metrics(sensor_id);

CREATE INDEX IF NOT EXISTS idx_humidity_time 
ON humidity_metrics(time DESC);

CREATE INDEX IF NOT EXISTS idx_humidity_metadata 
ON humidity_metrics USING GIN (metadata);

-- ============================================
-- SOIL MOISTURE METRICS
-- ============================================
CREATE TABLE IF NOT EXISTS soil_moisture_metrics (
    time TIMESTAMP NOT NULL,
    sensor_id VARCHAR(255) NOT NULL,
    value FLOAT,
    unit VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT create_hypertable('soil_moisture_metrics', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_soil_moisture_sensor_id 
ON soil_moisture_metrics(sensor_id);

CREATE INDEX IF NOT EXISTS idx_soil_moisture_time 
ON soil_moisture_metrics(time DESC);

-- ============================================
-- pH METRICS
-- ============================================
CREATE TABLE IF NOT EXISTS ph_metrics (
    time TIMESTAMP NOT NULL,
    sensor_id VARCHAR(255) NOT NULL,
    value FLOAT,
    unit VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT create_hypertable('ph_metrics', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_ph_sensor_id 
ON ph_metrics(sensor_id);

CREATE INDEX IF NOT EXISTS idx_ph_time 
ON ph_metrics(time DESC);

-- ============================================
-- RAINFALL METRICS
-- ============================================
CREATE TABLE IF NOT EXISTS rainfall_metrics (
    time TIMESTAMP NOT NULL,
    sensor_id VARCHAR(255) NOT NULL,
    value FLOAT,
    unit VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT create_hypertable('rainfall_metrics', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_rainfall_sensor_id 
ON rainfall_metrics(sensor_id);

CREATE INDEX IF NOT EXISTS idx_rainfall_time 
ON rainfall_metrics(time DESC);

-- ============================================
-- LIGHT METRICS
-- ============================================
CREATE TABLE IF NOT EXISTS light_metrics (
    time TIMESTAMP NOT NULL,
    sensor_id VARCHAR(255) NOT NULL,
    value FLOAT,
    unit VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT create_hypertable('light_metrics', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_light_sensor_id 
ON light_metrics(sensor_id);

CREATE INDEX IF NOT EXISTS idx_light_time 
ON light_metrics(time DESC);

-- ============================================
-- WIND METRICS
-- ============================================
CREATE TABLE IF NOT EXISTS wind_metrics (
    time TIMESTAMP NOT NULL,
    sensor_id VARCHAR(255) NOT NULL,
    value FLOAT,
    unit VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT create_hypertable('wind_metrics', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_wind_sensor_id 
ON wind_metrics(sensor_id);

CREATE INDEX IF NOT EXISTS idx_wind_time 
ON wind_metrics(time DESC);

-- ============================================
-- WATER QUALITY METRICS
-- ============================================
CREATE TABLE IF NOT EXISTS water_quality_metrics (
    time TIMESTAMP NOT NULL,
    sensor_id VARCHAR(255) NOT NULL,
    value FLOAT,
    unit VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT create_hypertable('water_quality_metrics', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_water_quality_sensor_id 
ON water_quality_metrics(sensor_id);

CREATE INDEX IF NOT EXISTS idx_water_quality_time 
ON water_quality_metrics(time DESC);

-- ============================================
-- GPS METRICS
-- ============================================
CREATE TABLE IF NOT EXISTS gps_metrics (
    time TIMESTAMP NOT NULL,
    sensor_id VARCHAR(255) NOT NULL,
    value FLOAT,
    unit VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT create_hypertable('gps_metrics', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_gps_sensor_id 
ON gps_metrics(sensor_id);

CREATE INDEX IF NOT EXISTS idx_gps_time 
ON gps_metrics(time DESC);

-- ============================================
-- ANIMAL METRICS
-- ============================================
CREATE TABLE IF NOT EXISTS animal_metrics (
    time TIMESTAMP NOT NULL,
    sensor_id VARCHAR(255) NOT NULL,
    value FLOAT,
    unit VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT create_hypertable('animal_metrics', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_animal_sensor_id 
ON animal_metrics(sensor_id);

CREATE INDEX IF NOT EXISTS idx_animal_time 
ON animal_metrics(time DESC);

-- ============================================
-- CONTINUOUS AGGREGATES (Optional)
-- For faster queries on aggregated data
-- ============================================

-- Hourly average temperature
CREATE MATERIALIZED VIEW IF NOT EXISTS temperature_hourly_avg
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS bucket,
    sensor_id,
    AVG(value) as avg_temperature,
    MIN(value) as min_temperature,
    MAX(value) as max_temperature,
    COUNT(*) as reading_count
FROM temperature_metrics
GROUP BY bucket, sensor_id;

-- Refresh policy for continuous aggregates
SELECT add_continuous_aggregate_policy('temperature_hourly_avg',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- ============================================
-- DATA RETENTION POLICY (Optional)
-- Automatically drop old data
-- ============================================

-- Keep data for 1 year (adjust as needed)
-- SELECT add_retention_policy('temperature_metrics', INTERVAL '1 year');
-- SELECT add_retention_policy('humidity_metrics', INTERVAL '1 year');
-- SELECT add_retention_policy('soil_moisture_metrics', INTERVAL '1 year');
-- (Repeat for other metrics tables)

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON TABLE temperature_metrics IS 'Time-series data for temperature sensors';
COMMENT ON TABLE humidity_metrics IS 'Time-series data for humidity sensors';
COMMENT ON TABLE soil_moisture_metrics IS 'Time-series data for soil moisture sensors';
COMMENT ON TABLE ph_metrics IS 'Time-series data for pH sensors';
COMMENT ON TABLE rainfall_metrics IS 'Time-series data for rainfall sensors';
COMMENT ON TABLE light_metrics IS 'Time-series data for light sensors';
COMMENT ON TABLE wind_metrics IS 'Time-series data for wind sensors';
COMMENT ON TABLE water_quality_metrics IS 'Time-series data for water quality sensors';
COMMENT ON TABLE gps_metrics IS 'Time-series data for GPS sensors';
COMMENT ON TABLE animal_metrics IS 'Time-series data for animal sensors';

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to get latest reading for a sensor
CREATE OR REPLACE FUNCTION get_latest_reading(p_sensor_id VARCHAR)
RETURNS TABLE (
    sensor_id VARCHAR,
    time TIMESTAMP,
    value FLOAT,
    unit VARCHAR,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.sensor_id,
        t.time,
        t.value,
        t.unit,
        t.metadata
    FROM temperature_metrics t
    WHERE t.sensor_id = p_sensor_id
    ORDER BY t.time DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function to get statistics for a sensor type
CREATE OR REPLACE FUNCTION get_sensor_type_stats(p_sensor_type VARCHAR)
RETURNS TABLE (
    sensor_count BIGINT,
    total_readings BIGINT,
    avg_value FLOAT,
    min_value FLOAT,
    max_value FLOAT,
    first_reading TIMESTAMP,
    last_reading TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    EXECUTE format('
        SELECT 
            COUNT(DISTINCT sensor_id) as sensor_count,
            COUNT(*) as total_readings,
            AVG(value) as avg_value,
            MIN(value) as min_value,
            MAX(value) as max_value,
            MIN(time) as first_reading,
            MAX(time) as last_reading
        FROM %I_metrics
    ', p_sensor_type);
END;
$$ LANGUAGE plpgsql;