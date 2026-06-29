#!/usr/bin/env python3
"""
Semantic Pipeline
Orchestrates the complete semantic processing workflow:
JSON → JSON-LD → RDF → SOSA/SSN Mapping → Neo4j Knowledge Graph
"""
import os
import sys
import time
import signal
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
from dotenv import load_dotenv

from semantic.jsonld_converter import JSONLDConverter, convert_to_jsonld
from semantic.rdf_converter import RDFConverter, convert_to_rdf, save_rdf_graph
from semantic.sosa_mapper import SOSAMapper, map_to_semantic, semantic_label
from semantic.neo4j_graph import Neo4jGraphManager, insert_semantic_data
from semantic.sparql_queries import SPARQLQueries, QueryExecutor

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SemanticPipeline:
    """
    Complete semantic processing pipeline
    Converts sensor data through semantic web formats to knowledge graph
    """
    
    def __init__(self, neo4j_uri: str = None, neo4j_user: str = None, 
                 neo4j_password: str = None, save_rdf: bool = False):
        """
        Initialize semantic pipeline
        
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            save_rdf: Whether to save RDF graphs to files
        """
        # Get Neo4j config from environment if not provided
        self.neo4j_uri = neo4j_uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.neo4j_user = neo4j_user or os.getenv('NEO4J_USER', 'neo4j')
        self.neo4j_password = neo4j_password or os.getenv('NEO4J_PASSWORD', 'password')
        self.save_rdf = save_rdf
        
        # Initialize components
        self.jsonld_converter = JSONLDConverter()
        self.rdf_converter = RDFConverter()
        self.sosa_mapper = SOSAMapper()
        self.neo4j_manager = Neo4jGraphManager(self.neo4j_uri, self.neo4j_user, self.neo4j_password)
        
        # Statistics
        self.pipeline_stats = {
            'total_processed': 0,
            'jsonld_converted': 0,
            'rdf_converted': 0,
            'neo4j_inserted': 0,
            'failed': 0,
            'by_sensor_type': {}
        }
        
    def process(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Graph, bool]:
        """
        Process data through complete semantic pipeline
        
        Args:
            data: Raw sensor data dictionary
            
        Returns:
            Tuple of (jsonld_data, rdf_graph, success)
        """
        self.pipeline_stats['total_processed'] += 1
        
        if not data:
            return None, None, False
        
        sensor_type = data.get('sensor_type', 'unknown')
        
        try:
            # Step 1: Map to semantic format (SOSA/SSN)
            logger.debug(f"Step 1: Mapping {sensor_type} to semantic format...")
            mapped_data = self.sosa_mapper.map_sensor_data(data)
            
            # Step 2: Convert to JSON-LD
            logger.debug(f"Step 2: Converting {sensor_type} to JSON-LD...")
            jsonld_data = self.jsonld_converter.convert(mapped_data)
            self.pipeline_stats['jsonld_converted'] += 1
            
            # Step 3: Convert to RDF
            logger.debug(f"Step 3: Converting {sensor_type} to RDF...")
            rdf_graph = self.rdf_converter.convert(jsonld_data)
            self.pipeline_stats['rdf_converted'] += 1
            
            # Step 4: Insert into Neo4j
            logger.debug(f"Step 4: Inserting {sensor_type} into Neo4j...")
            success = self.neo4j_manager.insert_semantic_data(mapped_data)
            
            if success:
                self.pipeline_stats['neo4j_inserted'] += 1
            else:
                self.pipeline_stats['failed'] += 1
                return jsonld_data, rdf_graph, False
            
            # Update sensor type stats
            if sensor_type not in self.pipeline_stats['by_sensor_type']:
                self.pipeline_stats['by_sensor_type'][sensor_type] = 0
            self.pipeline_stats['by_sensor_type'][sensor_type] += 1
            
            # Save RDF if enabled
            if self.save_rdf:
                self._save_rdf(rdf_graph, data.get('sensor_id'), data.get('timestamp'))
            
            logger.info(f"✓ Successfully processed {sensor_type} semantically")
            return jsonld_data, rdf_graph, True
            
        except Exception as e:
            logger.error(f"Semantic pipeline error for {sensor_type}: {e}", exc_info=True)
            self.pipeline_stats['failed'] += 1
            return None, None, False
    
    def process_batch(self, data_list: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Graph], List[Dict]]:
        """
        Process a batch of data through the pipeline
        
        Args:
            data_list: List of sensor data dictionaries
            
        Returns:
            Tuple of (jsonld_list, rdf_graphs, failed_data)
        """
        jsonld_list = []
        rdf_graphs = []
        failed_data = []
        
        for data in data_list:
            jsonld_data, rdf_graph, success = self.process(data)
            
            if success:
                jsonld_list.append(jsonld_data)
                rdf_graphs.append(rdf_graph)
            else:
                failed_data.append(data)
        
        return jsonld_list, rdf_graphs, failed_data
    
    def _save_rdf(self, graph, sensor_id: str, timestamp):
        """Save RDF graph to file"""
        try:
            if not sensor_id or not timestamp:
                return
            
            # Create filename
            ts_str = str(timestamp).replace(':', '-').replace('.', '-') if isinstance(timestamp, str) else timestamp.isoformat()
            filename = f"rdf_data/{sensor_id}_{ts_str}.rdf"
            
            # Ensure directory exists
            os.makedirs('rdf_data', exist_ok=True)
            
            # Save graph
            graph.serialize(destination=filename, format='xml')
            logger.debug(f"Saved RDF to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save RDF: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        stats = self.pipeline_stats.copy()
        
        # Calculate success rate
        if stats['total_processed'] > 0:
            stats['success_rate'] = (stats['neo4j_inserted'] / stats['total_processed']) * 100
        else:
            stats['success_rate'] = 0
        
        # Add Neo4j statistics
        stats['neo4j_stats'] = self.neo4j_manager.get_statistics()
        
        return stats
    
    def reset_stats(self):
        """Reset statistics"""
        self.pipeline_stats = {
            'total_processed': 0,
            'jsonld_converted': 0,
            'rdf_converted': 0,
            'neo4j_inserted': 0,
            'failed': 0,
            'by_sensor_type': {}
        }
        self.sosa_mapper.reset_stats()
    
    def print_report(self):
        """Print semantic pipeline report"""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print("RAPPORT DU PIPELINE SÉMANTIQUE")
        print("=" * 60)
        
        print(f"\nTotal traité: {stats['total_processed']}")
        print(f"JSON-LD converti: {stats['jsonld_converted']}")
        print(f"RDF converti: {stats['rdf_converted']}")
        print(f"Inséré dans Neo4j: {stats['neo4j_inserted']}")
        print(f"Échecs: {stats['failed']}")
        print(f"Taux de réussite: {stats['success_rate']:.2f}%")
        
        print(f"\n--- Par type de capteur ---")
        for sensor_type, count in stats['by_sensor_type'].items():
            print(f"  {sensor_type}: {count}")
        
        print(f"\n--- Statistiques Neo4j ---")
        neo4j_stats = stats.get('neo4j_stats', {})
        print(f"  Capteurs: {neo4j_stats.get('sensors', 0)}")
        print(f"  Observations: {neo4j_stats.get('observations', 0)}")
        print(f"  Propriétés: {neo4j_stats.get('properties', 0)}")
        print(f"  Relations: {neo4j_stats.get('relationships', 0)}")
        
        print("=" * 60 + "\n")
    
    def connect_neo4j(self) -> bool:
        """Connect to Neo4j database"""
        return self.neo4j_manager.connect()
    
    def close(self):
        """Close all connections"""
        self.neo4j_manager.close()


def main():
    """Main function for testing"""
    
    print("=" * 60)
    print("TEST DU PIPELINE SÉMANTIQUE")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = SemanticPipeline(save_rdf=False)
    
    # Connect to Neo4j
    if not pipeline.connect_neo4j():
        print("Failed to connect to Neo4j. Exiting...")
        return
    
    # Test data samples
    test_data_samples = [
        {
            'sensor_id': 'temp_sensor_001',
            'sensor_type': 'temperature',
            'temperature': 25.5,
            'unit': 'celsius',
            'timestamp': '2024-01-01T12:00:00'
        },
        {
            'sensor_id': 'humidity_sensor_001',
            'sensor_type': 'humidity',
            'humidity': 65.0,
            'unit': 'percent',
            'timestamp': '2024-01-01T12:01:00'
        },
        {
            'sensor_id': 'ph_sensor_001',
            'sensor_type': 'ph',
            'ph': 6.5,
            'unit': 'pH',
            'timestamp': '2024-01-01T12:02:00'
        },
        {
            'sensor_id': 'gps_sensor_001',
            'sensor_type': 'gps',
            'latitude': 36.7538,
            'longitude': 10.2922,
            'altitude': 100.0,
            'speed': 0.0,
            'timestamp': '2024-01-01T12:03:00'
        }
    ]
    
    print("\nTraitement des données de test...\n")
    
    # Process each sample
    for i, data in enumerate(test_data_samples, 1):
        print(f"\n--- Test {i}: {data.get('sensor_type')} ---")
        
        jsonld_data, rdf_graph, success = pipeline.process(data)
        
        if success:
            print(f"✓ Traitement réussi")
            print(f"  JSON-LD @id: {jsonld_data.get('@id', 'N/A')}")
            print(f"  JSON-LD @type: {jsonld_data.get('@type', 'N/A')}")
            print(f"  RDF triples: {len(rdf_graph)}")
        else:
            print(f"✗ Traitement échoué")
    
    # Print final report
    pipeline.print_report()
    
    # Close connections
    pipeline.close()


if __name__ == "__main__":
    main()