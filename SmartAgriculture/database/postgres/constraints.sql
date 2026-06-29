-- PostgreSQL Constraints for Smart Agriculture System
-- Ensures data integrity and business rules

-- ============================================
-- TABLE: sensors
-- ============================================

-- Protocol constraint
ALTER TABLE sensors 
ADD CONSTRAINT check_protocol 
CHECK (protocol IN ('MQTT', 'LoRaWAN', 'CoAP', 'HTTP'));

-- Latitude constraint
ALTER TABLE sensors 
ADD CONSTRAINT check_latitude 
CHECK (latitude >= -90 AND latitude <= 90);

-- Longitude constraint
ALTER TABLE sensors 
ADD CONSTRAINT check_longitude 
CHECK (longitude >= -180 AND longitude <= 180);

-- Installation date constraint
ALTER TABLE sensors 
ADD CONSTRAINT check_installation_date 
CHECK (installation_date <= CURRENT_DATE);

-- ============================================
-- TABLE: users
-- ============================================

-- Role constraint
ALTER TABLE users 
ADD CONSTRAINT check_role 
CHECK (role IN ('admin', 'manager', 'viewer', 'technician'));

-- Email format constraint
ALTER TABLE users 
ADD CONSTRAINT check_email_format 
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- ============================================
-- TABLE: fields
-- ============================================

-- Area constraint (must be positive)
ALTER TABLE fields 
ADD CONSTRAINT check_area 
CHECK (area IS NULL OR area > 0);

-- Field name constraint
ALTER TABLE fields 
ADD CONSTRAINT check_field_name 
CHECK (field_name <> '');

-- ============================================
-- TABLE: sensor_metadata
-- ============================================

-- Status constraint
ALTER TABLE sensor_metadata 
ADD CONSTRAINT check_status 
CHECK (status IN ('active', 'inactive', 'maintenance', 'decommissioned'));

-- Installation date constraint
ALTER TABLE sensor_metadata 
ADD CONSTRAINT check_metadata_installation_date 
CHECK (installation_date IS NULL OR installation_date <= CURRENT_DATE);

-- ============================================
-- TABLE: sensor_readings
-- ============================================

-- Quality constraint (0-100)
ALTER TABLE sensor_readings 
ADD CONSTRAINT check_quality 
CHECK (quality >= 0 AND quality <= 100);

-- Timestamp constraint
ALTER TABLE sensor_readings 
ADD CONSTRAINT check_timestamp 
CHECK (timestamp <= CURRENT_TIMESTAMP);

-- Sensor type constraint
ALTER TABLE sensor_readings 
ADD CONSTRAINT check_sensor_type 
CHECK (sensor_type <> '');

-- ============================================
-- TABLE: alerts
-- ============================================

-- Severity constraint
ALTER TABLE alerts 
ADD CONSTRAINT check_severity 
CHECK (severity IN ('low', 'medium', 'high', 'critical'));

-- Alert type constraint
ALTER TABLE alerts 
ADD CONSTRAINT check_alert_type 
CHECK (alert_type <> '');

-- Resolved timestamp constraint
ALTER TABLE alerts 
ADD CONSTRAINT check_resolved_at 
CHECK (resolved_at IS NULL OR resolved_at >= created_at);

-- ============================================
-- TABLE: maintenance_logs
-- ============================================

-- Maintenance type constraint
ALTER TABLE maintenance_logs 
ADD CONSTRAINT check_maintenance_type 
CHECK (maintenance_type <> '');

-- Performed at constraint
ALTER TABLE maintenance_logs 
ADD CONSTRAINT check_performed_at 
CHECK (performed_at <= CURRENT_TIMESTAMP);

-- ============================================
-- FOREIGN KEY CONSTRAINTS (if not in schema)
-- ============================================

-- Ensure sensor_id exists in sensors table
ALTER TABLE sensor_metadata 
ADD CONSTRAINT fk_sensor_metadata_sensor 
FOREIGN KEY(sensor_id) 
REFERENCES sensors(sensor_id) 
ON DELETE CASCADE 
ON UPDATE CASCADE;

-- Ensure field_id exists in fields table
ALTER TABLE sensor_metadata 
ADD CONSTRAINT fk_sensor_metadata_field 
FOREIGN KEY(field_id) 
REFERENCES fields(field_id) 
ON DELETE CASCADE 
ON UPDATE CASCADE;

-- Ensure sensor_id exists in sensor_readings
ALTER TABLE sensor_readings 
ADD CONSTRAINT fk_sensor_readings_sensor 
FOREIGN KEY(sensor_id) 
REFERENCES sensors(sensor_id) 
ON DELETE CASCADE 
ON UPDATE CASCADE;

-- Ensure sensor_id exists in alerts
ALTER TABLE alerts 
ADD CONSTRAINT fk_alerts_sensor 
FOREIGN KEY(sensor_id) 
REFERENCES sensors(sensor_id) 
ON DELETE SET NULL 
ON UPDATE CASCADE;

-- Ensure sensor_id exists in maintenance_logs
ALTER TABLE maintenance_logs 
ADD CONSTRAINT fk_maintenance_sensor 
FOREIGN KEY(sensor_id) 
REFERENCES sensors(sensor_id) 
ON DELETE CASCADE 
ON UPDATE CASCADE;

-- ============================================
-- UNIQUE CONSTRAINTS
-- ============================================

-- Ensure unique sensor-field combination
ALTER TABLE sensor_metadata 
ADD CONSTRAINT unique_sensor_field 
UNIQUE(sensor_id, field_id);

-- Ensure unique email
ALTER TABLE users 
ADD CONSTRAINT unique_user_email 
UNIQUE(email);

-- ============================================
-- CHECK CONSTRAINTS FOR DATA QUALITY
-- ============================================

-- Ensure sensor_id is not empty
ALTER TABLE sensors 
ADD CONSTRAINT check_sensor_id_not_empty 
CHECK (sensor_id <> '');

-- Ensure sensor type is not empty
ALTER TABLE sensors 
ADD CONSTRAINT check_sensor_type_not_empty 
CHECK (type <> '');

-- Ensure user fullname is not empty
ALTER TABLE users 
ADD CONSTRAINT check_fullname_not_empty 
CHECK (fullname <> '');

-- Ensure field name is not empty
ALTER TABLE fields 
ADD CONSTRAINT check_field_name_not_empty 
CHECK (field_name <> '');

-- ============================================
-- COMMENTS
-- ============================================
COMMENT ON CONSTRAINT check_protocol ON sensors IS 'Valid protocols: MQTT, LoRaWAN, CoAP, HTTP';
COMMENT ON CONSTRAINT check_latitude ON sensors IS 'Latitude must be between -90 and 90';
COMMENT ON CONSTRAINT check_longitude ON sensors IS 'Longitude must be between -180 and 180';
COMMENT ON CONSTRAINT check_role ON users IS 'Valid roles: admin, manager, viewer, technician';
COMMENT ON CONSTRAINT check_email_format ON users IS 'Email must be valid format';
COMMENT ON CONSTRAINT check_area ON fields IS 'Area must be positive';
COMMENT ON CONSTRAINT check_status ON sensor_metadata IS 'Valid statuses: active, inactive, maintenance, decommissioned';
COMMENT ON CONSTRAINT check_quality ON sensor_readings IS 'Quality must be between 0 and 100';
COMMENT ON CONSTRAINT check_severity ON alerts IS 'Valid severities: low, medium, high, critical';