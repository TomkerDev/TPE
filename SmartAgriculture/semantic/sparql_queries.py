"""
SPARQL Queries for Semantic Data
Pre-defined queries for querying RDF data and Neo4j knowledge graph
"""
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class SPARQLQueries:
    """Collection of SPARQL queries for semantic data"""
    
    # Namespace prefixes
    PREFIXES = """
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    PREFIX ssn: <http://www.w3.org/ns/ssn/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX ex: <http://example.org/agriculture/>
    PREFIX agri: <http://example.org/agriculture/ontology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    """
    
    @staticmethod
    def get_all_sensors() -> str:
        """Get all sensors"""
        return f"""
        {SPARQLQueries.PREFIXES}
        
        SELECT ?sensor ?type ?label
        WHERE {{
            ?sensor rdf:type ?type .
            ?sensor rdfs:label ?label .
            FILTER(?type IN (sosa:Sensor, sosa:AirTemperature, sosa:RelativeHumidity, 
                            agri:SoilMoisture, agri:SoilPH, sosa:Rainfall, 
                            sosa:SolarRadiation, sosa:WindSpeed, agri:WaterQuality,
                            agri:GPSLocation, agri:AnimalMonitoring))
        }}
        ORDER BY ?label
        """
    
    @staticmethod
    def get_sensor_observations(sensor_id: str, limit: int = 100) -> str:
        """Get observations for a specific sensor"""
        return f"""
        {SPARQLQueries.PREFIXES}
        
        SELECT ?observation ?timestamp ?value
        WHERE {{
            ?sensor rdf:type ?type .
            ?sensor sosa:madeObservation ?observation .
            ?observation sosa:resultTime ?timestamp .
            ?observation sosa:hasSimpleResult ?value .
            FILTER(?sensor = ex:sensor/{sensor_id})
        }}
        ORDER BY DESC(?timestamp)
        LIMIT {limit}
        """
    
    @staticmethod
    def get_latest_observation(sensor_id: str) -> str:
        """Get the latest observation for a sensor"""
        return f"""
        {SPARQLQueries.PREFIXES}
        
        SELECT ?observation ?timestamp ?value
        WHERE {{
            ?sensor rdf:type ?type .
            ?sensor sosa:madeObservation ?observation .
            ?observation sosa:resultTime ?timestamp .
            ?observation sosa:hasSimpleResult ?value .
            FILTER(?sensor = ex:sensor/{sensor_id})
        }}
        ORDER BY DESC(?timestamp)
        LIMIT 1
        """
    
    @staticmethod
    def get_observations_by_type(sensor_type: str, limit: int = 100) -> str:
        """Get observations by sensor type"""
        return f"""
        {SPARQLQueries.PREFIXES}
        
        SELECT ?sensor ?observation ?timestamp ?value
        WHERE {{
            ?sensor rdf:type ?type .
            ?sensor sosa:madeObservation ?observation .
            ?observation sosa:resultTime ?timestamp .
            ?observation sosa:hasSimpleResult ?value .
            FILTER(?type = {sensor_type})
        }}
        ORDER BY DESC(?timestamp)
        LIMIT {limit}
        """
    
    @staticmethod
    def get_observations_in_timerange(start_time: str, end_time: str) -> str:
        """Get observations within a time range"""
        return f"""
        {SPARQLQueries.PREFIXES}
        
        SELECT ?sensor ?observation ?timestamp ?value
        WHERE {{
            ?sensor rdf:type ?type .
            ?sensor sosa:madeObservation ?observation .
            ?observation sosa:resultTime ?timestamp .
            ?observation sosa:hasSimpleResult ?value .
            FILTER(?timestamp >= "{start_time}"^^xsd:dateTime && 
                   ?timestamp <= "{end_time}"^^xsd:dateTime)
        }}
        ORDER BY ?timestamp
        """
    
    @staticmethod
    def get_sensor_statistics(sensor_id: str) -> str:
        """Get statistics for a sensor"""
        return f"""
        {SPARQLQueries.PREFIXES}
        
        SELECT ?sensor (COUNT(?observation) AS ?observation_count)
               (MIN(?timestamp) AS ?first_reading)
               (MAX(?timestamp) AS ?last_reading)
               (AVG(?value) AS ?avg_value)
               (MIN(?value) AS ?min_value)
               (MAX(?value) AS ?max_value)
        WHERE {{
            ?sensor rdf:type ?type .
            ?sensor sosa:madeObservation ?observation .
            ?observation sosa:resultTime ?timestamp .
            ?observation sosa:hasSimpleResult ?value .
            FILTER(?sensor = ex:sensor/{sensor_id})
        }}
        GROUP BY ?sensor
        """
    
    @staticmethod
    def get_all_sensor_types() -> str:
        """Get all distinct sensor types"""
        return f"""
        {SPARQLQueries.PREFIXES}
        
        SELECT DISTINCT ?type (COUNT(?sensor) AS ?sensor_count)
        WHERE {{
            ?sensor rdf:type ?type .
        }}
        GROUP BY ?type
        ORDER BY DESC(?sensor_count)
        """
    
    @staticmethod
    def get_observations_with_property(property_uri: str, limit: int = 100) -> str:
        """Get observations with a specific property"""
        return f"""
        {SPARQLQueries.PREFIXES}
        
        SELECT ?sensor ?observation ?timestamp ?value
        WHERE {{
            ?sensor rdf:type ?type .
            ?sensor sosa:madeObservation ?observation .
            ?observation {property_uri} ?value .
            OPTIONAL {{ ?observation sosa:resultTime ?timestamp }}
        }}
        ORDER BY DESC(?timestamp)
        LIMIT {limit}
        """
    
    @staticmethod
    def get_sensors_by_location(latitude: float, longitude: float, radius: float = 0.01) -> str:
        """Get sensors near a location (simplified)"""
        return f"""
        {SPARQLQueries.PREFIXES}
        
        SELECT ?sensor ?lat ?long
        WHERE {{
            ?sensor rdf:type ?type .
            ?sensor geo:hasGeometry ?geom .
            ?geom geo:asWKT ?wkt .
            BIND(STRAFTER(?wkt, "POINT(") AS ?coords)
            BIND(STRAFTER(?coords, " ") AS ?lat_str)
            BIND(STRAFTER(?coords, ?lat_str) AS ?long_str)
            BIND(xsd:float(?lat_str) AS ?lat)
            BIND(xsd:float(?long_str) AS ?long)
            FILTER(?lat >= {latitude - radius} && ?lat <= {latitude + radius})
            FILTER(?long >= {longitude - radius} && ?long <= {longitude + radius})
        }}
        """
    
    @staticmethod
    def get_animal_health_status(animal_id: str) -> str:
        """Get health status for an animal"""
        return f"""
        {SPARQLQueries.PREFIXES}
        
        SELECT ?sensor ?observation ?timestamp ?activity ?temp ?heartRate ?status
        WHERE {{
            ?sensor rdf:type agri:AnimalSensor .
            ?sensor sosa:madeObservation ?observation .
            ?observation sosa:resultTime ?timestamp .
            ?observation agri:hasActivityLevel ?activity .
            ?observation agri:hasBodyTemperature ?temp .
            ?observation agri:hasHeartRate ?heartRate .
            ?observation agri:hasHealthStatus ?status .
            ?sensor agri:monitors ?animal .
            FILTER(?animal = ex:animal/{animal_id})
        }}
        ORDER BY DESC(?timestamp)
        LIMIT 10
        """
    
    @staticmethod
    def get_farm_summary() -> str:
        """Get summary of all farm sensors"""
        return f"""
        {SPARQLQueries.PREFIXES}
        
        SELECT ?type (COUNT(?sensor) AS ?count)
               (MIN(?timestamp) AS ?oldest)
               (MAX(?timestamp) AS ?newest)
        WHERE {{
            ?sensor rdf:type ?type .
            ?sensor sosa:madeObservation ?observation .
            ?observation sosa:resultTime ?timestamp .
        }}
        GROUP BY ?type
        ORDER BY DESC(?count)
        """
    
    @staticmethod
    def get_anomalies() -> str:
        """Get anomalous readings (example: temperature > 40 or < 0)"""
        return f"""
        {SPARQLQueries.PREFIXES}
        
        SELECT ?sensor ?observation ?timestamp ?value
        WHERE {{
            ?sensor rdf:type sosa:AirTemperature .
            ?sensor sosa:madeObservation ?observation .
            ?observation sosa:resultTime ?timestamp .
            ?observation sosa:hasSimpleResult ?value .
            FILTER(?value > 40 || ?value < 0)
        }}
        ORDER BY DESC(?timestamp)
        """
    
    @staticmethod
    def get_correlated_observations(sensor_id_1: str, sensor_id_2: str, 
                                    time_window_minutes: int = 5) -> str:
        """Get correlated observations from two sensors within a time window"""
        return f"""
        {SPARQLQueries.PREFIXES}
        
        SELECT ?obs1 ?timestamp1 ?value1 ?obs2 ?value2
        WHERE {{
            ?sensor1 rdf:type ?type1 .
            ?sensor1 sosa:madeObservation ?obs1 .
            ?obs1 sosa:resultTime ?timestamp1 .
            ?obs1 sosa:hasSimpleResult ?value1 .
            
            ?sensor2 rdf:type ?type2 .
            ?sensor2 sosa:madeObservation ?obs2 .
            ?obs2 sosa:resultTime ?timestamp2 .
            ?obs2 sosa:hasSimpleResult ?value2 .
            
            FILTER(?sensor1 = ex:sensor/{sensor_id_1})
            FILTER(?sensor2 = ex:sensor/{sensor_id_2})
            FILTER(?timestamp1 = ?timestamp2)
        }}
        LIMIT 100
        """


class QueryExecutor:
    """Executes SPARQL queries on RDF graphs"""
    
    def __init__(self, graph):
        """
        Initialize query executor
        
        Args:
            graph: RDFLib Graph object
        """
        self.graph = graph
        
    def execute(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a SPARQL query
        
        Args:
            query: SPARQL query string
            
        Returns:
            List of result dictionaries
        """
        try:
            results = self.graph.query(query)
            
            # Convert results to list of dictionaries
            result_list = []
            for row in results:
                result_dict = {}
                for var in results.vars:
                    result_dict[str(var)] = str(row[var])
                result_list.append(result_dict)
            
            return result_list
            
        except Exception as e:
            logger.error(f"SPARQL query execution failed: {e}")
            return []
    
    def execute_and_print(self, query: str):
        """Execute query and print results"""
        results = self.execute(query)
        
        if not results:
            print("No results found")
            return
        
        # Print header
        headers = list(results[0].keys())
        print(" | ".join(headers))
        print("-" * 100)
        
        # Print rows
        for row in results:
            print(" | ".join(str(row.get(h, '')) for h in headers))


# Convenience functions for common queries
def get_all_sensors_query() -> str:
    """Get query for all sensors"""
    return SPARQLQueries.get_all_sensors()


def get_sensor_observations_query(sensor_id: str, limit: int = 100) -> str:
    """Get query for sensor observations"""
    return SPARQLQueries.get_sensor_observations(sensor_id, limit)


def get_latest_observation_query(sensor_id: str) -> str:
    """Get query for latest observation"""
    return SPARQLQueries.get_latest_observation(sensor_id)


def get_sensor_statistics_query(sensor_id: str) -> str:
    """Get query for sensor statistics"""
    return SPARQLQueries.get_sensor_statistics(sensor_id)


def get_farm_summary_query() -> str:
    """Get query for farm summary"""
    return SPARQLQueries.get_farm_summary()


def get_anomalies_query() -> str:
    """Get query for anomalies"""
    return SPARQLQueries.get_anomalies()