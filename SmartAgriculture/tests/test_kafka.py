import os
from dotenv import load_dotenv
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

load_dotenv()

def test_kafka_connection():
    """Test Kafka connection"""
    try:
        kafka_host = os.getenv('KAFKA_HOST')
        
        # Test producer connection
        producer = KafkaProducer(
            bootstrap_servers=[kafka_host],
            value_serializer=lambda v: str(v).encode('utf-8')
        )
        
        # Test consumer connection
        consumer = KafkaConsumer(
            bootstrap_servers=[kafka_host],
            value_deserializer=lambda m: m.decode('utf-8')
        )
        
        print("✓ Kafka connection successful!")
        print(f"  Connected to: {kafka_host}")
        
        producer.close()
        consumer.close()
        return True
        
    except KafkaError as e:
        print(f"✗ Kafka connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Kafka connection error: {e}")
        return False

if __name__ == "__main__":
    test_kafka_connection()