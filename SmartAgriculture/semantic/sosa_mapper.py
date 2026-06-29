"""
SOSA/SSN Mapper
Maps sensor types to semantic web ontologies (SOSA/SSN)
"""
from typing import Dict, Any
import logging

from semantic.ontology import SOSA, AGRI

logger = logging.getLogger(__name__)


# Mapping from sensor types to SOSA/SSN semantic labels
SENSOR_TYPE_SEMANTIC_MAP = {
    "temperature": "AirTemperature",
    "humidity": "RelativeHumidity",
    "soil_moisture": "SoilMoisture",
    "ph": "SoilPH",
    "rainfall": "Rainfall",
    "light": "SolarRadiation",
    "wind": "WindSpeed",
    "water_quality": "WaterQuality",
    "gps": "GPSLocation",
    "animal": "AnimalMonitoring"
}

# Mapping to SOSA classes
SENSOR_CLASS_MAP = {
    "temperature": SOSA.AirTemperature,
    "humidity": SOSA.RelativeHumidity,
    "soil_moisture": AGRI.SoilMoisture,
    "ph": AGRI.SoilPH,
    "rainfall": SOSA.Rainfall,
    "light": SOSA.SolarRadiation,
    "wind": SOSA.WindSpeed,
    "water_quality": AGRI.WaterQuality,
    "gps": AGRI.GPSLocation,
    "animal": AGRI.AnimalMonitoring
}

# Mapping to property URIs
PROPERTY_URI_MAP = {
    "temperature": SOSA.hasSimpleResult,
    "humidity": SOSA.hasSimpleResult,
    "soil_moisture": AGRI.hasMoistureLevel,
    "ph": AGRI.hasPHLevel,
    "rainfall": SOSA.hasSimpleResult,
    "light": SOSA.hasSimpleResult,
    "wind": SOSA.hasSimpleResult,
    "water_quality": AGRI.hasWaterQuality,
    "gps": AGRI.hasLocation,
    "animal": AGRI.hasHealthStatus
}


class SOSAMapper:
    """Maps sensor data to SOSA/SSN ontology"""
    
    def __init__(self):
        self.mapping_stats = {
            'total_mapped': 0,
            'unknown_types': 0
        }
        
    def get_semantic_label(self, sensor_type: str) -> str:
        """
        Get semantic label for sensor type
        
        Args:
            sensor_type: Type of sensor
            
        Returns:
            Semantic label string
        """
        label = SENSOR_TYPE_SEMANTIC_MAP.get(sensor_type, "Unknown")
        
        if label == "Unknown":
            self.mapping_stats['unknown_types'] += 1
            logger.warning(f"Unknown sensor type: {sensor_type}")
        
        self.mapping_stats['total_mapped'] += 1
        return label
    
    def get_sensor_class(self, sensor_type: str):
        """
        Get SOSA/SSN class for sensor type
        
        Args:
            sensor_type: Type of sensor
            
        Returns:
            RDF class URI
        """
        return SENSOR_CLASS_MAP.get(sensor_type, SOSA.Sensor)
    
    def get_property_uri(self, sensor_type: str):
        """
        Get property URI for sensor type
        
        Args:
            sensor_type: Type of sensor
            
        Returns:
            Property URI
        """
        return PROPERTY_URI_MAP.get(sensor_type, SOSA.hasSimpleResult)
    
    def map_sensor_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map sensor data to semantic format
        
        Args:
            data: Sensor data dictionary
            
        Returns:
            Data with semantic mappings added
        """
        sensor_type = data.get('sensor_type')
        
        if not sensor_type:
            logger.warning("No sensor_type in data")
            return data
        
        # Create a copy to avoid modifying original
        mapped_data = data.copy()
        
        # Add semantic label
        mapped_data['semantic_label'] = self.get_semantic_label(sensor_type)
        
        # Add SOSA class
        mapped_data['sosa_class'] = str(self.get_sensor_class(sensor_type))
        
        # Add property URI
        mapped_data['property_uri'] = str(self.get_property_uri(sensor_type))
        
        # Add SOSA/SSN type
        mapped_data['@type'] = self._get_jsonld_type(sensor_type)
        
        return mapped_data
    
    def _get_jsonld_type(self, sensor_type: str) -> str:
        """Get JSON-LD @type for sensor type"""
        
        type_mapping = {
            'temperature': 'sosa:AirTemperature',
            'humidity': 'sosa:RelativeHumidity',
            'soil_moisture': 'agri:SoilMoisture',
            'ph': 'agri:SoilPH',
            'rainfall': 'sosa:Rainfall',
            'light': 'sosa:SolarRadiation',
            'wind': 'sosa:WindSpeed',
            'water_quality': 'agri:WaterQuality',
            'gps': 'agri:GPSLocation',
            'animal': 'agri:AnimalMonitoring'
        }
        
        return type_mapping.get(sensor_type, 'sosa:Sensor')
    
    def get_observation_type(self, sensor_type: str) -> str:
        """
        Get observation type for sensor
        
        Args:
            sensor_type: Type of sensor
            
        Returns:
            Observation type string
        """
        observation_types = {
            "temperature": "AirTemperatureObservation",
            "humidity": "HumidityObservation",
            "soil_moisture": "SoilMoistureObservation",
            "ph": "PHObservation",
            "rainfall": "RainfallObservation",
            "light": "LightIntensityObservation",
            "wind": "WindObservation",
            "water_quality": "WaterQualityObservation",
            "gps": "LocationObservation",
            "animal": "AnimalHealthObservation"
        }
        
        return observation_types.get(sensor_type, "Observation")
    
    def get_observed_property(self, sensor_type: str) -> str:
        """
        Get observed property name
        
        Args:
            sensor_type: Type of sensor
            
        Returns:
            Property name string
        """
        properties = {
            "temperature": "airTemperature",
            "humidity": "relativeHumidity",
            "soil_moisture": "soilMoisture",
            "ph": "soilPH",
            "rainfall": "rainfall",
            "light": "solarRadiation",
            "wind": "windSpeed",
            "water_quality": "waterQuality",
            "gps": "location",
            "animal": "healthStatus"
        }
        
        return properties.get(sensor_type, "measurement")
    
    def map_batch(self, data_list: list) -> list:
        """
        Map a batch of sensor data
        
        Args:
            data_list: List of sensor data dictionaries
            
        Returns:
            List of mapped data dictionaries
        """
        return [self.map_sensor_data(data) for data in data_list]
    
    def get_stats(self) -> Dict[str, int]:
        """Get mapping statistics"""
        return self.mapping_stats.copy()
    
    def reset_stats(self):
        """Reset mapping statistics"""
        self.mapping_stats = {
            'total_mapped': 0,
            'unknown_types': 0
        }


def semantic_label(sensor_type: str) -> str:
    """
    Convenience function to get semantic label
    
    Args:
        sensor_type: Type of sensor
        
    Returns:
        Semantic label string
    """
    mapper = SOSAMapper()
    return mapper.get_semantic_label(sensor_type)


def map_to_semantic(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to map sensor data to semantic format
    
    Args:
        data: Sensor data dictionary
        
    Returns:
        Mapped data dictionary
    """
    mapper = SOSAMapper()
    return mapper.map_sensor_data(data)


def get_all_semantic_mappings() -> Dict[str, Dict[str, str]]:
    """
    Get all semantic mappings
    
    Returns:
        Dictionary of all mappings
    """
    return {
        'labels': SENSOR_TYPE_SEMANTIC_MAP,
        'classes': {k: str(v) for k, v in SENSOR_CLASS_MAP.items()},
        'properties': {k: str(v) for k, v in PROPERTY_URI_MAP.items()}
    }