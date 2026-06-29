"""
Kafka Producer - Produces sensor data to Kafka topics
"""
import os
import json
import time
from typing import Dict, Any
from kafka import KafkaProducer
from dotenv import load_dotenv

from ingestion.utils import get_kafka_topic, enrich_data

load_dotenv()

# Configuration
KAFKA_HOST = os.getenv('KAFKA_HOST', 'localhost:9092')


class KafkaDataProducer:
    """Kafka Producer for sensor data"""
    
    def __init__(self):
        self.producer = None
        self.running = False
        
    def connect(self):
        """Connect to Kafka broker"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[KAFKA_HOST],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,   # Retry up to 3 times
                max_in_flight_requests_per_connection=1
            )
            print(f"✓ Connected to Kafka broker: {KAFKA_HOST}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Kafka: {e}")
            return False
    
    def send_sensor_data(self, sensor_type: str, data: Dict[str, Any]):
        """Send sensor data to appropriate Kafka topic"""
        try:
            if not self.producer:
                if not self.connect():
                    return False
            
            # Enrich data
            enriched_data = enrich_data(data)
            
            # Get Kafka topic
            topic = get_kafka_topic(sensor_type)
            
            # Send to Kafka
            future = self.producer.send(topic, enriched_data)
            
            # Wait for confirmation (optional, for critical data)
            # future.get(timeout=10)
            
            print(f"✓ Sent data to Kafka topic: {topic}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send data to Kafka: {e}")
            return False
    
    def send_batch(self, messages: list):
        """Send multiple messages in batch"""
        try:
            if not self.producer:
                if not self.connect():
                    return False
            
            for sensor_type, data in messages:
                enriched_data = enrich_data(data)
                topic = get_kafka_topic(sensor_type)
                self.producer.send(topic, enriched_data)
            
            # Flush to ensure all messages are sent
            self.producer.flush()
            print(f"✓ Sent {len(messages)} messages to Kafka")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send batch to Kafka: {e}")
            return False
    
    def close(self):
        """Close the producer"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            print("✓ Kafka producer closed")


def main():
    """Main function for testing"""
    producer = KafkaDataProducer()
    
    if not producer.connect():
        print("Failed to connect to Kafka")
        return
    
    # Test sending data
    test_data = {
        'sensor_type': 'temperature',
        'sensor_id': 'test_sensor_001',
        'temperature': 25.5,
        'unit': 'celsius',
        'timestamp': '2024-01-01T12:00:00'
    }
    
    print("\nSending test data...")
    producer.send_sensor_data('temperature', test_data)
    
    # Keep running
    print("\nKafka Producer is running...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        producer.close()


if __name__ == "__main__":
    main()