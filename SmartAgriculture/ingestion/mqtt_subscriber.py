"""
MQTT Subscriber - Receives data from sensors and forwards to Kafka
"""
import os
import json
import time
import signal
import sys
from typing import Dict, Any
import paho.mqtt.client as mqtt
from kafka import KafkaProducer
from dotenv import load_dotenv

from ingestion.utils import validate_sensor_data, enrich_data, get_kafka_topic

load_dotenv()

# Configuration
MQTT_HOST = os.getenv('MQTT_HOST', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
KAFKA_HOST = os.getenv('KAFKA_HOST', 'localhost:9092')

# MQTT Topics to subscribe
MQTT_TOPICS = [
    'agriculture/sensors/#',  # Subscribe to all sensor topics
]

# Global flag for graceful shutdown
running = True


def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the server"""
    if rc == 0:
        print(f"✓ Connected to MQTT Broker: {MQTT_HOST}:{MQTT_PORT}")
        
        # Subscribe to all topics
        for topic in MQTT_TOPICS:
            client.subscribe(topic)
            print(f"  Subscribed to: {topic}")
    else:
        print(f"✗ MQTT connection failed with code: {rc}")


def on_disconnect(client, userdata, rc):
    """Callback for when the client disconnects from the server"""
    if rc != 0:
        print(f"MQTT disconnected unexpectedly, attempting to reconnect...")
        time.sleep(5)
        try:
            client.reconnect()
        except Exception as e:
            print(f"Reconnection failed: {e}")


def on_message(client, userdata, msg):
    """Callback for when a PUBLISH message is received from the server"""
    try:
        # Decode message
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        print(f"\n📨 Received MQTT message on topic: {topic}")
        
        # Parse JSON data
        data = json.loads(payload)
        
        # Validate data
        if not validate_sensor_data(data):
            print(f"  ⚠ Invalid data received, skipping...")
            return
        
        # Enrich data
        enriched_data = enrich_data(data)
        
        # Get Kafka topic based on sensor type
        sensor_type = data.get('sensor_type', 'unknown')
        kafka_topic = get_kafka_topic(sensor_type)
        
        # Forward to Kafka
        kafka_producer = userdata.get('kafka_producer')
        if kafka_producer:
            kafka_producer.send(kafka_topic, enriched_data)
            kafka_producer.flush()
            print(f"  ✓ Forwarded to Kafka topic: {kafka_topic}")
        else:
            print(f"  ⚠ Kafka producer not available")
            
    except json.JSONDecodeError as e:
        print(f"  ✗ Failed to parse JSON: {e}")
    except Exception as e:
        print(f"  ✗ Error processing message: {e}")


def signal_handler(signum, frame):
    """Handle interrupt signals"""
    global running
    print("\n\n⚠ Signal received, shutting down MQTT subscriber...")
    running = False
    sys.exit(0)


class MQTTSubscriber:
    """MQTT Subscriber class"""
    
    def __init__(self):
        self.client = mqtt.Client(client_id="mqtt_subscriber", userdata={})
        self.kafka_producer = None
        
        # Set callbacks
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_message = on_message
        
    def init_kafka_producer(self):
        """Initialize Kafka producer"""
        try:
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=[KAFKA_HOST],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            # Store in userdata for access in callbacks
            self.client.user_data_set({'kafka_producer': self.kafka_producer})
            print(f"✓ Kafka producer initialized: {KAFKA_HOST}")
        except Exception as e:
            print(f"✗ Failed to initialize Kafka producer: {e}")
            sys.exit(1)
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(MQTT_HOST, MQTT_PORT, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"✗ Failed to connect to MQTT broker: {e}")
            return False
    
    def run(self):
        """Run the subscriber"""
        global running
        
        # Initialize Kafka producer
        self.init_kafka_producer()
        
        # Connect to MQTT
        if not self.connect():
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("MQTT Subscriber is running...")
        print("Press Ctrl+C to stop")
        print("=" * 60 + "\n")
        
        # Keep running
        try:
            while running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⚠ Interrupt received")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the subscriber"""
        print("\nStopping MQTT Subscriber...")
        self.client.loop_stop()
        self.client.disconnect()
        if self.kafka_producer:
            self.kafka_producer.close()
        print("✓ MQTT Subscriber stopped")


def main():
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run subscriber
    subscriber = MQTTSubscriber()
    subscriber.run()


if __name__ == "__main__":
    main()