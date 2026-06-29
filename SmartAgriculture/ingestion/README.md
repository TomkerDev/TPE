# Smart Agriculture Ingestion Layer

This module implements the data collection and ingestion pipeline for the Smart Agriculture System. It handles the flow of sensor data from MQTT brokers through Kafka to multiple databases.

## 📋 Architecture

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

## 📦 Components

### 1. MQTT Subscriber (`mqtt_subscriber.py`)
- Subscribes to all sensor topics from MQTT broker
- Receives real-time sensor data
- Validates and enriches data
- Forwards data to Kafka

### 2. Kafka Producer (`kafka_producer.py`)
- Produces sensor data to Kafka topics
- Handles message serialization
- Provides batch sending capabilities
- Includes retry logic and acknowledgments

### 3. Kafka Consumer (`kafka_consumer.py`)
- Consumes messages from Kafka topics
- Processes sensor data
- Supports callback functions for ETL integration
- Handles graceful shutdown

### 4. ETL Pipeline (`etl.py`)
- **Extract**: Validates and parses incoming data
- **Transform**: Normalizes data based on sensor type
- **Load**: Distributes data to multiple databases
- Tracks processing statistics

### 5. Database Loaders

#### PostgreSQL Loader (`postgres_loader.py`)
- Stores sensor data in relational format
- Creates indexes for efficient querying
- Supports JSONB for flexible schema
- Generic table structure for all sensor types

#### TimescaleDB Loader (`timescaledb_loader.py`)
- Optimized for time-series data
- Creates hypertables per sensor type
- Automatic time-based partitioning
- Efficient time-range queries

#### MongoDB Loader (`mongodb_loader.py`)
- Document-based storage
- Flexible schema for diverse sensor data
- Automatic collection creation per sensor type
- Supports batch inserts

#### Neo4j Loader (`neo4j_loader.py`)
- Graph database for relationship analysis
- Creates Sensor and Reading nodes
- Establishes relationships between sensors
- Enables complex graph queries

### 6. Utilities (`utils.py`)
- Data validation functions
- Topic mapping (MQTT ↔ Kafka)
- Timestamp formatting
- Data enrichment helpers

## 🔧 Configuration

All configuration is managed through the `.env` file:

```env
# MQTT
MQTT_HOST=localhost
MQTT_PORT=1883

# Kafka
KAFKA_HOST=localhost:9092

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=agriculture
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123

# TimescaleDB
TIMESCALE_HOST=localhost
TIMESCALE_PORT=5433
TIMESCALE_DB=agriculture_ts

# MongoDB
MONGO_HOST=localhost
MONGO_PORT=27017

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## 🚀 Usage

### Running the Complete Pipeline

The ingestion pipeline consists of multiple components that work together:

#### 1. Start MQTT Subscriber (MQTT → Kafka)

```bash
python ingestion/mqtt_subscriber.py
```

This component:
- Connects to MQTT broker
- Subscribes to all sensor topics
- Receives data from sensors
- Forwards to Kafka

#### 2. Start Kafka Consumer with ETL (Kafka → Databases)

```bash
python ingestion/kafka_consumer.py
```

This component:
- Consumes messages from Kafka
- Processes through ETL pipeline
- Loads to all databases

#### 3. Run Complete Pipeline

For a complete end-to-end pipeline:

```python
from ingestion.mqtt_subscriber import MQTTSubscriber
from ingestion.kafka_consumer import KafkaDataConsumer
from ingestion.etl import ETLPipeline
from ingestion.postgres_loader import PostgresLoader
from ingestion.timescaledb_loader import TimescaleDBLoader
from ingestion.mongodb_loader import MongoDBLoader
from ingestion.neo4j_loader import Neo4jLoader

# Initialize loaders
loaders = [
    PostgresLoader(),
    TimescaleDBLoader(),
    MongoDBLoader(),
    Neo4jLoader()
]

# Connect all loaders
for loader in loaders:
    loader.connect()

# Create ETL pipeline
etl = ETLPipeline()

# Create consumer with ETL callback
consumer = KafkaDataConsumer()

def process_data(data, topic):
    etl.process(data, loaders)

consumer.run(callback=process_data)
```

### Testing Individual Components

#### Test MQTT Subscriber

```bash
python ingestion/mqtt_subscriber.py
```

#### Test Kafka Producer

```bash
python ingestion/kafka_producer.py
```

#### Test Kafka Consumer

```bash
python ingestion/kafka_consumer.py
```

#### Test ETL Pipeline

```bash
python ingestion/etl.py
```

#### Test Database Loaders

```bash
# PostgreSQL
python ingestion/postgres_loader.py

# TimescaleDB
python ingestion/timescaledb_loader.py

# MongoDB
python ingestion/mongodb_loader.py

# Neo4j
python ingestion/neo4j_loader.py
```

## 📊 Data Flow

### 1. Sensor Data Format

All sensors publish data in JSON format:

```json
{
  "sensor_id": "temp_sensor_1234",
  "sensor_type": "temperature",
  "temperature": 25.5,
  "unit": "celsius",
  "timestamp": "2024-01-01T12:00:00",
  "data_quality": 1.0
}
```

### 2. MQTT Topics

Sensors publish to MQTT topics:
- `agriculture/sensors/temperature`
- `agriculture/sensors/humidity`
- `agriculture/sensors/soil_moisture`
- `agriculture/sensors/ph`
- `agriculture/sensors/rainfall`
- `agriculture/sensors/light`
- `agriculture/sensors/wind`
- `agriculture/sensors/water_quality`
- `agriculture/sensors/gps`
- `agriculture/sensors/animal`

### 3. Kafka Topics

Data is forwarded to Kafka topics:
- `agriculture.temperature`
- `agriculture.humidity`
- `agriculture.soil_moisture`
- `agriculture.ph`
- `agriculture.rainfall`
- `agriculture.light`
- `agriculture.wind`
- `agriculture.water_quality`
- `agriculture.gps`
- `agriculture.animal`

### 4. Database Schemas

#### PostgreSQL

```sql
CREATE TABLE sensor_data (
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
```

#### TimescaleDB

```sql
CREATE TABLE temperature_metrics (
    time TIMESTAMP NOT NULL,
    sensor_id VARCHAR(255) NOT NULL,
    value FLOAT,
    unit VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT create_hypertable('temperature_metrics', 'time');
```

#### MongoDB

```javascript
// Collection: sensor_temperature
{
  "sensor_id": "temp_sensor_1234",
  "sensor_type": "temperature",
  "temperature": 25.5,
  "unit": "celsius",
  "timestamp": "2024-01-01T12:00:00",
  "processed_at": "2024-01-01T12:00:01",
  "data_quality": 1.0
}
```

#### Neo4j

```cypher
// Nodes
(s:Sensor {sensor_id: "temp_sensor_1234", sensor_type: "temperature"})
(r:Reading {value: 25.5, unit: "celsius", timestamp: "2024-01-01T12:00:00"})

// Relationships
(s)-[:HAS_READING]->(r)
(s1)-[:SAME_TYPE]->(s2)
```

## 🔍 Monitoring and Statistics

Each component provides statistics:

### ETL Statistics

```python
etl = ETLPipeline()
# ... process data ...
stats = etl.get_stats()
# Returns:
# {
#     'total_processed': 1000,
#     'successful': 995,
#     'failed': 5,
#     'by_sensor_type': {
#         'temperature': 200,
#         'humidity': 200,
#         ...
#     }
# }
```

### Database Statistics

```python
# PostgreSQL
loader = PostgresLoader()
stats = loader.get_stats()
# Returns list of dicts with count, earliest, latest per sensor_type

# TimescaleDB
loader = TimescaleDBLoader()
stats = loader.get_stats()
# Returns list of hypertables with record counts

# MongoDB
loader = MongoDBLoader()
stats = loader.get_stats()
# Returns list of collections with document counts

# Neo4j
loader = Neo4jLoader()
stats = loader.get_stats()
# Returns total sensors, readings, and breakdown by type
```

## 🐛 Troubleshooting

### MQTT Connection Issues
- Verify Mosquitto broker is running: `mosquitto -v`
- Check MQTT_HOST and MQTT_PORT in .env
- Test with: `python tests/test_mqtt.py`

### Kafka Connection Issues
- Verify Kafka broker is running
- Check KAFKA_HOST in .env
- Ensure Zookeeper is running (if needed)
- Test with: `python tests/test_kafka.py`

### Database Connection Issues
- Verify all database services are running
- Check credentials in .env
- Test with individual test scripts in `tests/` directory

### Data Not Flowing
1. Check MQTT subscriber is running
2. Verify Kafka topics are created
3. Check Kafka consumer is running
4. Verify ETL pipeline is processing
5. Check database connections

## 📝 Logging

All components use Python's logging module:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Log levels:
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

## ⚙️ Advanced Configuration

### Batch Processing

For high-throughput scenarios, use batch processing:

```python
# MongoDB batch insert
loader = MongoDBLoader()
data_list = [data1, data2, data3, ...]
loader.load_batch(data_list)

# Neo4j batch insert
loader = Neo4jLoader()
loader.load_batch(data_list)
```

### Custom ETL Processing

Extend the ETL pipeline with custom transformations:

```python
class CustomETL(ETLPipeline):
    def transform(self, data):
        # Custom transformation logic
        transformed = super().transform(data)
        # Add custom fields
        transformed['custom_field'] = 'custom_value'
        return transformed
```

### Multiple Kafka Consumers

Scale processing with multiple consumer instances:

```bash
# Terminal 1
python ingestion/kafka_consumer.py

# Terminal 2
python ingestion/kafka_consumer.py

# Terminal 3
python ingestion/kafka_consumer.py
```

Kafka will automatically load-balance across consumers in the same consumer group.

## 🔐 Security Considerations

1. **Never commit .env files** to version control
2. **Use strong passwords** for all databases
3. **Enable authentication** on MQTT and Kafka in production
4. **Use TLS/SSL** for database connections in production
5. **Implement access controls** for database users
6. **Rotate credentials** regularly

## 📈 Performance Tuning

### Kafka
- Adjust `batch.size` and `linger.ms` for batching
- Tune `max_in_flight_requests_per_connection`
- Use compression (`compression_type='gzip'`)

### Databases
- PostgreSQL: Connection pooling with pgBouncer
- TimescaleDB: Adjust chunk time intervals
- MongoDB: Use write concerns appropriately
- Neo4j: Use appropriate transaction sizes

### MQTT
- Use QoS levels appropriately (0, 1, or 2)
- Implement message batching for high throughput
- Consider MQTT v5 for better performance

## 🚨 Error Handling

All components include comprehensive error handling:

- **Connection failures**: Automatic retry with exponential backoff
- **Invalid data**: Logged and skipped, doesn't crash pipeline
- **Database errors**: Transaction rollback, error logging
- **Graceful shutdown**: Signal handlers for clean exit

## 📄 License

Part of the Smart Agriculture System project.