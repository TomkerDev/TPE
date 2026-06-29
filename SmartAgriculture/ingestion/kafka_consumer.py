"""
Kafka Consumer - Consumes sensor data from Kafka and processes it
"""
import os
import json
import time
import signal
import sys
from typing import Dict, Any
from kafka import KafkaConsumer
from dotenv import load_dotenv

from ingestion.utils import validate_sensor_data, enrich_data

load_dotenv()

# Configuration
KAFKA_HOST = os.getenv('KAFKA_HOST', 'localhost:9092')

# Kafka topics to consume
KAFKA_TOPICS = [
    'agriculture.temperature',
    'agriculture.humidity',
    'agriculture.soil_moisture',
    'agriculture.ph',
    'agriculture.rainfall',
    'agriculture.light',
    'agriculture.wind',
    'agriculture.water_quality',
    'agriculture.gps',
    'agriculture.animal'
]

# Global flag for graceful shutdown
running = True


def signal_handler(signum, frame):
    """Handle interrupt signals"""
    global running
    print("\n\n⚠ Signal received, shutting down Kafka consumer...")
    running = False
    sys.exit(0)


class KafkaDataConsumer:
    """Kafka Consumer for sensor data"""
    
    def __init__(self, topics=None):
        self.topics = topics or KAFKA_TOPICS
        self.consumer = None
        self.running = False
        self.message_count = 0
        
    def connect(self):
        """Connect to Kafka broker"""
        try:
            self.consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=[KAFKA_HOST],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='agriculture_etl_group',
                auto_offset_reset='latest',  # Start from latest messages
                enable_auto_commit=True,
                auto_commit_interval_ms=1000
            )
            print(f"✓ Connected to Kafka broker: {KAFKA_HOST}")
            print(f"  Subscribed to {len(self.topics)} topics")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Kafka: {e}")
            return False
    
    def process_message(self, data: Dict[str, Any], topic: str):
        """Process consumed message"""
        try:
            # Validate data
            if not validate_sensor_data(data):
                print(f"  ⚠ Invalid data from {topic}, skipping...")
                return None
            
            # Enrich data
            enriched_data = enrich_data(data)
            
            self.message_count += 1
            print(f"\n📨 [{self.message_count}] Processed message from {topic}")
            print(f"  Sensor: {data.get('sensor_id')}")
            print(f"  Type: {data.get('sensor_type')}")
            
            return enriched_data
            
        except Exception as e:
            print(f"  ✗ Error processing message: {e}")
            return None
    
    def run(self, callback=None):
        """Run the consumer"""
        global running
        
        if not self.connect():
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("Kafka Consumer is running...")
        print("Press Ctrl+C to stop")
        print("=" * 60 + "\n")
        
        self.running = True
        
        try:
            for message in self.consumer:
                if not running:
                    break
                
                topic = message.topic
                data = message.value
                
                # Process message
                processed_data = self.process_message(data, topic)
                
                # Call callback if provided (e.g., for ETL processing)
                if callback and processed_data:
                    callback(processed_data, topic)
                
        except KeyboardInterrupt:
            print("\n\n⚠ Interrupt received")
        except Exception as e:
            print(f"\n✗ Consumer error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the consumer"""
        print("\nStopping Kafka Consumer...")
        self.running = False
        if self.consumer:
            self.consumer.close()
        print(f"✓ Kafka Consumer stopped. Total messages processed: {self.message_count}")


def main():
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run consumer
    consumer = KafkaDataConsumer()
    
    # Example callback function
    def etl_callback(data, topic):
        """Callback to process data (e.g., send to ETL pipeline)"""
        print(f"  → Processing for ETL: {data.get('sensor_type')}")
    
    consumer.run(callback=etl_callback)


if __name__ == "__main__":
    main()