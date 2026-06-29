"""
Ontology Definitions for Smart Agriculture System
Defines namespaces and ontologies used for semantic integration
"""
from rdflib import Namespace, Graph

# Standard Ontologies
SOSA = Namespace("http://www.w3.org/ns/sosa/")  # Sensor, Observation, Sample, Actuator
SSN = Namespace("http://www.w3.org/ns/ssn/")    # Semantic Sensor Network
GEO = Namespace("http://www.opengis.net/ont/geosparql#")  # GeoSPARQL
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

# Custom Namespaces
EX = Namespace("http://example.org/agriculture/")  # Agriculture domain
AGRI = Namespace("http://example.org/agriculture/ontology#")  # Agriculture ontology

# Define sensor type mappings to SOSA/SSN classes
SENSOR_TYPE_MAPPING = {
    'temperature': SOSA.AirTemperature,
    'humidity': SOSA.RelativeHumidity,
    'soil_moisture': AGRI.SoilMoisture,
    'ph': AGRI.SoilPH,
    'rainfall': SOSA.Rainfall,
    'light': SOSA.SolarRadiation,
    'wind': SOSA.WindSpeed,
    'water_quality': AGRI.WaterQuality,
    'gps': AGRI.GPSLocation,
    'animal': AGRI.AnimalMonitoring
}

# Define property mappings
PROPERTY_MAPPING = {
    'temperature': SOSA.hasSimpleResult,
    'humidity': SOSA.hasSimpleResult,
    'soil_moisture': AGRI.hasMoistureLevel,
    'ph': AGRI.hasPHLevel,
    'rainfall': SOSA.hasSimpleResult,
    'light': SOSA.hasSimpleResult,
    'wind': SOSA.hasSimpleResult,
    'water_quality': AGRI.hasWaterQuality,
    'gps': GEO.hasGeometry,
    'animal': AGRI.hasHealthStatus
}

# Define unit mappings
UNIT_MAPPING = {
    'temperature': '°C',
    'humidity': '%',
    'soil_moisture': '%',
    'ph': 'pH',
    'rainfall': 'mm',
    'light': 'Lux',
    'wind': 'km/h',
    'water_quality': 'various',
    'gps': 'degrees',
    'animal': 'various'
}


def get_sensor_class(sensor_type: str):
    """
    Get SOSA/SSN class for a sensor type
    
    Args:
        sensor_type: Type of sensor
        
    Returns:
        RDF class URI
    """
    return SENSOR_TYPE_MAPPING.get(sensor_type, SOSA.Sensor)


def get_property_uri(sensor_type: str):
    """
    Get property URI for a sensor type
    
    Args:
        sensor_type: Type of sensor
        
    Returns:
        Property URI
    """
    return PROPERTY_MAPPING.get(sensor_type, SOSA.hasSimpleResult)


def create_namespace_graph():
    """Create a new RDF graph with standard namespaces"""
    g = Graph()
    
    # Bind namespaces
    g.bind('sosa', SOSA)
    g.bind('ssn', SSN)
    g.bind('geo', GEO)
    g.bind('ex', EX)
    g.bind('agri', AGRI)
    g.bind('rdf', RDF)
    g.bind('rdfs', RDFS)
    g.bind('xsd', XSD)
    
    return g


# Ontology definitions (Turtle format)
ONTOLOGY_TURTLE = """
@prefix sosa: <http://www.w3.org/ns/sosa/> .
@prefix ssn: <http://www.w3.org/ns/ssn/> .
@prefix geo: <http://www.opengis.net/ont/geosparql#> .
@prefix ex: <http://example.org/agriculture/> .
@prefix agri: <http://example.org/agriculture/ontology#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Agriculture Sensor Ontology
agri:AgricultureSensor rdf:type rdfs:Class ;
    rdfs:subClassOf sosa:Sensor ;
    rdfs:label "Agriculture Sensor"@en ;
    rdfs:comment "A sensor used in agricultural monitoring"@en .

agri:TemperatureSensor rdf:type rdfs:Class ;
    rdfs:subClassOf agri:AgricultureSensor ;
    rdfs:label "Temperature Sensor"@en .

agri:HumiditySensor rdf:type rdfs:Class ;
    rdfs:subClassOf agri:AgricultureSensor ;
    rdfs:label "Humidity Sensor"@en .

agri:SoilMoistureSensor rdf:type rdfs:Class ;
    rdfs:subClassOf agri:AgricultureSensor ;
    rdfs:label "Soil Moisture Sensor"@en .

agri:PHSensor rdf:type rdfs:Class ;
    rdfs:subClassOf agri:AgricultureSensor ;
    rdfs:label "pH Sensor"@en .

agri:RainfallSensor rdf:type rdfs:Class ;
    rdfs:subClassOf agri:AgricultureSensor ;
    rdfs:label "Rainfall Sensor"@en .

agri:LightSensor rdf:type rdfs:Class ;
    rdfs:subClassOf agri:AgricultureSensor ;
    rdfs:label "Light Sensor"@en .

agri:WindSensor rdf:type rdfs:Class ;
    rdfs:subClassOf agri:AgricultureSensor ;
    rdfs:label "Wind Sensor"@en .

agri:WaterQualitySensor rdf:type rdfs:Class ;
    rdfs:subClassOf agri:AgricultureSensor ;
    rdfs:label "Water Quality Sensor"@en .

agri:GPSSensor rdf:type rdfs:Class ;
    rdfs:subClassOf agri:AgricultureSensor ;
    rdfs:label "GPS Sensor"@en .

agri:AnimalSensor rdf:type rdfs:Class ;
    rdfs:subClassOf agri:AgricultureSensor ;
    rdfs:label "Animal Sensor"@en .

# Properties
agri:hasMoistureLevel rdf:type rdf:Property ;
    rdfs:subPropertyOf sosa:hasSimpleResult ;
    rdfs:label "has moisture level"@en .

agri:hasPHLevel rdf:type rdf:Property ;
    rdfs:subPropertyOf sosa:hasSimpleResult ;
    rdfs:label "has pH level"@en .

agri:hasWaterQuality rdf:type rdf:Property ;
    rdfs:subPropertyOf sosa:hasSimpleResult ;
    rdfs:label "has water quality"@en .

agri:hasHealthStatus rdf:type rdf:Property ;
    rdfs:subPropertyOf sosa:hasSimpleResult ;
    rdfs:label "has health status"@en .

agri:locatedInFarm rdf:type rdf:Property ;
    rdfs:label "located in farm"@en ;
    rdfs:domain agri:AgricultureSensor ;
    rdfs:range agri:Farm .

agri:Farm rdf:type rdfs:Class ;
    rdfs:label "Farm"@en ;
    rdfs:comment "An agricultural farm or field"@en .
"""


def load_ontology(graph: Graph = None) -> Graph:
    """
    Load ontology into a graph
    
    Args:
        graph: Optional existing graph to add ontology to
        
    Returns:
        Graph with ontology loaded
    """
    if graph is None:
        graph = create_namespace_graph()
    
    graph.parse(data=ONTOLOGY_TURTLE, format='turtle')
    return graph


def get_all_namespaces():
    """Get all defined namespaces"""
    return {
        'SOSA': SOSA,
        'SSN': SSN,
        'GEO': GEO,
        'EX': EX,
        'AGRI': AGRI,
        'RDF': RDF,
        'RDFS': RDFS,
        'XSD': XSD
    }