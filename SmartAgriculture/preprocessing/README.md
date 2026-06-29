# Smart Agriculture - Preprocessing Module

This module implements the data preprocessing pipeline for the Smart Agriculture System. It ensures that collected sensor data is validated, cleaned, normalized, and enriched before being stored and used by AI models.

## 📋 Architecture

```
Kafka Consumer
      │
      ▼
Validation
      │
      ▼
Nettoyage (Cleaning)
      │
      ▼
Normalisation
      │
      ▼
Détection des anomalies (Outlier Detection)
      │
      ▼
Feature Engineering
      │
      ▼
Stockage (Storage)
```

## 📦 Components

### 1. Data Validator (`validator.py`)

Validates sensor data for completeness and correctness.

**Features:**
- Checks required fields (sensor_id, timestamp, sensor_type)
- Validates timestamp format (ISO 8601)
- Validates numeric values
- Sensor-specific field validation
- Batch validation support

**Usage:**
```python
from preprocessing.validator import validate_data

is_valid, message = validate_data(data)
if is_valid:
    print("Data is valid")
else:
    print(f"Validation failed: {message}")
```

### 2. Data Cleaner (`cleaner.py`)

Cleans and prepares sensor data for processing.

**Features:**
- Null/None value handling (converts to NaN)
- Type conversion (string to float)
- Duplicate detection and removal
- String whitespace cleaning
- Batch processing support
- Cleaning statistics tracking

**Usage:**
```python
from preprocessing.cleaner import clean_data

cleaned_data = clean_data(data)
```

### 3. Data Normalizer (`normalizer.py`)

Normalizes units and values across different sensor types.

**Features:**
- Unit conversion (K to °C, F to °C, cm to mm, etc.)
- Standardized units for all sensor types
- Sensor-specific normalization:
  - Temperature: K, F → °C
  - Humidity: % normalization
  - Soil moisture: % normalization
  - Light: Lux standardization
  - Wind: m/s, mph → km/h
  - GPS: ft → m
- Batch normalization support

**Usage:**
```python
from preprocessing.normalizer import normalize_data

normalized_data = normalize_data(data)
```

### 4. Outlier Detector (`outlier_detector.py`)

Detects anomalous sensor readings based on physical limits.

**Features:**
- Sensor-specific value limits:
  - Temperature: [-20, 60] °C
  - Humidity: [0, 100] %
  - Soil moisture: [0, 100] %
  - pH: [0, 14]
  - Wind: [0, 150] km/h
  - Light: [0, 120000] Lux
  - Rainfall: [0, 500] mm
- Complex sensor support (GPS, animal)
- Outlier marking or removal
- Batch detection support
- Statistics tracking

**Usage:**
```python
from preprocessing.outlier_detector import detect_outlier

is_outlier, reason = detect_outlier(data)
if is_outlier:
    print(f"Outlier detected: {reason}")
```

### 5. Feature Engineering (`feature_engineering.py`)

Creates additional features from sensor data for ML models.

**Features:**

**Time-based features:**
- year, month, day, hour, minute, second
- weekday (0=Monday, 6=Sunday)
- day_of_year
- is_weekend, is_night, is_morning, is_afternoon, is_evening
- season (winter, spring, summer, fall)
- Cyclic features: hour_sin, hour_cos, month_sin, month_cos

**Sensor-specific features:**
- Temperature: temp_category, gdd (Growing Degree Days)
- Humidity: humidity_category, dew_point
- Soil moisture: moisture_status
- pH: ph_category, ph_suitable
- Rainfall: rainfall_intensity, has_rain
- Light: light_category, par_approx
- Wind: wind_category, wind_cardinal
- Water quality: water_quality_index
- GPS: hemisphere, climate_zone, is_moving
- Animal: activity_category, temp_status, heart_rate_status

**Derived features:**
- heat_index (temperature + humidity)

**Usage:**
```python
from preprocessing.feature_engineering import create_features

data_with_features = create_features(data)
```

### 6. Preprocessing Pipeline (`pipeline_preprocessing.py`)

Orchestrates the complete preprocessing workflow.

**Features:**
- Sequential processing: Validation → Cleaning → Normalization → Outlier Detection → Feature Engineering
- Batch processing support
- Comprehensive statistics tracking
- Configurable outlier removal
- Detailed reporting
- Error handling

**Usage:**
```python
from preprocessing.pipeline_preprocessing import PreprocessingPipeline

# Create pipeline
pipeline = PreprocessingPipeline(remove_outliers=False)

# Process single data point
processed_data, is_success, message = pipeline.process(data)

# Process batch
processed_list, failed_list = pipeline.process_batch(data_list)

# Get statistics
stats = pipeline.get_stats()

# Print report
pipeline.print_report()
```

### 7. Quality Report (`quality_report.py`)

Generates comprehensive quality reports for monitoring and analysis.

**Features:**
- Summary statistics
- Validation metrics
- Cleaning statistics
- Normalization metrics
- Outlier detection statistics
- Feature engineering metrics
- Automated recommendations
- Sample data analysis
- Export to JSON
- Export to HTML

**Usage:**
```python
from preprocessing.quality_report import generate_quality_report, print_quality_report

# Generate report
report = generate_quality_report(pipeline_stats, sample_data)

# Print report
print_quality_report(pipeline_stats, sample_data)

# Export to JSON
from preprocessing.quality_report import QualityReport
report_gen = QualityReport()
report_gen.generate_report(stats)
report_gen.export_to_json('report.json')
report_gen.export_to_html('report.html')
```

## 🔧 Configuration

All configuration is managed through the `.env` file. No additional configuration needed for preprocessing.

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## 🚀 Usage

### Standalone Testing

Test the preprocessing pipeline:

```bash
python preprocessing/pipeline_preprocessing.py
```

This will:
1. Process sample data through the complete pipeline
2. Display detailed results for each step
3. Generate and print a comprehensive quality report

### Integration with ETL

Integrate preprocessing into the ETL pipeline:

```python
from ingestion.etl import ETLPipeline
from ingestion.postgres_loader import PostgresLoader
from preprocessing.pipeline_preprocessing import PreprocessingPipeline

# Initialize preprocessing pipeline
preprocessing = PreprocessingPipeline(remove_outliers=False)

# Initialize ETL and loaders
etl = ETLPipeline()
loader = PostgresLoader()
loader.connect()

# Process data with preprocessing
def process_with_preprocessing(data):
    # Apply preprocessing
    processed_data, is_success, message = preprocessing.process(data)
    
    if is_success:
        # Load to database
        loader.load(processed_data)
    
    return is_success

# Use in Kafka consumer
consumer.run(callback=process_with_preprocessing)
```

### Batch Processing

Process large datasets efficiently:

```python
from preprocessing.pipeline_preprocessing import PreprocessingPipeline

pipeline = PreprocessingPipeline()

# Load data
with open('sensor_data.json', 'r') as f:
    data_list = json.load(f)

# Process batch
processed, failed = pipeline.process_batch(data_list)

# Generate report
pipeline.print_report()

# Export results
with open('processed_data.json', 'w') as f:
    json.dump(processed, f)

with open('failed_data.json', 'w') as f:
    json.dump(failed, f)
```

## 📊 Data Flow

### Input Format

```json
{
  "sensor_id": "temp_sensor_001",
  "sensor_type": "temperature",
  "temperature": 25.5,
  "unit": "celsius",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Output Format

After preprocessing, data includes:

```json
{
  "sensor_id": "temp_sensor_001",
  "sensor_type": "temperature",
  "temperature": 25.5,
  "unit": "°C",
  "timestamp": "2024-01-01T12:00:00",
  
  // Validation
  "is_valid": true,
  
  // Cleaning
  "cleaned": true,
  
  // Normalization
  "unit_normalized": true,
  
  // Outlier detection
  "is_outlier": false,
  
  // Feature engineering
  "year": 2024,
  "month": 1,
  "day": 1,
  "hour": 12,
  "weekday": 0,
  "season": "winter",
  "temp_category": "moderate",
  "gdd": 15.5,
  "hour_sin": -0.5,
  "hour_cos": 0.866,
  
  // Metadata
  "processed_at": "2024-01-01T12:00:01.123456"
}
```

## 🔍 Monitoring and Statistics

### Pipeline Statistics

```python
stats = pipeline.get_stats()

# Example output:
{
    'total_received': 1000,
    'validation_failed': 5,
    'cleaning_failed': 10,
    'outliers_detected': 15,
    'successful': 970,
    'success_rate': 97.0,
    'by_sensor_type': {
        'temperature': 200,
        'humidity': 200,
        'soil_moisture': 150,
        ...
    },
    'cleaner': {
        'total_processed': 995,
        'null_values_cleaned': 20,
        'type_conversions': 15,
        'duplicates_removed': 10
    },
    'normalizer': {
        'total_processed': 985,
        'units_normalized': 50,
        'values_converted': 30
    },
    'outlier_detector': {
        'total_checked': 985,
        'outliers_detected': 15,
        'outliers_by_type': {
            'temperature': 5,
            'humidity': 10
        }
    },
    'feature_engineer': {
        'total_processed': 970,
        'features_created': 970
    }
}
```

## 🧪 Testing

### Test Individual Components

```python
# Test validator
from preprocessing.validator import validate_data
is_valid, msg = validate_data(test_data)

# Test cleaner
from preprocessing.cleaner import clean_data
cleaned = clean_data(test_data)

# Test normalizer
from preprocessing.normalizer import normalize_data
normalized = normalize_data(test_data)

# Test outlier detector
from preprocessing.outlier_detector import detect_outlier
is_outlier, reason = detect_outlier(test_data)

# Test feature engineering
from preprocessing.feature_engineering import create_features
with_features = create_features(test_data)
```

### Test Complete Pipeline

```bash
python preprocessing/pipeline_preprocessing.py
```

## 📈 Performance Optimization

### For High Throughput

1. **Batch processing:**
   ```python
   # Process in batches of 1000
   batch_size = 1000
   for i in range(0, len(data_list), batch_size):
       batch = data_list[i:i+batch_size]
       processed, failed = pipeline.process_batch(batch)
   ```

2. **Disable outlier removal for speed:**
   ```python
   pipeline = PreprocessingPipeline(remove_outliers=False)
   ```

3. **Skip feature engineering if not needed:**
   Modify pipeline to conditionally skip feature engineering

### For Development

1. **Enable debug logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Use smaller test datasets:**
   ```python
   test_data = data_list[:100]  # Test with first 100 records
   ```

## 🐛 Troubleshooting

### Common Issues

1. **Import errors:**
   ```bash
   # Ensure you're in the SmartAgriculture directory
   cd SmartAgriculture
   
   # Install dependencies
   pip install -r preprocessing/requirements.txt
   ```

2. **NumPy not found:**
   ```bash
   pip install numpy>=1.24.0
   ```

3. **Validation failures:**
   - Check that all required fields are present
   - Verify timestamp format is ISO 8601
   - Ensure sensor_type is specified

4. **Outlier detection too sensitive:**
   - Adjust limits in `outlier_detector.py`
   - Use `remove_outliers=False` to keep outliers

## 📝 Best Practices

1. **Always validate before processing:**
   ```python
   is_valid, msg = validate_data(data)
   if not is_valid:
       log_error(msg)
       return
   ```

2. **Monitor statistics:**
   ```python
   stats = pipeline.get_stats()
   if stats['success_rate'] < 90:
       alert_team()
   ```

3. **Generate regular reports:**
   ```python
   pipeline.print_report()
   # or
   report_gen.export_to_html('daily_report.html')
   ```

4. **Handle outliers appropriately:**
   - Mark outliers for investigation
   - Don't automatically remove unless certain
   - Log outlier reasons for analysis

5. **Use batch processing for large datasets:**
   ```python
   processed, failed = pipeline.process_batch(large_data_list)
   ```

## 🔐 Data Quality Guidelines

### Validation Rules

- **Required fields:** sensor_id, timestamp, sensor_type
- **Timestamp format:** ISO 8601 (e.g., "2024-01-01T12:00:00")
- **Numeric values:** Must be convertible to float
- **Sensor-specific:** Each sensor type has required fields

### Cleaning Rules

- **Null values:** Converted to NaN for numeric fields
- **Type conversion:** Strings converted to appropriate types
- **Duplicates:** Removed based on (sensor_id, timestamp) key
- **Strings:** Whitespace stripped

### Normalization Rules

- **Temperature:** All units → °C
- **Humidity:** All units → %
- **Soil moisture:** All units → %
- **pH:** Standardized to pH
- **Light:** All units → Lux
- **Wind:** All units → km/h
- **GPS:** Coordinates in decimal degrees

### Outlier Thresholds

| Sensor Type | Min | Max | Unit |
|-------------|-----|-----|------|
| Temperature | -20 | 60 | °C |
| Humidity | 0 | 100 | % |
| Soil Moisture | 0 | 100 | % |
| pH | 0 | 14 | pH |
| Wind | 0 | 150 | km/h |
| Light | 0 | 120000 | Lux |
| Rainfall | 0 | 500 | mm |

## 📚 Additional Resources

- [Data Validation Best Practices](https://docs.python.org/3/library/typing.html)
- [NumPy Documentation](https://numpy.org/doc/)
- [Data Cleaning Techniques](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [Feature Engineering Guide](https://scikit-learn.org/stable/modules/preprocessing.html)

## 📄 License

Part of the Smart Agriculture System project.