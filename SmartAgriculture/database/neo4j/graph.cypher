-- Neo4j Graph Database Cypher Scripts
-- Knowledge graph for semantic sensor data

-- ============================================
-- CONSTRAINTS AND INDEXES
-- ============================================

-- Sensor constraints
CREATE CONSTRAINT sensor_id_unique IF NOT EXISTS
FOR (s:Sensor) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT sensor_type_constraint IF NOT EXISTS
FOR (s:Sensor) REQUIRE s.type IS NOT NULL;

-- Observation constraints
CREATE CONSTRAINT observation_id_unique IF NOT EXISTS
FOR (o:Observation) REQUIRE o.id IS UNIQUE;

-- Property constraints
CREATE CONSTRAINT property_name_unique IF NOT EXISTS
FOR (p:Property) REQUIRE p.name IS UNIQUE;

-- Indexes
CREATE INDEX sensor_type_index IF NOT EXISTS
FOR (s:Sensor) ON (s.type);

CREATE INDEX sensor_semantic_type_index IF NOT EXISTS
FOR (s:Sensor) ON (s.semantic_type);

CREATE INDEX observation_timestamp_index IF NOT EXISTS
FOR (o:Observation) ON (o.timestamp);

CREATE INDEX observation_sensor_id_index IF NOT EXISTS
FOR (o:Observation) ON (o.sensor_id);

CREATE INDEX property_name_index IF NOT EXISTS
FOR (p:Property) ON (p.name);

-- ============================================
-- SAMPLE DATA INSERTION
-- ============================================

-- Create sample sensors
CREATE (s1:Sensor {
    id: 'TEMP001',
    type: 'temperature',
    semantic_type: 'AirTemperature',
    manufacturer: 'Bosch',
    protocol: 'MQTT',
    created_at: datetime(),
    last_seen: datetime(),
    update_count: 0
});

CREATE (s2:Sensor {
    id: 'HUM001',
    type: 'humidity',
    semantic_type: 'RelativeHumidity',
    manufacturer: 'Sensirion',
    protocol: 'MQTT',
    created_at: datetime(),
    last_seen: datetime(),
    update_count: 0
});

CREATE (s3:Sensor {
    id: 'SOIL001',
    type: 'soil_moisture',
    semantic_type: 'SoilMoisture',
    manufacturer: 'Decagon',
    protocol: 'LoRaWAN',
    created_at: datetime(),
    last_seen: datetime(),
    update_count: 0
});

CREATE (s4:Sensor {
    id: 'GPS001',
    type: 'gps',
    semantic_type: 'GPSLocation',
    manufacturer: 'u-blox',
    protocol: 'MQTT',
    created_at: datetime(),
    last_seen: datetime(),
    update_count: 0
});

-- Create sample observations
CREATE (o1:Observation {
    id: 'obs_TEMP001_2024_01_01T12_00_00',
    timestamp: datetime('2024-01-01T12:00:00'),
    value: 25.5,
    sensor_id: 'TEMP001'
});

CREATE (o2:Observation {
    id: 'obs_HUM001_2024_01_01T12_00_00',
    timestamp: datetime('2024-01-01T12:00:00'),
    value: 65.0,
    sensor_id: 'HUM001'
});

CREATE (o3:Observation {
    id: 'obs_SOIL001_2024_01_01T12_00_00',
    timestamp: datetime('2024-01-01T12:00:00'),
    value: 45.0,
    sensor_id: 'SOIL001'
});

-- Create properties
CREATE (p1:Property {name: 'AirTemperature'});
CREATE (p2:Property {name: 'RelativeHumidity'});
CREATE (p3:Property {name: 'SoilMoisture'});

-- Create relationships
MATCH (s:Sensor {id: 'TEMP001'}), (o:Observation {id: 'obs_TEMP001_2024_01_01T12_00_00'})
CREATE (s)-[:MADE]->(o);

MATCH (s:Sensor {id: 'HUM001'}), (o:Observation {id: 'obs_HUM001_2024_01_01T12_00_00'})
CREATE (s)-[:MADE]->(o);

MATCH (s:Sensor {id: 'SOIL001'}), (o:Observation {id: 'obs_SOIL001_2024_01_01T12_00_00'})
CREATE (s)-[:MADE]->(o);

MATCH (o:Observation {id: 'obs_TEMP001_2024_01_01T12_00_00'}), (p:Property {name: 'AirTemperature'})
CREATE (o)-[:OBSERVES]->(p);

MATCH (o:Observation {id: 'obs_HUM001_2024_01_01T12_00_00'}), (p:Property {name: 'RelativeHumidity'})
CREATE (o)-[:OBSERVES]->(p);

MATCH (o:Observation {id: 'obs_SOIL001_2024_01_01T12_00_00'}), (p:Property {name: 'SoilMoisture'})
CREATE (o)-[:OBSERVES]->(p);

-- ============================================
-- SAMPLE QUERIES
-- ============================================

-- Query 1: Get all sensors with their latest observation
MATCH (s:Sensor)-[:MADE]->(o:Observation)
WITH s, o
ORDER BY o.timestamp DESC
WITH s, collect(o)[0] AS latest_obs
RETURN s.id, s.type, s.semantic_type, latest_obs.timestamp, latest_obs.value
ORDER BY s.id;

-- Query 2: Get sensor statistics
MATCH (s:Sensor {id: 'TEMP001'})-[:MADE]->(o:Observation)
RETURN 
    s.id,
    COUNT(o) AS total_observations,
    MIN(o.timestamp) AS first_reading,
    MAX(o.timestamp) AS last_reading,
    AVG(o.value) AS avg_value,
    MIN(o.value) AS min_value,
    MAX(o.value) AS max_value;

-- Query 3: Get all observations for a sensor type
MATCH (s:Sensor {type: 'temperature'})-[:MADE]->(o:Observation)
RETURN s.id, o.timestamp, o.value
ORDER BY o.timestamp DESC
LIMIT 100;

-- Query 4: Find sensors of the same type
MATCH (s1:Sensor {id: 'TEMP001'})-[:SAME_TYPE]->(s2:Sensor)
RETURN s1.id, s1.type, s2.id, s2.type;

-- Query 5: Get observations with properties
MATCH (s:Sensor)-[:MADE]->(o:Observation)-[:OBSERVES]->(p:Property)
RETURN s.id, s.type, o.timestamp, o.value, p.name
ORDER BY o.timestamp DESC
LIMIT 50;

-- Query 6: Count by sensor type
MATCH (s:Sensor)
RETURN s.type, s.semantic_type, COUNT(s) AS count
ORDER BY count DESC;

-- Query 7: Get recent observations (last 24 hours)
MATCH (s:Sensor)-[:MADE]->(o:Observation)
WHERE o.timestamp >= datetime() - duration('P1D')
RETURN s.id, s.type, o.timestamp, o.value
ORDER BY o.timestamp DESC;

-- Query 8: Find sensors in same zone
MATCH (s1:Sensor)-[:IN_ZONE]->(z:Zone)<-[:IN_ZONE]-(s2:Sensor)
WHERE s1 <> s2
RETURN s1.id, s2.id, z.name
LIMIT 25;

-- ============================================
-- MAINTENANCE QUERIES
-- ============================================

-- Delete old observations (older than 2 years)
MATCH (o:Observation)
WHERE o.timestamp < datetime() - duration('P2Y')
DETACH DELETE o;

-- Update sensor last_seen
MATCH (s:Sensor {id: 'TEMP001'})
SET s.last_seen = datetime(), s.update_count = coalesce(s.update_count, 0) + 1;

-- ============================================
-- ADVANCED QUERIES
-- ============================================

-- Find correlated sensor readings (same timestamp)
MATCH (s1:Sensor {id: 'TEMP001'})-[:MADE]->(o1:Observation)
MATCH (s2:Sensor {id: 'HUM001'})-[:MADE]->(o2:Observation)
WHERE o1.timestamp = o2.timestamp
RETURN o1.timestamp, o1.value AS temperature, o2.value AS humidity
ORDER BY o1.timestamp DESC
LIMIT 100;

-- Get sensor network (all sensors and their observations)
MATCH (s:Sensor)-[r]->(o:Observation)
RETURN s, r, o
LIMIT 100;

-- Find anomalies (example: temperature > 40 or < 0)
MATCH (s:Sensor {type: 'temperature'})-[:MADE]->(o:Observation)
WHERE o.value > 40 OR o.value < 0
RETURN s.id, o.timestamp, o.value
ORDER BY o.timestamp DESC;

-- ============================================
-- GRAPH ANALYTICS
-- ============================================

-- Most active sensors
MATCH (s:Sensor)-[:MADE]->(o:Observation)
RETURN s.id, s.type, COUNT(o) AS observation_count
ORDER BY observation_count DESC
LIMIT 10;

-- Sensor connectivity
MATCH (s:Sensor)-[:MADE]->(o:Observation)-[:OBSERVES]->(p:Property)
RETURN s.id, p.name, COUNT(o) AS count
ORDER BY count DESC;

-- Time series analysis
MATCH (s:Sensor)-[:MADE]->(o:Observation)
WHERE s.type = 'temperature'
RETURN 
    o.timestamp,
    AVG(o.value) AS avg_temperature,
    MIN(o.value) AS min_temperature,
    MAX(o.value) AS max_temperature
ORDER BY o.timestamp
LIMIT 1000;

-- ============================================
-- UTILITY QUERIES
-- ============================================

-- Count all nodes
MATCH (n)
RETURN labels(n) AS node_type, COUNT(n) AS count;

-- Count all relationships
MATCH ()-[r]->()
RETURN type(r) AS relationship_type, COUNT(r) AS count;

-- Get graph schema
CALL db.schema.visualization();

-- Clear all data (use with caution!)
-- MATCH (n)
-- DETACH DELETE n;