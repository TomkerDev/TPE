"""
JSON-LD Converter
Converts JSON sensor data to JSON-LD format for semantic web
"""
import json
from typing import Dict, Any
from pyld import jsonld
from datetime import datetime
import logging

from semantic.ontology import EX, GEO, SOSA

logger = logging.getLogger(__name__)


# JSON-LD Context definition
JSONLD_CONTEXT = {
    "@context": {
        "sensor_id": "ex:sensorID",
        "sensor_type": "ex:sensorType",
        "type": "ex:sensorType",
        "value": "ex:value",
        "unit": "ex:unit",
        "timestamp": "ex:timestamp",
        "latitude": "geo:lat",
        "longitude": "geo:long",
        "temperature": "ex:temperature",
        "humidity": "ex:humidity",
        "soil_moisture": "ex:soilMoisture",
        "ph": "ex:ph",
        "rainfall": "ex:rainfall",
        "light_intensity": "ex:lightIntensity",
        "wind_speed": "ex:windSpeed",
        "wind_direction": "ex:windDirection",
        "dissolved_oxygen": "ex:dissolvedOxygen",
        "turbidity": "ex:turbidity",
        "conductivity": "ex:conductivity",
        "altitude": "ex:altitude",
        "speed": "ex:speed",
        "animal_id": "ex:animalID",
        "activity_level": "ex:activityLevel",
        "body_temperature": "ex:bodyTemperature",
        "heart_rate": "ex:heartRate",
        "location_zone": "ex:locationZone",
        "health_status": "ex:healthStatus",
        "ex": "http://example.org/agriculture/",
        "geo": "http://www.opengis.net/ont/geosparql#",
        "sosa": "http://www.w3.org/ns/sosa/",
        "ssn": "http://www.w3.org/ns/ssn/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "xsd": "http://www.w3.org/2001/XMLSchema#"
    }
}


class JSONLDConverter:
    """Converts JSON data to JSON-LD format"""
    
    def __init__(self, base_uri: str = "http://example.org/agriculture/"):
        """
        Initialize JSON-LD converter
        
        Args:
            base_uri: Base URI for resources
        """
        self.base_uri = base_uri
        self.context = JSONLD_CONTEXT
        
    def convert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert JSON data to JSON-LD format
        
        Args:
            data: JSON data dictionary
            
        Returns:
            JSON-LD document
        """
        try:
            # Create a copy of the data
            doc = data.copy()
            
            # Add @context
            doc['@context'] = self.context['@context']
            
            # Add @id for the sensor
            if 'sensor_id' in doc:
                doc['@id'] = f"ex:sensor/{doc['sensor_id']}"
            
            # Add @type based on sensor type
            if 'sensor_type' in doc:
                sensor_type = doc['sensor_type']
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
                doc['@type'] = type_mapping.get(sensor_type, 'sosa:Sensor')
            
            # Compact the JSON-LD document
            compacted = jsonld.compact(doc, self.context)
            
            logger.debug(f"Converted data to JSON-LD: {compacted.get('@id', 'unknown')}")
            return compacted
            
        except Exception as e:
            logger.error(f"Failed to convert to JSON-LD: {e}")
            return data
    
    def convert_batch(self, data_list: list) -> list:
        """
        Convert a batch of JSON data to JSON-LD
        
        Args:
            data_list: List of JSON data dictionaries
            
        Returns:
            List of JSON-LD documents
        """
        return [self.convert(data) for data in data_list]
    
    def expand(self, jsonld_data: Dict[str, Any]) -> list:
        """
        Expand JSON-LD document
        
        Args:
            jsonld_data: JSON-LD document
            
        Returns:
            Expanded JSON-LD document
        """
        try:
            return jsonld.expand(jsonld_data)
        except Exception as e:
            logger.error(f"Failed to expand JSON-LD: {e}")
            return []
    
    def flatten(self, jsonld_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten JSON-LD document
        
        Args:
            jsonld_data: JSON-LD document
            
        Returns:
            Flattened JSON-LD document
        """
        try:
            return jsonld.flatten(jsonld_data)
        except Exception as e:
            logger.error(f"Failed to flatten JSON-LD: {e}")
            return jsonld_data
    
    def frame(self, jsonld_data: Dict[str, Any], frame: Dict[str, Any]) -> Dict[str, Any]:
        """
        Frame JSON-LD document
        
        Args:
            jsonld_data: JSON-LD document
            frame: Frame to apply
            
        Returns:
            Framed JSON-LD document
        """
        try:
            return jsonld.frame(jsonld_data, frame)
        except Exception as e:
            logger.error(f"Failed to frame JSON-LD: {e}")
            return jsonld_data


def convert_to_jsonld(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to convert JSON to JSON-LD
    
    Args:
        data: JSON data dictionary
        
    Returns:
        JSON-LD document
    """
    converter = JSONLDConverter()
    return converter.convert(data)


def create_observation_framing() -> Dict[str, Any]:
    """
    Create a frame for observations
    
    Returns:
        Frame dictionary
    """
    return {
        "@context": JSONLD_CONTEXT['@context'],
        "@type": "sosa:Observation",
        "sosa:hasSimpleResult": {},
        "sosa:resultTime": {},
        "sosa:madeBySensor": {
            "@type": "sosa:Sensor",
            "sosa:hasProperty": {}
        }
    }


def create_sensor_framing() -> Dict[str, Any]:
    """
    Create a frame for sensors
    
    Returns:
        Frame dictionary
    """
    return {
        "@context": JSONLD_CONTEXT['@context'],
        "@type": "sosa:Sensor",
        "sosa:madeObservation": {
            "@type": "sosa:Observation"
        }
    }