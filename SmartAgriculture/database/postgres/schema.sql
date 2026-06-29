-- PostgreSQL Schema for Smart Agriculture System
-- Main relational database for structured data

-- Drop existing tables if needed (for clean setup)
-- DROP TABLE IF EXISTS sensor_metadata CASCADE;
-- DROP TABLE IF EXISTS fields CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;
-- DROP TABLE IF EXISTS sensors CASCADE;

-- ============================================
-- TABLE: sensors
-- Stores sensor information
-- ============================================
CREATE TABLE IF NOT EXISTS sensors (
    sensor_id VARCHAR(30) PRIMARY KEY,
    type VARCHAR(30) NOT NULL,
    manufacturer VARCHAR(100),
    protocol VARCHAR(30),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    installation_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLE: users
-- Stores user information
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    role VARCHAR(40) DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLE: fields
-- Stores agricultural field/parcel information
-- ============================================
CREATE TABLE IF NOT EXISTS fields (
    field_id SERIAL PRIMARY KEY,
    field_name VARCHAR(100) NOT NULL,
    area DOUBLE PRECISION,
    crop VARCHAR(100),
    location VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLE: sensor_metadata
-- Links sensors to fields
-- ============================================
CREATE TABLE IF NOT EXISTS sensor_metadata (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(30) NOT NULL,
    field_id INTEGER NOT NULL,
    installation_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign keys
    CONSTRAINT fk_sensor 
        FOREIGN KEY(sensor_id) 
        REFERENCES sensors(sensor_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_field 
        FOREIGN KEY(field_id) 
        REFERENCES fields(field_id)
        ON DELETE CASCADE,
    
    -- Unique constraint
    CONSTRAINT unique_sensor_field 
        UNIQUE(sensor_id, field_id)
);

-- ============================================
-- TABLE: sensor_readings (relational copy)
-- Stores latest readings for quick access
-- ============================================
CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(30) NOT NULL,
    sensor_type VARCHAR(30) NOT NULL,
    value DOUBLE PRECISION,
    unit VARCHAR(20),
    timestamp TIMESTAMP NOT NULL,
    quality INTEGER DEFAULT 100,
    is_outlier BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_reading_sensor 
        FOREIGN KEY(sensor_id) 
        REFERENCES sensors(sensor_id)
        ON DELETE CASCADE
);

-- ============================================
-- TABLE: alerts
-- Stores system alerts and notifications
-- ============================================
CREATE TABLE IF NOT EXISTS alerts (
    alert_id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(30),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    
    CONSTRAINT fk_alert_sensor 
        FOREIGN KEY(sensor_id) 
        REFERENCES sensors(sensor_id)
        ON DELETE SET NULL
);

-- ============================================
-- TABLE: maintenance_logs
-- Tracks sensor maintenance activities
-- ============================================
CREATE TABLE IF NOT EXISTS maintenance_logs (
    log_id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(30) NOT NULL,
    maintenance_type VARCHAR(50),
    description TEXT,
    performed_by VARCHAR(100),
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_maintenance_sensor 
        FOREIGN KEY(sensor_id) 
        REFERENCES sensors(sensor_id)
        ON DELETE CASCADE
);

-- ============================================
-- COMMENTS
-- ============================================
COMMENT ON TABLE sensors IS 'Main sensor registry';
COMMENT ON TABLE users IS 'System users';
COMMENT ON TABLE fields IS 'Agricultural fields/parcels';
COMMENT ON TABLE sensor_metadata IS 'Sensor-field relationships';
COMMENT ON TABLE sensor_readings IS 'Latest sensor readings (relational view)';
COMMENT ON TABLE alerts IS 'System alerts and notifications';
COMMENT ON TABLE maintenance_logs IS 'Sensor maintenance history';