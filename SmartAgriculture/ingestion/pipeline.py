#!/usr/bin/env python3
"""
Complete Pipeline Orchestrator for Smart Agriculture System
Orchestrates the entire data flow from sensors to databases
"""
import os
import sys
import time
import signal
import logging
import subprocess
from typing import List
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

from ingestion.mqtt_subscriber import MQTTSubscriber
from ingestion.kafka_consumer import KafkaDataConsumer
from ingestion.etl import ETLPipeline
from ingestion.postgres_loader import PostgresLoader
from ingestion.timescaledb_loader import TimescaleDBLoader
from ingestion.mongodb_loader import MongoDBLoader
from ingestion.neo4j_loader import Neo4jLoader

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Main orchestrator for the complete data pipeline"""
    
    def __init__(self):
        self.running = False
        self.components = {}
        self.loaders = []
        self.etl = None
        
    def initialize_databases(self):
        """Initialize all database connections"""
        logger.info("=" * 60)
        logger.info("Initializing Database Connections...")
        logger.info("=" * 60)
        
        # PostgreSQL
        logger.info("\n1. Connecting to PostgreSQL...")
        postgres_loader = PostgresLoader()
        if postgres_loader.connect():
            logger.info("✓ PostgreSQL connected")
            self.loaders.append(postgres_loader)
        else:
            logger.error("✗ PostgreSQL connection failed")
            return False
        
        # TimescaleDB
        logger.info("\n2. Connecting to TimescaleDB...")
        timescale_loader = TimescaleDBLoader()
        if timescale_loader.connect():
            logger.info("✓ TimescaleDB connected")
            self.loaders.append(timescale_loader)
        else:
            logger.error("✗ TimescaleDB connection failed")
            return False
        
        # MongoDB
        logger.info("\n3. Connecting to MongoDB...")
        mongo_loader = MongoDBLoader()
        if mongo_loader.connect():
            logger.info("✓ MongoDB connected")
            self.loaders.append(mongo_loader)
        else:
            logger.error("✗ MongoDB connection failed")
            return False
        
        # Neo4j
        logger.info("\n4. Connecting to Neo4j...")
        neo4j_loader = Neo4jLoader()
        if neo4j_loader.connect():
            logger.info("✓ Neo4j connected")
            self.loaders.append(neo4j_loader)
        else:
            logger.error("✗ Neo4j connection failed")
            return False
        
        logger.info(f"\n✓ All {len(self.loaders)} databases connected successfully")
        return True
    
    def initialize_etl(self):
        """Initialize ETL pipeline"""
        logger.info("\n" + "=" * 60)
        logger.info("Initializing ETL Pipeline...")
        logger.info("=" * 60)
        
        self.etl = ETLPipeline()
        logger.info("✓ ETL Pipeline initialized")
        return True
    
    def start_mqtt_subscriber(self):
        """Start MQTT subscriber in background thread"""
        logger.info("\n" + "=" * 60)
        logger.info("Starting MQTT Subscriber...")
        logger.info("=" * 60)
        
        def run_subscriber():
            subscriber = MQTTSubscriber()
            subscriber.run()
        
        # Run in background thread
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(run_subscriber)
        self.components['mqtt_subscriber'] = (executor, future)
        
        # Give it time to connect
        time.sleep(3)
        logger.info("✓ MQTT Subscriber started in background")
        return True
    
    def start_kafka_consumer(self):
        """Start Kafka consumer with ETL processing"""
        logger.info("\n" + "=" * 60)
        logger.info("Starting Kafka Consumer with ETL...")
        logger.info("=" * 60)
        
        def run_consumer():
            consumer = KafkaDataConsumer()
            
            # Define ETL callback
            def process_with_etl(data, topic):
                if self.etl and self.loaders:
                    self.etl.process(data, self.loaders)
            
            consumer.run(callback=process_with_etl)
        
        # Run in background thread
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(run_consumer)
        self.components['kafka_consumer'] = (executor, future)
        
        logger.info("✓ Kafka Consumer started in background")
        return True
    
    def start_sensors(self):
        """Start sensor simulation"""
        logger.info("\n" + "=" * 60)
        logger.info("Starting Sensor Simulation...")
        logger.info("=" * 60)
        
        try:
            # Import and run sensors
            from sensors.run_all_sensors import SensorManager
            
            manager = SensorManager()
            manager.create_sensors()
            
            # Run in parallel mode in background
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(manager.run_all_parallel, interval=5)
            self.components['sensors'] = (executor, future)
            
            logger.info("✓ Sensors started in background")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to start sensors: {e}")
            return False
    
    def run(self):
        """Run the complete pipeline"""
        self.running = True
        
        try:
            # Step 1: Initialize databases
            if not self.initialize_databases():
                logger.error("Failed to initialize databases. Exiting...")
                return False
            
            # Step 2: Initialize ETL
            if not self.initialize_etl():
                logger.error("Failed to initialize ETL. Exiting...")
                return False
            
            # Step 3: Start MQTT subscriber
            if not self.start_mqtt_subscriber():
                logger.error("Failed to start MQTT subscriber. Exiting...")
                return False
            
            # Step 4: Start Kafka consumer
            if not self.start_kafka_consumer():
                logger.error("Failed to start Kafka consumer. Exiting...")
                return False
            
            # Step 5: Start sensors
            if not self.start_sensors():
                logger.error("Failed to start sensors. Exiting...")
                return False
            
            # Pipeline is now running
            logger.info("\n" + "=" * 60)
            logger.info("✓ COMPLETE PIPELINE IS RUNNING")
            logger.info("=" * 60)
            logger.info("\nData flow:")
            logger.info("  Sensors → MQTT → Kafka → ETL → Databases")
            logger.info("\nPress Ctrl+C to stop\n")
            
            # Keep main thread alive
            try:
                while self.running:
                    time.sleep(1)
                    
                    # Print stats every 30 seconds
                    if int(time.time()) % 30 == 0:
                        self.print_stats()
                        
            except KeyboardInterrupt:
                logger.info("\n\n⚠ Shutdown signal received...")
                self.stop()
                
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            self.stop()
            return False
        
        return True
    
    def print_stats(self):
        """Print pipeline statistics"""
        try:
            logger.info("\n" + "-" * 60)
            logger.info("Pipeline Statistics:")
            logger.info("-" * 60)
            
            # ETL stats
            if self.etl:
                stats = self.etl.get_stats()
                logger.info(f"ETL: {stats['total_processed']} processed "
                          f"({stats['successful']} successful, {stats['failed']} failed)")
            
            # Database stats
            for loader in self.loaders:
                db_stats = loader.get_stats()
                if db_stats:
                    logger.info(f"{loader.__class__.__name__}: {db_stats}")
            
            logger.info("-" * 60)
            
        except Exception as e:
            logger.error(f"Error printing stats: {e}")
    
    def stop(self):
        """Stop all pipeline components"""
        logger.info("\n" + "=" * 60)
        logger.info("Stopping Pipeline...")
        logger.info("=" * 60)
        
        self.running = False
        
        # Stop all components
        for name, (executor, future) in self.components.items():
            try:
                logger.info(f"Stopping {name}...")
                executor.shutdown(wait=False)
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
        
        # Close database connections
        for loader in self.loaders:
            try:
                loader.close()
            except Exception as e:
                logger.error(f"Error closing {loader.__class__.__name__}: {e}")
        
        logger.info("\n✓ Pipeline stopped")


def signal_handler(signum, frame):
    """Handle interrupt signals"""
    logger.info("\n\n⚠ Signal received, initiating shutdown...")
    sys.exit(0)


def check_services():
    """Check if required services are running"""
    logger.info("Checking required services...")
    
    services = {
        'MQTT': (os.getenv('MQTT_HOST', 'localhost'), int(os.getenv('MQTT_PORT', 1883))),
        'Kafka': (os.getenv('KAFKA_HOST', 'localhost:9092').split(':')[0], 
                  int(os.getenv('KAFKA_HOST', 'localhost:9092').split(':')[1]) if ':' in os.getenv('KAFKA_HOST', 'localhost:9092') else 9092),
        'PostgreSQL': (os.getenv('POSTGRES_HOST', 'localhost'), int(os.getenv('POSTGRES_PORT', 5432))),
        'TimescaleDB': (os.getenv('TIMESCALE_HOST', 'localhost'), int(os.getenv('TIMESCALE_PORT', 5433))),
        'MongoDB': (os.getenv('MONGO_HOST', 'localhost'), int(os.getenv('MONGO_PORT', 27017))),
        'Neo4j': (os.getenv('NEO4J_URI', 'bolt://localhost:7687').replace('bolt://', '').split(':')[0],
                  int(os.getenv('NEO4J_URI', 'bolt://localhost:7687').replace('bolt://', '').split(':')[1]) if ':' in os.getenv('NEO4J_URI', 'bolt://localhost:7687') else 7687)
    }
    
    logger.info("\nService endpoints:")
    for service, (host, port) in services.items():
        logger.info(f"  {service}: {host}:{port}")
    
    logger.info("\n⚠ Make sure all services are running before starting the pipeline!")
    logger.info("  Use Docker Compose: docker-compose up -d")
    logger.info("  Or start services individually\n")


def main():
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=" * 60)
    logger.info("Smart Agriculture - Complete Pipeline")
    logger.info("=" * 60)
    
    # Check services
    check_services()
    
    # Ask for confirmation
    try:
        response = input("\nStart the pipeline? (y/n): ").strip().lower()
        if response != 'y':
            logger.info("Pipeline start cancelled")
            return
    except KeyboardInterrupt:
        logger.info("\n\nPipeline start cancelled")
        return
    
    # Create and run orchestrator
    orchestrator = PipelineOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()