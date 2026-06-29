-- =============================================================================
-- Smart Agriculture Platform - PostgreSQL/TimescaleDB Initialization Script
-- =============================================================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- =============================================================================
-- Sensor Registry Table (Structured metadata about sensors)
-- =============================================================================

CREATE TABLE IF NOT EXISTS sensors (
    sensor_id VARCHAR(255) PRIMARY KEY,
    sensor_type VARCHAR(100) NOT NULL,  -- temperature, humidity, soil_moisture, etc.
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    firmware_version VARCHAR(50),
    installation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location_lat DECIMAL(10, 8),
    location_lon DECIMAL(11, 8),
    location_description TEXT,
    field_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',  -- active, inactive, maintenance
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sensors_type ON sensors(sensor_type);
CREATE INDEX idx_sensors_field ON sensors(field_id);
CREATE INDEX idx_sensors_status ON sensors(status);
CREATE INDEX idx_sensors_metadata ON sensors USING GIN(metadata);

-- =============================================================================
-- Raw Sensor Data Table (Time-series data)
-- =============================================================================

CREATE TABLE IF NOT EXISTS sensor_readings_raw (
    time TIMESTAMP NOT NULL,
    sensor_id VARCHAR(255) NOT NULL,
    measurement_type VARCHAR(100) NOT NULL,
    value DECIMAL(15, 6),
    unit VARCHAR(50),
    raw_payload JSONB,
    quality_score DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('sensor_readings_raw', 'time', if_not_exists => TRUE);

-- Create indexes for time-series queries
CREATE INDEX idx_sensor_readings_sensor_time ON sensor_readings_raw(sensor_id, time DESC);
CREATE INDEX idx_sensor_readings_type_time ON sensor_readings_raw(measurement_type, time DESC);
CREATE INDEX idx_sensor_readings_raw_payload ON sensor_readings_raw USING GIN(raw_payload);

-- =============================================================================
# Smart Agriculture Platform - Database Schema

## Architecture Overview

This project implements a **multi-layer interoperable architecture** for heterogeneous agricultural sensor integration, combining:

- **Semantic Interoperability**: SSN/SOSA ontology + JSON-LD
- **Hybrid Storage**: PostgreSQL + TimescaleDB + MongoDB
- **Data Quality Pipeline**: Validation → Cleaning → Semantic Enrichment
- **AI/ML Integration**: Predictive analytics and anomaly detection

## Project Structure

```
SmartAgriculture/
├── docker/                    # Docker configuration
│   ├── docker-compose.yml    # Multi-container orchestration
│   ├── mosquitto/            # MQTT broker configuration
│   └── init/                 # Database initialization scripts
├── data/                     # Data storage
│   ├── raw/                  # Raw sensor data
│   ├── processed/            # Cleaned and normalized data
│   ├── models/               # Trained ML models
│   └── results/              # Analysis results and predictions
├── sensors/                  # Sensor drivers and adapters
├── ingestion/                # Data ingestion layer (MQTT, APIs)
├── preprocessing/            # Data validation and cleaning
├── semantic/                 # Semantic enrichment (SSN/SOSA, JSON-LD)
├── database/                 # Database models and migrations
├── analytics/                # AI/ML models and predictions
├── dashboard/                # Web visualization interface
├── notebooks/                # Jupyter notebooks for exploration
├── api/                      # REST API and microservices
└── tests/                    # Unit and integration tests
```

## Key Features

### 1. Multi-Layer Architecture
- **Acquisition Layer**: MQTT broker (Mosquitto) for real-time sensor data
- **Ingestion Layer**: Multi-protocol support (MQTT, HTTP, CoAP)
- **Preprocessing Layer**: Data validation, cleaning, normalization
- **Semantic Layer**: SSN/SOSA ontology-based interoperability
- **Storage Layer**: Hybrid database architecture
- **Analytics Layer**: AI/ML for predictions and anomaly detection
- **Presentation Layer**: Interactive dashboard

### 2. Semantic Interoperability
- **SSN/SOSA Ontology**: W3C Semantic Sensor Network standard
- **JSON-LD**: Linked data format for semantic enrichment
- **Ontology Alignment**: Mapping between heterogeneous sensor models
- **Knowledge Graph**: Agricultural domain knowledge representation

### 3. Hybrid Storage Architecture
- **PostgreSQL**: Structured metadata and sensor registry
- **TimescaleDB**: Time-series sensor readings (hypertables)
- **MongoDB**: Semi-structured data, JSON-LD documents, logs
- **Redis**: Caching and real-time message queuing

### 4. Data Quality Pipeline
- **Validation**: Schema validation, range checks, format verification
- **Cleaning**: Outlier detection, missing value imputation
- **Normalization**: Unit conversion, standardization
- **Enrichment**: Semantic annotation, context addition

### 5. AI/ML Integration
- **Predictive Analytics**: Crop yield prediction, resource optimization
- **Anomaly Detection**: Sensor fault detection, environmental anomalies
- **Time-Series Forecasting**: ARIMA, LSTM, Prophet models
- **Classification**: Disease detection, stress identification

## Technology Stack

### Backend
- **Python 3.11+**: Core programming language
- **FastAPI**: REST API framework
- **SQLAlchemy**: ORM for PostgreSQL/TimescaleDB
- **Motor**: Async MongoDB driver
- **Pydantic**: Data validation and settings

### Data Processing
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Scikit-learn**: Machine learning
- **TensorFlow/PyTorch**: Deep learning (optional)
- **RDFLib**: Semantic web and JSON-LD processing

### Messaging & Integration
- **MQTT**: Eclipse Mosquitto broker
- **paho-mqtt**: MQTT client library
- **Redis**: Caching and pub/sub

### Frontend
- **React**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Chart.js/Recharts**: Data visualization
- **Material-UI**: Component library

### Infrastructure
- **Docker & Docker Compose**: Containerization
- **PostgreSQL 15**: Relational database
- **TimescaleDB 2.11**: Time-series extension
- **MongoDB 7.0**: Document database
- **Redis 7.2**: In-memory cache

## Getting Started

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11 or higher
- Node.js 18+ (for dashboard development)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SmartAgriculture
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services with Docker**
   ```bash
   docker-compose up -d
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize databases**
   ```bash
   docker-compose exec postgres psql -U smartagri -d smartagriculture -f /docker-entrypoint-initdb.d/init.sql
   ```

6. **Access the dashboard**
   ```
   http://localhost:3000
   ```

7. **Access the API documentation**
   ```
   http://localhost:8000/docs
   ```

## Project Modules

### Sensors Module (`sensors/`)
- Sensor drivers and adapters
- Protocol implementations (MQTT, HTTP, Modbus, etc.)
- Sensor data models and parsers

### Ingestion Module (`ingestion/`)
- MQTT message handlers
- Data ingestion pipelines
- Protocol adapters
- Message queue consumers

### Preprocessing Module (`preprocessing/`)
- Data validation rules
- Outlier detection algorithms
- Missing value imputation
- Unit conversion and normalization

### Semantic Module (`semantic/`)
- SSN/SOSA ontology definitions
- JSON-LD context and serialization
- Semantic annotation engine
- Ontology alignment tools

### Database Module (`database/`)
- SQLAlchemy models
- Database migrations (Alembic)
- Repository patterns
- Connection management

### Analytics Module (`analytics/`)
- Time-series forecasting models
- Anomaly detection algorithms
- Predictive models (crop yield, resource needs)
- Model training and evaluation pipelines

### Dashboard Module (`dashboard/`)
- React-based web interface
- Real-time data visualization
- Interactive charts and maps
- Alert management interface

### API Module (`api/`)
- FastAPI REST endpoints
- Authentication and authorization
- API versioning
- OpenAPI documentation

## Data Flow

```
Sensors → MQTT Broker → Ingestion Service → Preprocessing → 
Semantic Enrichment → Storage (PostgreSQL/TimescaleDB/MongoDB) → 
Analytics (AI/ML) → API → Dashboard
```

## Configuration

### Environment Variables (.env)
```env
# Database Configuration
POSTGRES_USER=smartagri
POSTGRES_PASSWORD=your_password
POSTGRES_DB=smartagriculture
MONGO_USER=smartagri
MONGO_PASSWORD=your_password
MONGO_DB=smartagriculture

# MQTT Configuration
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USER=sensor_user
MQTT_PASSWORD=sensor_pass

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your_secret_key
```

## Development

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=.

# Run specific test module
pytest tests/test_ingestion.py
```

### Code Quality
```bash
# Linting
flake8 .

# Type checking
mypy .

# Formatting
black .
```

### Jupyter Notebooks
```bash
# Start Jupyter Lab
jupyter lab --notebook-dir=notebooks/
```

## Scientific Contributions

This project provides:

1. **Original Multi-Layer Architecture**: Integrating acquisition, normalization, interoperability, storage, and AI
2. **Semantic Interoperability Model**: Based on SSN/SOSA and JSON-LD standards
3. **Hybrid Storage Architecture**: Combining PostgreSQL, TimescaleDB, and MongoDB
4. **Data Quality Pipeline**: Validation, cleaning, and semantic enrichment
5. **Native AI Integration**: Predictive analytics and agricultural anomaly detection
6. **Methodological Framework**: Reference for developing interoperable smart agriculture platforms

## Deployment

### Production Deployment
```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale analytics=3
```

### Monitoring
- Health checks: `http://localhost:8000/health`
- Metrics: Prometheus + Grafana (optional)
- Logs: `docker-compose logs -f [service-name]`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]

## Contact

[Your Contact Information]

## References

- W3C SSN/SOSA Ontology: https://www.w3.org/TR/vocab-ssn/
- JSON-LD Specification: https://json-ld.org/
- TimescaleDB Documentation: https://docs.timescale.com/
- MQTT Protocol: https://mqtt.org/