# Smart Agriculture Sensors

This module contains all sensor implementations for the Smart Agriculture System. The sensors simulate real-world agricultural data and publish it to MQTT and Kafka brokers.

## 📋 Prerequisites

- Python 3.8+
- MQTT Broker (Mosquitto) running on configured host/port
- Kafka Broker running on configured host/port
- Required Python packages (see requirements.txt)

## 🔧 Configuration

All configuration is managed through the `.env` file in the parent directory. Key configurations include:

- **MQTT**: Host and port for MQTT broker
- **Kafka**: Host and port for Kafka broker
- **Database**: Connection details for PostgreSQL, MongoDB, Neo4j

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## 🚀 Usage

### Running Individual Sensors

Each sensor can be run independently:

```bash
# Temperature sensor
python sensors/temperature_sensor.py

# Humidity sensor
python sensors/humidity_sensor.py

# Soil moisture sensor
python sensors/soil_moisture_sensor.py

# pH sensor
python sensors/ph_sensor.py

# Rainfall sensor
python sensors/rainfall_sensor.py

# Light sensor
python sensors/light_sensor.py

# Wind sensor
python sensors/wind_sensor.py

# Water quality sensor
python sensors/water_quality_sensor.py

# GPS sensor
python sensors/gps_sensor.py

# Animal sensor
python sensors/animal_sensor.py
```

### Running All Sensors

To run all sensors simultaneously:

```bash
python sensors/run_all_sensors.py
```

You'll be prompted to choose:
- **Option 1**: Sequential mode (runs one sensor at a time)
- **Option 2**: Parallel mode (runs all sensors simultaneously) - **Recommended**

Press `Ctrl+C` to stop all sensors gracefully.

## 📊 Sensor Types

### 1. Temperature Sensor
- **Topic**: `agriculture/sensors/temperature`
- **Data**: Temperature in Celsius
- **Range**: 15°C - 40°C
- **Update Interval**: 5 seconds (configurable)

### 2. Humidity Sensor
- **Topic**: `agriculture/sensors/humidity`
- **Data**: Humidity percentage
- **Range**: 30% - 90%
- **Update Interval**: 5 seconds

### 3. Soil Moisture Sensor
- **Topic**: `agriculture/sensors/soil_moisture`
- **Data**: Soil moisture percentage
- **Range**: 20% - 80%
- **Update Interval**: 5 seconds

### 4. pH Sensor
- **Topic**: `agriculture/sensors/ph`
- **Data**: pH level
- **Range**: 5.5 - 7.5
- **Update Interval**: 5 seconds

### 5. Rainfall Sensor
- **Topic**: `agriculture/sensors/rainfall`
- **Data**: Rainfall in mm (last hour)
- **Range**: 0 - 15 mm
- **Update Interval**: 5 seconds

### 6. Light Sensor
- **Topic**: `agriculture/sensors/light`
- **Data**: Light intensity in lux
- **Range**: 0 - 100,000 lux
- **Update Interval**: 5 seconds

### 7. Wind Sensor
- **Topic**: `agriculture/sensors/wind`
- **Data**: Wind speed (km/h) and direction (degrees)
- **Range**: 0 - 25 km/h, 0-360°
- **Update Interval**: 5 seconds

### 8. Water Quality Sensor
- **Topic**: `agriculture/sensors/water_quality`
- **Data**: pH, dissolved oxygen, turbidity, conductivity
- **Update Interval**: 5 seconds

### 9. GPS Sensor
- **Topic**: `agriculture/sensors/gps`
- **Data**: Latitude, longitude, altitude, speed
- **Update Interval**: 5 seconds

### 10. Animal Sensor
- **Topic**: `agriculture/sensors/animal`
- **Data**: Animal ID, activity level, body temperature, heart rate, location, health status
- **Update Interval**: 5 seconds

## 🔍 Testing Connection

Before running sensors, test your connections:

```bash
# Test PostgreSQL connection
python tests/test_postgres.py

# Test Kafka connection
python tests/test_kafka.py

# Test MQTT connection
python tests/test_mqtt.py

# Test Neo4j connection
python tests/test_neo4j.py

# Test MongoDB connection
python tests/test_mongodb.py
```

## 📡 Data Flow

```
Sensors → Publisher → MQTT Broker → Consumers
                      → Kafka Broker → Consumers
```

Each sensor:
1. Reads simulated data
2. Adds timestamp and sensor type
3. Publishes to MQTT topic
4. Publishes to Kafka topic

## 🏗️ Architecture

```
sensors/
├── config.py              # Configuration management
├── publisher.py           # MQTT and Kafka publisher
├── temperature_sensor.py  # Temperature sensor
├── humidity_sensor.py     # Humidity sensor
├── soil_moisture_sensor.py # Soil moisture sensor
├── ph_sensor.py           # pH sensor
├── rainfall_sensor.py     # Rainfall sensor
├── light_sensor.py        # Light sensor
├── wind_sensor.py         # Wind sensor
├── water_quality_sensor.py # Water quality sensor
├── gps_sensor.py          # GPS sensor
├── animal_sensor.py       # Animal sensor
├── run_all_sensors.py     # Run all sensors
└── requirements.txt       # Python dependencies
```

## ⚙️ Configuration Options

### Sensor Update Interval

Modify the `interval` parameter when running sensors:

```python
sensor.run(interval=10)  # Update every 10 seconds
```

### Parallel Execution

The `run_all_sensors.py` uses `ThreadPoolExecutor` for parallel execution. Adjust `max_workers` if needed:

```python
with ThreadPoolExecutor(max_workers=10) as executor:
```

## 🐛 Troubleshooting

### MQTT Connection Failed
- Ensure Mosquitto broker is running
- Check MQTT_HOST and MQTT_PORT in .env
- Verify firewall settings

### Kafka Connection Failed
- Ensure Kafka broker is running
- Check KAFKA_HOST in .env
- Verify Zookeeper is running (if required)

### Import Errors
- Ensure you're running from the SmartAgriculture directory
- Check that all sensor files are present
- Verify Python path includes the sensors directory

## 📝 Notes

- All sensor data is simulated for testing purposes
- In production, replace simulation logic with actual sensor readings
- Sensors run indefinitely until interrupted (Ctrl+C)
- Each sensor has a unique ID generated on initialization
- Data is published in JSON format

## 🔐 Security

- Never commit `.env` file to version control
- Use environment variables for sensitive data
- Implement authentication for MQTT and Kafka in production

## 📄 License

Part of the Smart Agriculture System project.