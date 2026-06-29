-- PostgreSQL Indexes for Smart Agriculture System
-- Optimizes query performance

-- ============================================
-- TABLE: sensors
-- ============================================
CREATE INDEX IF NOT EXISTS idx_sensor_sensor_id 
ON sensors(sensor_id);

CREATE INDEX IF NOT EXISTS idx_sensor_type 
ON sensors(type);

CREATE INDEX IF NOT EXISTS idx_sensor_protocol 
ON sensors(protocol);

CREATE INDEX IF NOT EXISTS idx_sensor_installation_date 
ON sensors(installation_date);

CREATE INDEX IF NOT EXISTS idx_sensor_created_at 
ON sensors(created_at);

-- ============================================
-- TABLE: users
-- ============================================
CREATE INDEX IF NOT EXISTS idx_user_email 
ON users(email);

CREATE INDEX IF NOT EXISTS idx_user_role 
ON users(role);

CREATE INDEX IF NOT EXISTS idx_user_created_at 
ON users(created_at);

-- ============================================
-- TABLE: fields
-- ============================================
CREATE INDEX IF NOT EXISTS idx_field_name 
ON fields(field_name);

CREATE INDEX IF NOT EXISTS idx_field_crop 
ON fields(crop);

CREATE INDEX IF NOT EXISTS idx_field_created_at 
ON fields(created_at);

-- ============================================
-- TABLE: sensor_metadata
-- ============================================
CREATE INDEX IF NOT EXISTS idx_sensor_metadata_sensor_id 
ON sensor_metadata(sensor_id);

CREATE INDEX IF NOT EXISTS idx_sensor_metadata_field_id 
ON sensor_metadata(field_id);

CREATE INDEX IF NOT EXISTS idx_sensor_metadata_status 
ON sensor_metadata(status);

CREATE INDEX IF NOT EXISTS idx_sensor_metadata_installation_date 
ON sensor_metadata(installation_date);

-- ============================================
-- TABLE: sensor_readings
-- ============================================
CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_id 
ON sensor_readings(sensor_id);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp 
ON sensor_readings(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_type 
ON sensor_readings(sensor_type);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_quality 
ON sensor_readings(quality);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_is_outlier 
ON sensor_readings(is_outlier);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_created_at 
ON sensor_readings(created_at);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_timestamp 
ON sensor_readings(sensor_id, timestamp DESC);

-- ============================================
-- TABLE: alerts
-- ============================================
CREATE INDEX IF NOT EXISTS idx_alerts_sensor_id 
ON alerts(sensor_id);

CREATE INDEX IF NOT EXISTS idx_alerts_alert_type 
ON alerts(alert_type);

CREATE INDEX IF NOT EXISTS idx_alerts_severity 
ON alerts(severity);

CREATE INDEX IF NOT EXISTS idx_alerts_resolved 
ON alerts(resolved);

CREATE INDEX IF NOT EXISTS idx_alerts_created_at 
ON alerts(created_at DESC);

-- ============================================
-- TABLE: maintenance_logs
-- ============================================
CREATE INDEX IF NOT EXISTS idx_maintenance_sensor_id 
ON maintenance_logs(sensor_id);

CREATE INDEX IF NOT EXISTS idx_maintenance_type 
ON maintenance_logs(maintenance_type);

CREATE INDEX IF NOT EXISTS idx_maintenance_performed_at 
ON maintenance_logs(performed_at DESC);

-- ============================================
-- FULL-TEXT SEARCH INDEXES (optional)
-- ============================================
-- For searching in message fields
CREATE INDEX IF NOT EXISTS idx_alerts_message_gin 
ON alerts USING GIN (to_tsvector('french', message));

CREATE INDEX IF NOT EXISTS idx_maintenance_description_gin 
ON maintenance_logs USING GIN (to_tsvector('french', description));

-- ============================================
-- PARTIAL INDEXES (for specific queries)
-- ============================================
-- Index for active sensors only
CREATE INDEX IF NOT EXISTS idx_sensor_metadata_active 
ON sensor_metadata(sensor_id) 
WHERE status = 'active';

-- Index for unresolved alerts
CREATE INDEX IF NOT EXISTS idx_alerts_unresolved 
ON alerts(created_at DESC) 
WHERE resolved = FALSE;

-- Index for outlier readings
CREATE INDEX IF NOT EXISTS idx_sensor_readings_outliers 
ON sensor_readings(sensor_id, timestamp DESC) 
WHERE is_outlier = TRUE;

-- ============================================
-- COMMENTS
-- ============================================
COMMENT ON INDEX idx_sensor_sensor_id IS 'Primary lookup for sensors';
COMMENT ON INDEX idx_sensor_readings_sensor_timestamp IS 'Composite index for sensor readings queries';
COMMENT ON INDEX idx_alerts_unresolved IS 'Index for active alerts only';