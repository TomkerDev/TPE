# Smart Agriculture - Semantic Integration Module

This module implements semantic integration and interoperability for the Smart Agriculture System. It converts sensor data through semantic web formats (JSON-LD, RDF) and aligns it with standard ontologies (SOSA/SSN) before storing in a Neo4j knowledge graph.

## 📋 Architecture

```
Sensors
   │
   ▼
JSON Data
   │
   ▼
JSON-LD (Linked Data)
   │
   ▼
RDF (Resource Description Framework)
   │
   ▼
SSN/SOSA Ontology Alignment
   │
   ▼
Neo4j Knowledge Graph
   │
   ▼
AI Applications
```

## 📦 Components

### 1. Ontology Definitions (`ontology.py`)

Defines namespaces and ontologies used for semantic integration.

**Features:**
- Standard ontologies: SOSA, SSN, GEO (GeoSPARQL)
- Custom agriculture ontology (AGRI)
- Sensor type mappings to SOSA/SSN classes
- Property mappings for different sensor types
- Complete ontology in Turtle format

**Usage:**
```python
from semantic.ontology import SOSA, SSN, EX, AGRI, get_sensor_class

# Get SOSA class for sensor type
sensor_class = get_sensor_class('temperature')  # Returns SOSA.AirTemperature

# Use namespaces
sensor_uri = EX + "sensor/temp_001"
```

### 2. JSON-LD Converter (`jsonld_converter.py`)

Converts JSON sensor data to JSON-LD format for semantic web.

**Features:**
- JSON to JSON-LD conversion
- Context definition with all sensor fields
- @id and @type generation
- Batch conversion support
- JSON-LD operations (expand, flatten, frame)

**Usage:**
```python
from semantic.jsonld_converter import JSONLDConverter, convert_to_jsonld

# Using class
converter = JSONLDConverter()
jsonld_data = converter.convert(json_data)

# Using convenience function
jsonld_data = convert_to_jsonld(json_data)

# Expand JSON-LD
expanded = converter.expand(jsonld_data)

# Frame JSON-LD
framed = converter.frame(jsonld_data, frame)
```

**Example Input/Output:**

Input:
```json
{
  "sensor_id": "TEMP001",
  "sensor_type": "temperature",
  "temperature": 28.4,
  "unit": "°C",
  "timestamp": "2024-01-01T12:30:00"
}
```

Output (JSON-LD):
```json
{
  "@context": {
    "sensor_id": "ex:sensorID",
    "sensor_type": "ex:sensorType",
    "temperature": "ex:temperature",
    "unit": "ex:unit",
    "timestamp": "ex:timestamp",
    "ex": "http://example.org/agriculture/",
    "sosa": "http://www.w3.org/ns/sosa/"
  },
  "@id": "ex:sensor/TEMP001",
  "@type": "sosa:AirTemperature",
  "sensor_id": "TEMP001",
  "sensor_type": "temperature",
  "temperature": 28.4,
  "unit": "°C",
  "timestamp": "2024-01-01T12:30:00"
}
```

### 3. RDF Converter (`rdf_converter.py`)

Converts JSON-LD data to RDF graph format.

**Features:**
- JSON-LD to RDF conversion
- Sensor and observation creation
- SOSA/SSN triple generation
- Sensor-specific properties
- GeoSPARQL support for GPS data
- Batch conversion
- Serialization (XML, Turtle, JSON-LD, N-Triples)
- SPARQL query support

**Usage:**
```python
from semantic.rdf_converter import RDFConverter, convert_to_rdf

# Convert to RDF
converter = RDFConverter()
graph = converter.convert(jsonld_data)

# Serialize to file
converter.serialize(format='turtle', destination='output.ttl')

# Query with SPARQL
results = converter.query("""
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    SELECT ?observation ?value
    WHERE {
        ?sensor sosa:madeObservation ?observation .
        ?observation sosa:hasSimpleResult ?value .
    }
""")
```

**RDF Output Example:**
```turtle
@prefix sosa: <http://www.w3.org/ns/sosa/> .
@prefix ex: <http://example.org/agriculture/> .

ex:sensor/TEMP001 a sosa:AirTemperature ;
    rdfs:label "Sensor TEMP001" ;
    sosa:madeObservation ex:observation/TEMP001/2024-01-01T12:30:00 .

ex:observation/TEMP001/2024-01-01T12-30-00 a sosa:Observation ;
    sosa:hasSimpleResult 28.4 ;
    sosa:resultTime "2024-01-01T12:30:00"^^xsd:dateTime .
```

### 4. SOSA Mapper (`sosa_mapper.py`)

Maps sensor types to SOSA/SSN ontology concepts.

**Features:**
- Sensor type to semantic label mapping
- SOSA/SSN class mapping
- Property URI mapping
- JSON-LD @type generation
- Batch mapping support
- Statistics tracking

**Usage:**
```python
from semantic.sosa_mapper import SOSAMapper, semantic_label, map_to_semantic

# Get semantic label
label = semantic_label('temperature')  # Returns "AirTemperature"

# Map sensor data
mapper = SOSAMapper()
mapped_data = mapper.map_sensor_data(data)
# Adds: semantic_label, sosa_class, property_uri, @type

# Get all mappings
from semantic.sosa_mapper import get_all_semantic_mappings
mappings = get_all_semantic_mappings()
```

**Sensor Type Mappings:**

| Sensor Type | Semantic Label | SOSA Class |
|-------------|----------------|------------|
| temperature | AirTemperature | sosa:AirTemperature |
| humidity | RelativeHumidity | sosa:RelativeHumidity |
| soil_moisture | SoilMoisture | agri:SoilMoisture |
| ph | SoilPH | agri:SoilPH |
| rainfall | Rainfall | sosa:Rainfall |
| light | SolarRadiation | sosa:SolarRadiation |
| wind | WindSpeed | sosa:WindSpeed |
| water_quality | WaterQuality | agri:WaterQuality |
| gps | GPSLocation | agri:GPSLocation |
| animal | AnimalMonitoring | agri:AnimalMonitoring |

### 5. Neo4j Graph Manager (`neo4j_graph.py`)

Manages the semantic knowledge graph in Neo4j.

**Features:**
- Neo4j connection management
- Constraint and index creation
- Semantic data insertion
- Sensor-specific relationships (GPS, Animal, Zones)
- Batch insertion
- Query support (observations, sensors by type)
- Graph statistics
- Graph clearing (for testing)

**Usage:**
```python
from semantic.neo4j_graph import Neo4jGraphManager

# Initialize manager
manager = Neo4jGraphManager(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# Connect
manager.connect()

# Insert semantic data
success = manager.insert_semantic_data(mapped_data)

# Query observations
observations = manager.query_sensor_observations("temp_sensor_001", limit=100)

# Get statistics
stats = manager.get_statistics()

# Close connection
manager.close()
```

**Graph Schema:**
```
(Sensor)-[:MADE]->(Observation)-[:OBSERVES]->(Property)
   │
   ├─[:LOCATED_AT]->(Location) [for GPS sensors]
   ├─[:MONITORS]->(Animal) [for animal sensors]
   └─[:IN_ZONE]->(Zone) [if location_zone specified]
```

### 6. SPARQL Queries (`sparql_queries.py`)

Pre-defined SPARQL queries for semantic data.

**Features:**
- Complete SPARQL query library
- Query executor for RDF graphs
- Common queries for sensors, observations, statistics
- Time-range queries
- Location-based queries
- Anomaly detection queries
- Correlation queries

**Usage:**
```python
from semantic.sparql_queries import SPARQLQueries, QueryExecutor

# Get pre-defined queries
all_sensors_query = SPARQLQueries.get_all_sensors()
observations_query = SPARQLQueries.get_sensor_observations("temp_001", limit=100)
stats_query = SPARQLQueries.get_sensor_statistics("temp_001")

# Execute queries
executor = QueryExecutor(rdf_graph)
results = executor.execute(all_sensors_query)

# Print results
executor.execute_and_print(all_sensors_query)
```

**Available Queries:**
- `get_all_sensors()` - Get all sensors
- `get_sensor_observations(sensor_id, limit)` - Get observations for a sensor
- `get_latest_observation(sensor_id)` - Get latest observation
- `get_observations_by_type(sensor_type, limit)` - Get by type
- `get_observations_in_timerange(start, end)` - Get by time range
- `get_sensor_statistics(sensor_id)` - Get sensor statistics
- `get_all_sensor_types()` - Get all sensor types
- `get_sensors_by_location(lat, long, radius)` - Get nearby sensors
- `get_animal_health_status(animal_id)` - Get animal health
- `get_farm_summary()` - Get farm overview
- `get_anomalies()` - Get anomalous readings
- `get_correlated_observations(sensor1, sensor2)` - Get correlated data

### 7. Semantic Pipeline (`semantic_pipeline.py`)

Orchestrates the complete semantic processing workflow.

**Features:**
- End-to-end semantic processing
- JSON → JSON-LD → RDF → Neo4j
- Batch processing support
- Statistics tracking
- RDF file saving (optional)
- Comprehensive reporting

**Usage:**
```python
from semantic.semantic_pipeline import SemanticPipeline

# Initialize pipeline
pipeline = SemanticPipeline(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    save_rdf=False
)

# Connect to Neo4j
pipeline.connect_neo4j()

# Process single data point
jsonld_data, rdf_graph, success = pipeline.process(data)

# Process batch
jsonld_list, rdf_graphs, failed = pipeline.process_batch(data_list)

# Get statistics
stats = pipeline.get_stats()

# Print report
pipeline.print_report()

# Close connections
pipeline.close()
```

**Pipeline Flow:**
```
1. Map to semantic format (SOSA/SSN)
   ↓
2. Convert to JSON-LD
   ↓
3. Convert to RDF
   ↓
4. Insert into Neo4j Knowledge Graph
   ↓
5. (Optional) Save RDF to file
```

## 🔧 Configuration

All configuration is managed through the `.env` file:

```env
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

### Standalone Testing

Test the semantic pipeline:

```bash
python semantic/semantic_pipeline.py
```

This will:
1. Process sample sensor data
2. Convert through JSON-LD and RDF
3. Insert into Neo4j knowledge graph
4. Display comprehensive report

### Integration with ETL

Integrate semantic processing into the ETL pipeline:

```python
from ingestion.etl import ETLPipeline
from ingestion.neo4j_loader import Neo4jLoader
from semantic.semantic_pipeline import SemanticPipeline

# Initialize semantic pipeline
semantic = SemanticPipeline()
semantic.connect_neo4j()

# Initialize ETL
etl = ETLPipeline()

# Process with semantic enrichment
def process_with_semantic(data):
    # Standard ETL processing
    processed = etl.process(data)
    
    # Add semantic processing
    jsonld_data, rdf_graph, success = semantic.process(processed)
    
    return processed

# Use in Kafka consumer
consumer.run(callback=process_with_semantic)
```

### Querying the Knowledge Graph

```python
from semantic.sparql_queries import SPARQLQueries, QueryExecutor
from semantic.rdf_converter import RDFConverter

# Convert data to RDF
converter = RDFConverter()
graph = converter.convert(data)

# Execute SPARQL queries
executor = QueryExecutor(graph)

# Get all sensors
results = executor.execute(SPARQLQueries.get_all_sensors())

# Get sensor statistics
results = executor.execute(SPARQLQueries.get_sensor_statistics("temp_001"))

# Print results
executor.execute_and_print(SPARQLQueries.get_farm_summary())
```

### Cypher Queries in Neo4j

Query the knowledge graph using Cypher:

```cypher
// Get all sensors and their observations
MATCH (s:Sensor)-[:MADE]->(o:Observation)-[:OBSERVES]->(p:Property)
RETURN s.id, s.type, o.timestamp, o.value, p.name
ORDER BY o.timestamp DESC

// Get sensor statistics
MATCH (s:Sensor {id: "temp_sensor_001"})-[:MADE]->(o:Observation)
RETURN 
    s.id,
    COUNT(o) as observation_count,
    MIN(o.timestamp) as first_reading,
    MAX(o.timestamp) as last_reading,
    AVG(o.value) as avg_value

// Find sensors by type
MATCH (s:Sensor {type: "temperature"})
RETURN s.id, s.semantic_type, s.last_seen
ORDER BY s.last_seen DESC

// Get correlated observations
MATCH (s1:Sensor {id: "temp_001"})-[:MADE]->(o1:Observation)
MATCH (s2:Sensor {id: "humidity_001"})-[:MADE]->(o2:Observation)
WHERE o1.timestamp = o2.timestamp
RETURN o1.timestamp, o1.value as temperature, o2.value as humidity
```

## 📊 Data Flow

### Semantic Processing Stages

1. **JSON Input**: Raw sensor data
   ```json
   {"sensor_id": "TEMP001", "sensor_type": "temperature", "temperature": 25.5}
   ```

2. **SOSA Mapping**: Add semantic labels
   ```python
   data['semantic_label'] = "AirTemperature"
   data['sosa_class'] = "http://www.w3.org/ns/sosa/AirTemperature"
   data['@type'] = "sosa:AirTemperature"
   ```

3. **JSON-LD**: Add linked data context
   ```json
   {
     "@context": {...},
     "@id": "ex:sensor/TEMP001",
     "@type": "sosa:AirTemperature",
     ...
   }
   ```

4. **RDF**: Create semantic triples
   ```turtle
   ex:sensor/TEMP001 a sosa:AirTemperature .
   ex:sensor/TEMP001 sosa:madeObservation ex:obs_001 .
   ex:obs_001 sosa:hasSimpleResult 25.5 .
   ```

5. **Neo4j**: Store in knowledge graph
   ```
   (Sensor:TEMP001)-[:MADE]->(Observation:obs_001)-[:OBSERVES]->(Property:AirTemperature)
   ```

## 🔍 Monitoring and Statistics

### Pipeline Statistics

```python
stats = pipeline.get_stats()

# Example output:
{
    'total_processed': 1000,
    'jsonld_converted': 1000,
    'rdf_converted': 1000,
    'neo4j_inserted': 995,
    'failed': 5,
    'success_rate': 99.5,
    'by_sensor_type': {
        'temperature': 300,
        'humidity': 300,
        'soil_moisture': 200,
        ...
    },
    'neo4j_stats': {
        'sensors': 50,
        'observations': 10000,
        'properties': 10,
        'relationships': 10050
    }
}
```

### Graph Statistics

```python
stats = manager.get_statistics()
# Returns: sensors, observations, properties, relationships counts
```

## 🧪 Testing

### Test Individual Components

```python
# Test JSON-LD conversion
from semantic.jsonld_converter import convert_to_jsonld
jsonld = convert_to_jsonld(data)

# Test RDF conversion
from semantic.rdf_converter import convert_to_rdf
graph = convert_to_rdf(data)

# Test SOSA mapping
from semantic.sosa_mapper import semantic_label
label = semantic_label('temperature')  # "AirTemperature"

# Test Neo4j insertion
from semantic.neo4j_graph import insert_semantic_data
success = insert_semantic_data(mapped_data)
```

### Test Complete Pipeline

```bash
python semantic/semantic_pipeline.py
```

## 📈 Performance Optimization

### For High Throughput

1. **Batch processing:**
   ```python
   jsonld_list, rdf_graphs, failed = pipeline.process_batch(data_list)
   ```

2. **Disable RDF saving:**
   ```python
   pipeline = SemanticPipeline(save_rdf=False)
   ```

3. **Use connection pooling for Neo4j**

### For Development

1. **Enable debug logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Save RDF for inspection:**
   ```python
   pipeline = SemanticPipeline(save_rdf=True)
   ```

## 🐛 Troubleshooting

### Common Issues

1. **Import errors:**
   ```bash
   # Ensure you're in the SmartAgriculture directory
   cd SmartAgriculture
   
   # Install dependencies
   pip install -r semantic/requirements.txt
   ```

2. **Neo4j connection issues:**
   - Verify Neo4j is running: `docker-compose ps neo4j`
   - Check credentials in `.env`
   - Test connection: `python tests/test_neo4j.py`

3. **RDF serialization errors:**
   - Ensure all URIs are valid
   - Check for circular references
   - Verify namespace bindings

4. **JSON-LD compaction issues:**
   - Ensure @context is properly defined
   - Check for missing required fields
   - Verify JSON-LD syntax

## 📝 Best Practices

1. **Always validate before semantic processing:**
   ```python
   is_valid, msg = validate_data(data)
   if not is_valid:
       return
   ```

2. **Use batch processing for large datasets:**
   ```python
   jsonld_list, rdf_graphs, failed = pipeline.process_batch(data_list)
   ```

3. **Monitor statistics:**
   ```python
   stats = pipeline.get_stats()
   if stats['success_rate'] < 95:
       alert_team()
   ```

4. **Save RDF for audit trail:**
   ```python
   pipeline = SemanticPipeline(save_rdf=True)
   ```

5. **Use appropriate Neo4j constraints:**
   ```python
   manager.ensure_constraints()
   ```

## 🔐 Interoperability Standards

### Implemented Standards

- **JSON-LD**: JSON for Linked Data (W3C Recommendation)
- **RDF**: Resource Description Framework (W3C Recommendation)
- **SOSA**: Sensor, Observation, Sample, and Actuator (W3C/OGC)
- **SSN**: Semantic Sensor Network (W3C Recommendation)
- **GeoSPARQL**: Geographic queries in RDF (OGC Standard)

### Benefits

1. **Syntactic Interoperability**: JSON-LD provides standard data format
2. **Semantic Interoperability**: SOSA/SSN ontologies provide common vocabulary
3. **Organizational Interoperability**: Neo4j graph enables complex queries
4. **AI/ML Ready**: Structured data for machine learning models

## 📚 Additional Resources

- [SOSA/SSN Ontology](https://www.w3.org/TR/vocab-ssn/)
- [JSON-LD Specification](https://www.w3.org/TR/json-ld/)
- [RDF Specification](https://www.w3.org/RDF/)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [GeoSPARQL](https://www.opengeospatial.org/standards/geosparql)
- [rdflib Documentation](https://rdflib.readthedocs.io/)
- [pyld Documentation](https://github.com/digitalbazaar/pyld)

## 📄 License

Part of the Smart Agriculture System project.