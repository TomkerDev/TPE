-- PostgreSQL Stored Procedures and Functions
-- Business logic and data manipulation routines

-- ============================================
-- FUNCTION: get_sensor_latest_reading
-- Returns the latest reading for a sensor
-- ============================================
CREATE OR REPLACE FUNCTION get_sensor_latest_reading(p_sensor_id VARCHAR)
RETURNS TABLE (
    sensor_id VARCHAR(30),
    sensor_type VARCHAR(30),
    value DOUBLE PRECISION,
    unit VARCHAR(20),
    timestamp TIMESTAMP,
    quality INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sr.sensor_id,
        sr.sensor_type,
        sr.value,
        sr.unit,
        sr.timestamp,
        sr.quality
    FROM sensor_readings sr
    WHERE sr.sensor_id = p_sensor_id
    ORDER BY sr.timestamp DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: get_sensor_statistics
-- Returns statistics for a sensor
-- ============================================
CREATE OR REPLACE FUNCTION get_sensor_statistics(p_sensor_id VARCHAR)
RETURNS TABLE (
    sensor_id VARCHAR(30),
    total_readings BIGINT,
    avg_value DOUBLE PRECISION,
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    first_reading TIMESTAMP,
    last_reading TIMESTAMP,
    avg_quality DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sr.sensor_id,
        COUNT(*)::BIGINT,
        AVG(sr.value),
        MIN(sr.value),
        MAX(sr.value),
        MIN(sr.timestamp),
        MAX(sr.timestamp),
        AVG(sr.quality)
    FROM sensor_readings sr
    WHERE sr.sensor_id = p_sensor_id
    GROUP BY sr.sensor_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: get_field_sensors
-- Returns all sensors for a specific field
-- ============================================
CREATE OR REPLACE FUNCTION get_field_sensors(p_field_id INTEGER)
RETURNS TABLE (
    sensor_id VARCHAR(30),
    sensor_type VARCHAR(30),
    manufacturer VARCHAR(100),
    protocol VARCHAR(30),
    status VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.sensor_id,
        s.type,
        s.manufacturer,
        s.protocol,
        sm.status
    FROM sensors s
    JOIN sensor_metadata sm ON s.sensor_id = sm.sensor_id
    WHERE sm.field_id = p_field_id
    AND sm.status = 'active'
    ORDER BY s.sensor_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: get_active_alerts
-- Returns all unresolved alerts
-- ============================================
CREATE OR REPLACE FUNCTION get_active_alerts()
RETURNS TABLE (
    alert_id INTEGER,
    sensor_id VARCHAR(30),
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    message TEXT,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.alert_id,
        a.sensor_id,
        a.alert_type,
        a.severity,
        a.message,
        a.created_at
    FROM alerts a
    WHERE a.resolved = FALSE
    ORDER BY 
        CASE a.severity
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2
            WHEN 'medium' THEN 3
            WHEN 'low' THEN 4
        END,
        a.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: resolve_alert
-- Marks an alert as resolved
-- ============================================
CREATE OR REPLACE FUNCTION resolve_alert(p_alert_id INTEGER, p_resolved_by VARCHAR(100))
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE alerts 
    SET 
        resolved = TRUE,
        resolved_at = CURRENT_TIMESTAMP
    WHERE alert_id = p_alert_id 
    AND resolved = FALSE;
    
    IF FOUND THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: insert_sensor_reading
-- Inserts a new sensor reading with validation
-- ============================================
CREATE OR REPLACE FUNCTION insert_sensor_reading(
    p_sensor_id VARCHAR(30),
    p_sensor_type VARCHAR(30),
    p_value DOUBLE PRECISION,
    p_unit VARCHAR(20),
    p_timestamp TIMESTAMP,
    p_quality INTEGER DEFAULT 100
)
RETURNS INTEGER AS $$
DECLARE
    v_reading_id INTEGER;
BEGIN
    -- Validate sensor exists
    IF NOT EXISTS (SELECT 1 FROM sensors WHERE sensor_id = p_sensor_id) THEN
        RAISE EXCEPTION 'Sensor % does not exist', p_sensor_id;
    END IF;
    
    -- Validate quality
    IF p_quality < 0 OR p_quality > 100 THEN
        RAISE EXCEPTION 'Quality must be between 0 and 100';
    END IF;
    
    -- Insert reading
    INSERT INTO sensor_readings (
        sensor_id,
        sensor_type,
        value,
        unit,
        timestamp,
        quality
    ) VALUES (
        p_sensor_id,
        p_sensor_type,
        p_value,
        p_unit,
        p_timestamp,
        p_quality
    ) RETURNING id INTO v_reading_id;
    
    RETURN v_reading_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: get_sensors_by_location
-- Returns sensors within a radius of a point
-- ============================================
CREATE OR REPLACE FUNCTION get_sensors_by_location(
    p_latitude DOUBLE PRECISION,
    p_longitude DOUBLE PRECISION,
    p_radius_km DOUBLE PRECISION DEFAULT 10
)
RETURNS TABLE (
    sensor_id VARCHAR(30),
    type VARCHAR(30),
    manufacturer VARCHAR(100),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    distance_km DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.sensor_id,
        s.type,
        s.manufacturer,
        s.latitude,
        s.longitude,
        -- Haversine formula for distance calculation
        (6371 * acos(
            cos(radians(p_latitude)) * cos(radians(s.latitude)) *
            cos(radians(s.longitude) - radians(p_longitude)) +
            sin(radians(p_latitude)) * sin(radians(s.latitude))
        )) AS distance_km
    FROM sensors s
    WHERE s.latitude IS NOT NULL 
    AND s.longitude IS NOT NULL
    AND (
        6371 * acos(
            cos(radians(p_latitude)) * cos(radians(s.latitude)) *
            cos(radians(s.longitude) - radians(p_longitude)) +
            sin(radians(p_latitude)) * sin(radians(s.latitude))
        )
    ) <= p_radius_km
    ORDER BY distance_km;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: get_daily_summary
-- Returns daily summary for a sensor
-- ============================================
CREATE OR REPLACE FUNCTION get_daily_summary(
    p_sensor_id VARCHAR(30),
    p_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    sensor_id VARCHAR(30),
    reading_date DATE,
    total_readings BIGINT,
    avg_value DOUBLE PRECISION,
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    stddev_value DOUBLE PRECISION,
    avg_quality DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sr.sensor_id,
        p_date::DATE,
        COUNT(*)::BIGINT,
        AVG(sr.value),
        MIN(sr.value),
        MAX(sr.value),
        STDDEV(sr.value),
        AVG(sr.quality)
    FROM sensor_readings sr
    WHERE sr.sensor_id = p_sensor_id
    AND DATE(sr.timestamp) = p_date
    GROUP BY sr.sensor_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: cleanup_old_readings
-- Deletes readings older than specified days
-- ============================================
CREATE OR REPLACE FUNCTION cleanup_old_readings(p_days INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    DELETE FROM sensor_readings
    WHERE timestamp < CURRENT_TIMESTAMP - (p_days || ' days')::INTERVAL;
    
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    
    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: register_sensor
-- Registers a new sensor with validation
-- ============================================
CREATE OR REPLACE FUNCTION register_sensor(
    p_sensor_id VARCHAR(30),
    p_type VARCHAR(30),
    p_manufacturer VARCHAR(100),
    p_protocol VARCHAR(30),
    p_latitude DOUBLE PRECISION,
    p_longitude DOUBLE PRECISION,
    p_installation_date DATE
)
RETURNS BOOLEAN AS $$
BEGIN
    -- Validate protocol
    IF p_protocol NOT IN ('MQTT', 'LoRaWAN', 'CoAP', 'HTTP') THEN
        RAISE EXCEPTION 'Invalid protocol: %', p_protocol;
    END IF;
    
    -- Validate coordinates
    IF p_latitude IS NOT NULL AND (p_latitude < -90 OR p_latitude > 90) THEN
        RAISE EXCEPTION 'Invalid latitude: %', p_latitude;
    END IF;
    
    IF p_longitude IS NOT NULL AND (p_longitude < -180 OR p_longitude > 180) THEN
        RAISE EXCEPTION 'Invalid longitude: %', p_longitude;
    END IF;
    
    -- Insert sensor
    INSERT INTO sensors (
        sensor_id,
        type,
        manufacturer,
        protocol,
        latitude,
        longitude,
        installation_date
    ) VALUES (
        p_sensor_id,
        p_type,
        p_manufacturer,
        p_protocol,
        p_latitude,
        p_longitude,
        p_installation_date
    );
    
    RETURN TRUE;
EXCEPTION
    WHEN unique_violation THEN
        RAISE NOTICE 'Sensor % already exists', p_sensor_id;
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: link_sensor_to_field
-- Links a sensor to a field
-- ============================================
CREATE OR REPLACE FUNCTION link_sensor_to_field(
    p_sensor_id VARCHAR(30),
    p_field_id INTEGER,
    p_installation_date DATE DEFAULT CURRENT_DATE
)
RETURNS BOOLEAN AS $$
BEGIN
    INSERT INTO sensor_metadata (
        sensor_id,
        field_id,
        installation_date,
        status
    ) VALUES (
        p_sensor_id,
        p_field_id,
        p_installation_date,
        'active'
    );
    
    RETURN TRUE;
EXCEPTION
    WHEN unique_violation THEN
        RAISE NOTICE 'Sensor % already linked to field %', p_sensor_id, p_field_id;
        RETURN FALSE;
    WHEN foreign_key_violation THEN
        RAISE EXCEPTION 'Invalid sensor_id or field_id';
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TRIGGER: update_updated_at_column
-- Automatically updates updated_at timestamp
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables
CREATE TRIGGER update_sensors_updated_at 
    BEFORE UPDATE ON sensors 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fields_updated_at 
    BEFORE UPDATE ON fields 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- TRIGGER: check_sensor_reading_quality
-- Validates reading quality before insert
-- ============================================
CREATE OR REPLACE FUNCTION check_reading_quality()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quality < 0 OR NEW.quality > 100 THEN
        RAISE EXCEPTION 'Quality must be between 0 and 100, got: %', NEW.quality;
    END IF;
    
    IF NEW.value IS NULL THEN
        RAISE WARNING 'Null value for sensor %', NEW.sensor_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_sensor_reading_quality 
    BEFORE INSERT ON sensor_readings 
    FOR EACH ROW 
    EXECUTE FUNCTION check_reading_quality();

-- ============================================
-- VIEW: sensor_dashboard
-- Dashboard view for sensor monitoring
-- ============================================
CREATE OR REPLACE VIEW sensor_dashboard AS
SELECT 
    s.sensor_id,
    s.type,
    s.manufacturer,
    s.protocol,
    sm.status,
    sm.field_id,
    f.field_name,
    f.crop,
    sr.latest_value,
    sr.latest_timestamp,
    sr.reading_count,
    a.active_alerts
FROM sensors s
LEFT JOIN sensor_metadata sm ON s.sensor_id = sm.sensor_id
LEFT JOIN fields f ON sm.field_id = f.field_id
LEFT JOIN (
    SELECT 
        sensor_id,
        MAX(timestamp) as latest_timestamp,
        value as latest_value,
        COUNT(*) as reading_count
    FROM sensor_readings
    GROUP BY sensor_id, value
) sr ON s.sensor_id = sr.sensor_id
LEFT JOIN (
    SELECT 
        sensor_id,
        COUNT(*) as active_alerts
    FROM alerts
    WHERE resolved = FALSE
    GROUP BY sensor_id
) a ON s.sensor_id = a.sensor_id;

-- ============================================
-- COMMENTS
-- ============================================
COMMENT ON FUNCTION get_sensor_latest_reading IS 'Returns latest reading for a sensor';
COMMENT ON FUNCTION get_sensor_statistics IS 'Returns statistics for a sensor';
COMMENT ON FUNCTION get_field_sensors IS 'Returns all sensors for a field';
COMMENT ON FUNCTION get_active_alerts IS 'Returns all unresolved alerts';
COMMENT ON FUNCTION resolve_alert IS 'Marks an alert as resolved';
COMMENT ON FUNCTION insert_sensor_reading IS 'Inserts a new sensor reading with validation';
COMMENT ON FUNCTION get_sensors_by_location IS 'Returns sensors within radius using Haversine formula';
COMMENT ON FUNCTION get_daily_summary IS 'Returns daily summary for a sensor';
COMMENT ON FUNCTION cleanup_old_readings IS 'Deletes readings older than specified days';
COMMENT ON FUNCTION register_sensor IS 'Registers a new sensor with validation';
COMMENT ON FUNCTION link_sensor_to_field IS 'Links a sensor to a field';
COMMENT ON VIEW sensor_dashboard IS 'Dashboard view for sensor monitoring';