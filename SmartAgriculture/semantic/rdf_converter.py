"""
RDF Converter
Converts JSON-LD data to RDF format for semantic web applications
"""
from typing import Dict, Any, Optional
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD
from datetime import datetime
import logging

from semantic.ontology import SOSA, SSN, EX, AGRI, get_sensor_class, get_property_uri

logger = logging.getLogger(__name__)


class RDFConverter:
    """Converts JSON-LD data to RDF format"""
    
    def __init__(self, base_uri: str = "http://example.org/agriculture/"):
        """
        Initialize RDF converter
        
        Args:
            base_uri: Base URI for resources
        """
        self.base_uri = base_uri
        self.graph = None
        
    def convert(self, data: Dict[str, Any]) -> Graph:
        """
        Convert JSON-LD data to RDF graph
        
        Args:
            data: JSON-LD data dictionary
            
        Returns:
            RDF Graph
        """
        try:
            # Create new graph
            self.graph = Graph()
            
            # Bind namespaces
            self.graph.bind('sosa', SOSA)
            self.graph.bind('ssn', SSN)
            self.graph.bind('ex', EX)
            self.graph.bind('agri', AGRI)
            self.graph.bind('rdf', RDF)
            self.graph.bind('rdfs', RDFS)
            self.graph.bind('xsd', XSD)
            
            # Extract sensor information
            sensor_id = data.get('sensor_id')
            sensor_type = data.get('sensor_type')
            timestamp = data.get('timestamp')
            value = data.get('value')
            
            if not sensor_id:
                logger.warning("No sensor_id provided")
                return self.graph
            
            # Create sensor URI
            sensor_uri = URIRef(EX + f"sensor/{sensor_id}")
            
            # Add sensor type
            sensor_class = get_sensor_class(sensor_type)
            self.graph.add((sensor_uri, RDF.type, sensor_class))
            
            # Add sensor properties
            self.graph.add((sensor_uri, RDFS.label, Literal(f"Sensor {sensor_id}")))
            
            # Create observation URI
            obs_id = f"observation/{sensor_id}/{timestamp}"
            if isinstance(timestamp, str):
                obs_id = f"observation/{sensor_id}/{timestamp.replace(':', '-').replace('.', '-')}"
            observation_uri = URIRef(EX + obs_id)
            
            # Add observation
            self.graph.add((observation_uri, RDF.type, SOSA.Observation))
            
            # Link sensor to observation
            self.graph.add((sensor_uri, SOSA.madeObservation, observation_uri))
            
            # Add observation result
            if value is not None:
                self.graph.add((observation_uri, SOSA.hasSimpleResult, Literal(value, datatype=XSD.float)))
            
            # Add observation time
            if timestamp:
                if isinstance(timestamp, str):
                    self.graph.add((observation_uri, SOSA.resultTime, Literal(timestamp, datatype=XSD.dateTime)))
                elif isinstance(timestamp, datetime):
                    self.graph.add((observation_uri, SOSA.resultTime, Literal(timestamp.isoformat(), datatype=XSD.dateTime)))
            
            # Add sensor-specific properties
            self._add_sensor_specific_triples(data, sensor_uri, observation_uri)
            
            logger.debug(f"Converted sensor {sensor_id} to RDF")
            return self.graph
            
        except Exception as e:
            logger.error(f"Failed to convert to RDF: {e}")
            return Graph()
    
    def _add_sensor_specific_triples(self, data: Dict[str, Any], 
                                     sensor_uri: URIRef, 
                                     observation_uri: URIRef):
        """Add sensor-specific RDF triples"""
        
        sensor_type = data.get('sensor_type')
        
        # Temperature sensor
        if sensor_type == 'temperature':
            self.graph.add((observation_uri, SOSA.hasSimpleResult, Literal(data.get('temperature'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasUnit, Literal(data.get('unit', '°C'))))
        
        # Humidity sensor
        elif sensor_type == 'humidity':
            self.graph.add((observation_uri, SOSA.hasSimpleResult, Literal(data.get('humidity'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasUnit, Literal(data.get('unit', '%'))))
        
        # Soil moisture sensor
        elif sensor_type == 'soil_moisture':
            self.graph.add((observation_uri, AGRI.hasMoistureLevel, Literal(data.get('soil_moisture'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasUnit, Literal(data.get('unit', '%'))))
        
        # pH sensor
        elif sensor_type == 'ph':
            self.graph.add((observation_uri, AGRI.hasPHLevel, Literal(data.get('ph'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasUnit, Literal(data.get('unit', 'pH'))))
        
        # Rainfall sensor
        elif sensor_type == 'rainfall':
            self.graph.add((observation_uri, SOSA.hasSimpleResult, Literal(data.get('rainfall'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasUnit, Literal(data.get('unit', 'mm'))))
            self.graph.add((observation_uri, AGRI.hasPeriod, Literal(data.get('period', 'last_hour'))))
        
        # Light sensor
        elif sensor_type == 'light':
            self.graph.add((observation_uri, SOSA.hasSimpleResult, Literal(data.get('light_intensity'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasUnit, Literal(data.get('unit', 'Lux'))))
        
        # Wind sensor
        elif sensor_type == 'wind':
            self.graph.add((observation_uri, SOSA.hasSimpleResult, Literal(data.get('wind_speed'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasWindDirection, Literal(data.get('wind_direction'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasUnit, Literal(data.get('unit_speed', 'km/h'))))
        
        # Water quality sensor
        elif sensor_type == 'water_quality':
            self.graph.add((observation_uri, AGRI.hasPH, Literal(data.get('ph'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasDissolvedOxygen, Literal(data.get('dissolved_oxygen'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasTurbidity, Literal(data.get('turbidity'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasConductivity, Literal(data.get('conductivity'), datatype=XSD.float)))
        
        # GPS sensor
        elif sensor_type == 'gps':
            # Create geometry
            geom_uri = URIRef(EX + f"geometry/{data.get('sensor_id')}/{data.get('timestamp')}")
            self.graph.add((geom_uri, RDF.type, GEO.Geometry))
            self.graph.add((geom_uri, GEO.asWKT, Literal(f"POINT({data.get('longitude')} {data.get('latitude')})", datatype=GEO.wktLiteral)))
            self.graph.add((observation_uri, GEO.hasGeometry, geom_uri))
            
            self.graph.add((observation_uri, AGRI.hasAltitude, Literal(data.get('altitude'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasSpeed, Literal(data.get('speed'), datatype=XSD.float)))
        
        # Animal sensor
        elif sensor_type == 'animal':
            self.graph.add((observation_uri, AGRI.hasAnimalID, Literal(data.get('animal_id'))))
            self.graph.add((observation_uri, AGRI.hasActivityLevel, Literal(data.get('activity_level'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasBodyTemperature, Literal(data.get('body_temperature'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasHeartRate, Literal(data.get('heart_rate'), datatype=XSD.float)))
            self.graph.add((observation_uri, AGRI.hasLocationZone, Literal(data.get('location_zone'))))
            self.graph.add((observation_uri, AGRI.hasHealthStatus, Literal(data.get('health_status'))))
    
    def convert_batch(self, data_list: list) -> Graph:
        """
        Convert a batch of JSON-LD data to RDF
        
        Args:
            data_list: List of JSON-LD data dictionaries
            
        Returns:
            Combined RDF Graph
        """
        combined_graph = Graph()
        
        # Bind namespaces
        combined_graph.bind('sosa', SOSA)
        combined_graph.bind('ssn', SSN)
        combined_graph.bind('ex', EX)
        combined_graph.bind('agri', AGRI)
        combined_graph.bind('rdf', RDF)
        combined_graph.bind('rdfs', RDFS)
        combined_graph.bind('xsd', XSD)
        
        for data in data_list:
            graph = self.convert(data)
            combined_graph += graph
        
        return combined_graph
    
    def serialize(self, format: str = 'xml', destination: Optional[str] = None) -> Optional[str]:
        """
        Serialize RDF graph
        
        Args:
            format: Serialization format ('xml', 'turtle', 'json-ld', 'nt')
            destination: Optional file path to save to
            
        Returns:
            Serialized string if no destination provided
        """
        if self.graph is None:
            logger.warning("No graph to serialize")
            return None
        
        try:
            serialized = self.graph.serialize(format=format)
            
            if destination:
                with open(destination, 'w', encoding='utf-8') as f:
                    f.write(serialized)
                logger.info(f"RDF serialized to {destination}")
                return None
            
            return serialized
            
        except Exception as e:
            logger.error(f"Failed to serialize RDF: {e}")
            return None
    
    def get_graph(self) -> Graph:
        """Get the current RDF graph"""
        return self.graph
    
    def query(self, sparql_query: str) -> list:
        """
        Query the RDF graph using SPARQL
        
        Args:
            sparql_query: SPARQL query string
            
        Returns:
            Query results
        """
        if self.graph is None:
            logger.warning("No graph to query")
            return []
        
        try:
            results = self.graph.query(sparql_query)
            return list(results)
        except Exception as e:
            logger.error(f"SPARQL query failed: {e}")
            return []


def convert_to_rdf(data: Dict[str, Any]) -> Graph:
    """
    Convenience function to convert JSON-LD to RDF
    
    Args:
        data: JSON-LD data dictionary
        
    Returns:
        RDF Graph
    """
    converter = RDFConverter()
    return converter.convert(data)


def save_rdf_graph(graph: Graph, filepath: str, format: str = 'xml'):
    """
    Save RDF graph to file
    
    Args:
        graph: RDF Graph
        filepath: File path to save to
        format: Serialization format
    """
    try:
        graph.serialize(destination=filepath, format=format)
        logger.info(f"RDF graph saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to save RDF graph: {e}")
        return False