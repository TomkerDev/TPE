# Smart Agriculture System - Execution Guide

This guide provides step-by-step instructions for running the complete Smart Agriculture System pipeline.

## 📋 Prerequisites

- Docker and Docker Compose installed
- Python 3.8+
- Git (optional)

## 🏗️ Architecture Overview

```
┌─────────────┐
│   Sensors   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ MQTT Broker │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ MQTT Subscriber  │
└──────┬───────────┘
       │
       ▼
┌─────────────┐
│   Kafka     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Kafka Consumer│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    ETL      │
└──────┬──────┘
       │
       ├────────► PostgreSQL
       ├────────► TimescaleDB
       ├────────► MongoDB
       └────────► Neo4j
```

## 🚀 Execution Order

### Step 1: Start Docker Services

```bash
cd SmartAgriculture
docker-compose up -d
```

This starts all required services:
- PostgreSQL (port 5432)
- TimescaleDB (port 5433)
- MongoDB (port 27017)
- Neo4j (bolt:7687, http:7474)
- Mosquitto MQTT Broker (port 1883)
- Kafka (port 9092)
- Zookeeper (port 2181)

**Verify services are running:**
```bash
docker-compose ps
```

**Check service logs if needed:**
```bash
docker-compose logs -f [service_name]
```

### Step 2: Initialize PostgreSQL

```bash
# Option 1: Using psql command
psql -h localhost -U admin -d agriculture -f database/init_postgres.sql

# Option 2: Using Docker exec
docker exec -i smartagriculture-postgres psql -U admin -d agriculture < database/init_postgres.sql
```

**Verify PostgreSQL:**
```bash
python tests/test_postgres.py
```

### Step 3: Initialize TimescaleDB

```bash
# Option 1: Using psql command
psql -h localhost -p 5433 -U admin -d agriculture_ts -f database/init_timescaledb.sql

# Option 2: Using Docker exec
docker exec -i smartagriculture-timescaledb psql -U admin -d agriculture_ts < database/init_timescaledb.sql
```

**Verify TimescaleDB:**
```bash
# Connect to TimescaleDB
psql -h localhost -p 5433 -U admin -d agriculture_ts

# Check hypertables
SELECT hypertable_name FROM timescaledb_information.hypertables;
```

### Step 4: Initialize MongoDB

MongoDB doesn't require manual initialization - collections are created automatically by the loader.

**Verify MongoDB:**
```bash
python tests/test_mongodb.py
```

### Step 5: Initialize Neo4j

Neo4j constraints and indexes are created automatically by the loader.

**Verify Neo4j:**
```bash
python tests/test_neo4j.py
```

**Access Neo4j Browser:**
- URL: http://localhost:7474
- Username: neo4j
- Password: password

### Step 6: Verify MQTT Broker

```bash
python tests/test_mqtt.py
```

**Test MQTT manually:**
```bash
# Subscribe to a topic
mosquitto_sub -h localhost -t "agriculture/sensors/#" -v

# Publish a test message
mosquitto_pub -h localhost -t "agriculture/sensors/temperature" -m '{"sensor_id":"test","sensor_type":"temperature","temperature":25.5}'
```

### Step 7: Verify Kafka

```bash
python tests/test_kafka.py
```

**Test Kafka manually:**
```bash
# List topics
docker exec smartagriculture-kafka kafka-topics.sh --list --bootstrap-server localhost:9092

# Create a test topic
docker exec smartagriculture-kafka kafka-topics.sh --create --topic test --bootstrap-server localhost:9092

# Consume messages
docker exec smartagriculture-kafka kafka-console-consumer.sh --topic test --from-beginning --bootstrap-server localhost:9092
```

### Step 8: Start Sensor Simulation

Open a new terminal and run:

```bash
cd SmartAgriculture
python sensors/run_all_sensors.py
```

**Select mode:**
- Option 1: Sequential (one sensor at a time)
- Option 2: Parallel (all sensors simultaneously) - **Recommended**

**Expected output:**
```
============================================================
Initializing Smart Agriculture Sensors...
============================================================
✓ 10 sensors initialized successfully

Select running mode:
1. Sequential (one sensor at a time)
2. Parallel (all sensors simultaneously)

Enter your choice (1 or 2, default=2): 2

============================================================
Running sensors in PARALLEL
============================================================

[Temperature] Starting...
[Humidity] Starting...
[Soil Moisture] Starting...
...
```

**Keep this terminal running.**

### Step 9: Start MQTT Subscriber

Open a new terminal:

```bash
cd SmartAgriculture
python ingestion/mqtt_subscriber.py
```

**Expected output:**
```
✓ Connected to MQTT Broker: localhost:1883
  Subscribed to: agriculture/sensors/#
✓ Kafka producer initialized: localhost:9092

============================================================
MQTT Subscriber is running...
Press Ctrl+C to stop
============================================================
```

**Keep this terminal running.**

### Step 10: Start Complete Pipeline

Open a new terminal:

```bash
cd SmartAgriculture
python ingestion/pipeline.py
```

**Expected output:**
```
============================================================
Smart Agriculture - Complete Pipeline
============================================================

Checking required services...

Service endpoints:
  MQTT: localhost:1883
  Kafka: localhost:9092
  PostgreSQL: localhost:5432
  TimescaleDB: localhost:5433
  MongoDB: localhost:27017
  Neo4j: localhost:7687

⚠ Make sure all services are running before starting the pipeline!
  Use Docker Compose: docker-compose up -d
  Or start services individually

Start the pipeline? (y/n): y

============================================================
Initializing Database Connections...
============================================================

1. Connecting to PostgreSQL...
✓ PostgreSQL connected

2. Connecting to TimescaleDB...
✓ TimescaleDB connected

3. Connecting to MongoDB...
✓ MongoDB connected

4. Connecting to Neo4j...
✓ Neo4j connected

✓ All 4 databases connected successfully

============================================================
Initializing ETL Pipeline...
============================================================
✓ ETL Pipeline initialized

============================================================
Starting MQTT Subscriber...
============================================================
✓ MQTT Subscriber started in background

============================================================
Starting Kafka Consumer with ETL...
============================================================
✓ Kafka Consumer started in background

============================================================
Starting Sensor Simulation...
============================================================
✓ Sensors started in background

============================================================
✓ COMPLETE PIPELINE IS RUNNING
============================================================

Data flow:
  Sensors → MQTT → Kafka → ETL → Databases

Press Ctrl+C to stop
```

## 📊 Monitoring the Pipeline

### View Real-time Statistics

The pipeline automatically prints statistics every 30 seconds:

```
------------------------------------------------------------
Pipeline Statistics:
------------------------------------------------------------
ETL: 150 processed (150 successful, 0 failed)
PostgresLoader: [{'sensor_type': 'temperature', 'count': 50, ...}]
TimescaleDBLoader: [{'sensor_type': 'temperature', 'count': 50, ...}]
MongoDBLoader: [{'sensor_type': 'temperature', 'count': 50, ...}]
Neo4jLoader: {'total_sensors': 10, 'total_readings': 150, ...}
------------------------------------------------------------
```

### Query PostgreSQL

```bash
psql -h localhost -U admin -d agriculture

# View latest readings
SELECT * FROM latest_sensor_readings LIMIT 10;

# View statistics
SELECT * FROM sensor_statistics;

# Query specific sensor
SELECT * FROM sensor_data 
WHERE sensor_id = 'temp_sensor_1234' 
ORDER BY timestamp DESC 
LIMIT 10;
```

### Query TimescaleDB

```bash
psql -h localhost -p 5433 -U admin -d agriculture_ts

# View hypertables
SELECT hypertable_name FROM timescaledb_information.hypertables;

# Query time-series data
SELECT * FROM temperature_metrics 
ORDER BY time DESC 
LIMIT 10;

# Get hourly averages
SELECT * FROM temperature_hourly_avg 
ORDER BY bucket DESC 
LIMIT 10;
```

### Query MongoDB

```bash
# Using MongoDB shell
docker exec -it smartagriculture-mongodb mongosh

# Switch to database
use agriculture

# View collections
show collections

# Query temperature data
db.sensor_temperature.find().limit(10).pretty()

# Count documents
db.sensor_temperature.countDocuments()
```

### Query Neo4j

```bash
# Using Neo4j Browser (http://localhost:7474)

# Count sensors
MATCH (s:Sensor) RETURN count(s) AS total_sensors;

# Count readings
MATCH (r:Reading) RETURN count(r) AS total_readings;

# Get sensor types
MATCH (s:Sensor) 
RETURN s.sensor_type AS type, count(s) AS count 
ORDER BY count DESC;

# Get readings for a specific sensor
MATCH (s:Sensor {sensor_id: "temp_sensor_1234"})-[:HAS_READING]->(r:Reading)
RETURN r
ORDER BY r.timestamp DESC
LIMIT 10;

# Find sensors of same type
MATCH (s1:Sensor {sensor_id: "temp_sensor_1234"})-[:SAME_TYPE]->(s2)
RETURN s2.sensor_id, s2.sensor_type;
```

## 🔧 Troubleshooting

### Services Won't Start

```bash
# Check Docker logs
docker-compose logs

# Restart services
docker-compose restart

# Recreate services
docker-compose down
docker-compose up -d
```

### Connection Errors

1. **Check if services are running:**
   ```bash
   docker-compose ps
   ```

2. **Verify ports are not in use:**
   ```bash
   # Windows
   netstat -ano | findstr :5432
   
   # Linux/Mac
   lsof -i :5432
   ```

3. **Check firewall settings**

### No Data Flowing

1. **Check MQTT subscriber is running:**
   - Look for "✓ Connected to MQTT Broker" in subscriber terminal

2. **Check Kafka topics:**
   ```bash
   docker exec smartagriculture-kafka kafka-topics.sh --list --bootstrap-server localhost:9092
   ```

3. **Check Kafka consumer:**
   - Look for "📨 [N] Processed message" in pipeline terminal

4. **Check ETL processing:**
   - Look for "✓ Processed" messages in logs

### Database Errors

1. **PostgreSQL:**
   ```bash
   # Check if database exists
   docker exec smartagriculture-postgres psql -U admin -l
   
   # Create database if needed
   docker exec smartagriculture-postgres psql -U admin -c "CREATE DATABASE agriculture;"
   ```

2. **TimescaleDB:**
   ```bash
   # Check if extension is enabled
   docker exec smartagriculture-timescaledb psql -U admin -d agriculture_ts -c "SELECT * FROM pg_extension WHERE extname = 'timescaledb';"
   ```

3. **MongoDB:**
   ```bash
   # Check connection
   docker exec smartagriculture-mongodb mongosh --eval "db.adminCommand('ping')"
   ```

4. **Neo4j:**
   ```bash
   # Check connection
   curl -H "Content-Type: application/json" -X POST -d '{"password":"password"}' http://localhost:7474/db/user/neo4j/authenticate
   ```

## 🛑 Stopping the Pipeline

### Graceful Shutdown

Press `Ctrl+C` in the pipeline terminal. This will:
1. Stop all sensors
2. Stop MQTT subscriber
3. Stop Kafka consumer
4. Close all database connections

### Stop All Services

```bash
# Stop pipeline components (Ctrl+C in each terminal)

# Stop Docker services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

## 📈 Performance Optimization

### For High Throughput

1. **Increase Kafka batch size:**
   ```python
   # In kafka_producer.py
   KafkaProducer(
       batch_size=16384,  # 16KB batches
       linger_ms=10,      # Wait 10ms for batching
       compression_type='gzip'
   )
   ```

2. **Use connection pooling:**
   ```python
   # For PostgreSQL
   from psycopg2.pool import SimpleConnectionPool
   ```

3. **Increase consumer parallelism:**
   ```bash
   # Run multiple consumers
   python ingestion/kafka_consumer.py  # Terminal 1
   python ingestion/kafka_consumer.py  # Terminal 2
   python ingestion/kafka_consumer.py  # Terminal 3
   ```

### For Development

1. **Reduce sensor interval:**
   ```python
   manager.run_all_parallel(interval=2)  # 2 seconds instead of 5
   ```

2. **Enable debug logging:**
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

## 🔐 Security Notes

1. **Change default passwords** in `.env` file
2. **Enable authentication** on MQTT and Kafka for production
3. **Use TLS/SSL** for database connections
4. **Restrict network access** to database ports
5. **Never commit `.env`** to version control

## 📝 Quick Reference

### Start Everything (Quick)

```bash
# Terminal 1: Start services
cd SmartAgriculture
docker-compose up -d

# Terminal 2: Initialize databases
psql -h localhost -U admin -d agriculture -f database/init_postgres.sql
psql -h localhost -p 5433 -U admin -d agriculture_ts -f database/init_timescaledb.sql

# Terminal 3: Start complete pipeline
python ingestion/pipeline.py
```

### Stop Everything (Quick)

```bash
# Terminal 1: Stop pipeline (Ctrl+C)

# Terminal 2: Stop services
docker-compose down
```

### Test Individual Components

```bash
# Test connections
python tests/test_postgres.py
python tests/test_mqtt.py
python tests/test_kafka.py
python tests/test_neo4j.py
python tests/test_mongodb.py

# Test components
python ingestion/etl.py
python ingestion/postgres_loader.py
python ingestion/timescaledb_loader.py
python ingestion/mongodb_loader.py
python ingestion/neo4j_loader.py
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [MQTT Protocol](https://mqtt.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Neo4j Documentation](https://neo4j.com/docs/)

## 🆘 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify all services are running: `docker-compose ps`
3. Test individual components using test scripts
4. Check firewall and network settings
5. Ensure ports are not in use by other applications