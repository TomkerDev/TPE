-- PostgreSQL Database Initialization Script
-- Creates tables for Smart Agriculture System

-- Drop existing table if needed (for clean setup)
-- DROP TABLE IF EXISTS sensor_data;

-- Create main sensor data table
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    sensor_type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    processed_at TIMESTAMP,
    metric VARCHAR(100),
    value FLOAT,
    unit VARCHAR(50),
    data_quality FLOAT DEFAULT 1.0,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_sensor_data_sensor_id 
ON sensor_data(sensor_id);

CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp 
ON sensor_data(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_sensor_data_type 
ON sensor_data(sensor_type);

CREATE INDEX IF NOT EXISTS idx_sensor_data_metric 
ON sensor_data(metric);

-- Create a view for latest readings per sensor
CREATE OR REPLACE VIEW latest_sensor_readings AS
SELECT DISTINCT ON (sensor_id) *
FROM sensor_data
ORDER BY sensor_id, timestamp DESC;

-- Create a view for aggregated statistics
CREATE OR REPLACE VIEW sensor_statistics AS
SELECT 
    sensor_type,
    COUNT(*) as total_readings,
    COUNT(DISTINCT sensor_id) as unique_sensors,
    MIN(timestamp) as earliest_reading,
    MAX(timestamp) as latest_reading,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value
FROM sensor_data
GROUP BY sensor_type
ORDER BY total_readings DESC;

-- Insert sample data (optional, for testing)
-- INSERT INTO sensor_data (sensor_id, sensor_type, timestamp, metric, value, unit, data_quality)
-- VALUES 
--     ('temp_sensor_001', 'temperature', NOW(), 'temperature', 25.5, 'celsius', 1.0),
--     ('humidity_sensor_001', 'humidity', NOW(), 'humidity', 65.0, 'percent', 1.0);

COMMENT ON TABLE sensor_data IS 'Main table for storing all sensor data from Smart Agriculture System';
COMMENT ON COLUMN sensor_data.sensor_id IS 'Unique identifier for each sensor';
COMMENT ON COLUMN sensor_data.sensor_type IS 'Type of sensor (temperature, humidity, etc.)';
COMMENT ON COLUMN sensor_data.timestamp IS 'Timestamp when the reading was taken';
COMMENT ON COLUMN sensor_data.raw_data IS 'Complete raw data in JSONB format for flexibility';