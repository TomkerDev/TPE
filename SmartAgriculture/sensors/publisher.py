import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from kafka import KafkaProducer
from sensors.config import SensorConfig

class SensorPublisher:
    """Publisher class for sending sensor data to MQTT and Kafka"""
    
    def __init__(self, sensor_type):
        self.sensor_type = sensor_type
        self.config = SensorConfig()
        
        # Initialize MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
        
        # Initialize Kafka producer
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=[self.config.KAFKA_HOST],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Connect to MQTT broker
        self._connect_mqtt()
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection"""
        if rc == 0:
            print(f"✓ MQTT connected for {self.sensor_type} sensor")
        else:
            print(f"✗ MQTT connection failed for {self.sensor_type} sensor with code {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """Callback for MQTT disconnection"""
        if rc != 0:
            print(f"MQTT disconnected for {self.sensor_type} sensor, attempting to reconnect...")
    
    def _connect_mqtt(self):
        """Connect to MQTT broker"""
        try:
            self.mqtt_client.connect(self.config.MQTT_HOST, self.config.MQTT_PORT, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            print(f"Failed to connect MQTT for {self.sensor_type}: {e}")
    
    def publish(self, data):
        """Publish data to both MQTT and Kafka"""
        try:
            # Add timestamp
            data['timestamp'] = datetime.utcnow().isoformat()
            data['sensor_type'] = self.sensor_type
            
            # Publish to MQTT
            mqtt_topic = self.config.TOPICS.get(self.sensor_type)
            if mqtt_topic:
                self.mqtt_client.publish(mqtt_topic, json.dumps(data))
                print(f"Published to MQTT [{mqtt_topic}]: {data}")
            
            # Publish to Kafka
            kafka_topic = self.config.KAFKA_TOPICS.get(self.sensor_type)
            if kafka_topic:
                self.kafka_producer.send(kafka_topic, data)
                print(f"Published to Kafka [{kafka_topic}]: {data}")
            
            return True
            
        except Exception as e:
            print(f"Error publishing data for {self.sensor_type}: {e}")
            return False
    
    def stop(self):
        """Stop the publisher and clean up connections"""
        try:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            self.kafka_producer.close()
        except Exception as e:
            print(f"Error stopping publisher for {self.sensor_type}: {e}")