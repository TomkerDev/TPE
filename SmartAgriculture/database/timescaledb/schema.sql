-- TimescaleDB Schema for Smart Agriculture System
-- Time-series data for sensor observations

-- ============================================
-- MAIN OBSERVATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS observations (
    sensor_id VARCHAR(30) NOT NULL,
    sensor_type VARCHAR(30) NOT NULL,
    value DOUBLE PRECISION,
    unit VARCHAR(20),
    timestamp TIMESTAMP NOT NULL,
    quality INTEGER DEFAULT 100,
    outlier BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- HYPER TABLE EXTENSION
-- ============================================
SELECT create_hypertable('observations', 'timestamp', if_not_exists => TRUE);

-- ============================================
-- COMPRESSION SETTINGS
-- ============================================
ALTER TABLE observations SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'sensor_id',
    timescaledb.compress_orderby = 'timestamp DESC'
);

-- Compression policy: compress chunks older than 30 days
SELECT add_compression_policy('observations', INTERVAL '30 days');

-- ============================================
-- RETENTION POLICY (optional)
-- Keep data for 2 years, then drop
-- ============================================
-- SELECT add_retention_policy('observations', INTERVAL '2 years');

-- ============================================
-- CONTINUOUS AGGREGATES
-- ============================================

-- Hourly averages by sensor
CREATE MATERIALIZED VIEW IF NOT EXISTS observations_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp) AS bucket,
    sensor_id,
    sensor_type,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    STDDEV(value) as stddev_value,
    COUNT(*) as reading_count,
    AVG(quality) as avg_quality,
    SUM(CASE WHEN outlier THEN 1 ELSE 0 END) as outlier_count
FROM observations
GROUP BY bucket, sensor_id, sensor_type;

-- Refresh policy for hourly aggregates
SELECT add_continuous_aggregate_policy('observations_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);

-- Daily averages by sensor type
CREATE MATERIALIZED VIEW IF NOT EXISTS observations_daily
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', timestamp) AS bucket,
    sensor_type,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(DISTINCT sensor_id) as unique_sensors,
    COUNT(*) as total_readings,
    AVG(quality) as avg_quality
FROM observations
GROUP BY bucket, sensor_type;

-- Refresh policy for daily aggregates
SELECT add_continuous_aggregate_policy('observations_daily',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '6 hours'
);

-- ============================================
-- INDEXES
-- ============================================

-- Index on sensor_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_observations_sensor_id 
ON observations(sensor_id);

-- Index on timestamp for time-range queries
CREATE INDEX IF NOT EXISTS idx_observations_timestamp 
ON observations(timestamp DESC);

-- Index on sensor_type for filtering
CREATE INDEX IF NOT EXISTS idx_observations_sensor_type 
ON observations(sensor_type);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_observations_sensor_timestamp 
ON observations(sensor_id, timestamp DESC);

-- Index on quality for data quality queries
CREATE INDEX IF NOT EXISTS idx_observations_quality 
ON observations(quality);

-- Index on outlier flag
CREATE INDEX IF NOT EXISTS idx_observations_outlier 
ON observations(outlier) WHERE outlier = TRUE;

-- GIN index on metadata for JSON queries
CREATE INDEX IF NOT EXISTS idx_observations_metadata 
ON observations USING GIN (metadata);

-- ============================================
-- COMMENTS
-- ============================================
COMMENT ON TABLE observations IS 'Main time-series observations table (hypertable)';
COMMENT ON COLUMN observations.sensor_id IS 'Foreign key to sensors table';
COMMENT ON COLUMN observations.sensor_type IS 'Type of sensor (temperature, humidity, etc.)';
COMMENT ON COLUMN observations.value IS 'Sensor reading value';
COMMENT ON COLUMN observations.quality IS 'Data quality score (0-100)';
COMMENT ON COLUMN observations.outlier IS 'Flag indicating if reading is an outlier';
COMMENT ON COLUMN observations.metadata IS 'Additional metadata in JSONB format';