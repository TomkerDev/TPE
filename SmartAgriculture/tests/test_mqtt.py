import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

load_dotenv()

def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the server"""
    if rc == 0:
        print("✓ MQTT connection successful!")
        print(f"  Connected to broker: {os.getenv('MQTT_HOST')}:{os.getenv('MQTT_PORT')}")
        client.disconnect()
    else:
        print(f"✗ MQTT connection failed with code: {rc}")

def on_disconnect(client, userdata, rc):
    """Callback for when the client disconnects from the server"""
    pass

def test_mqtt_connection():
    """Test MQTT connection"""
    try:
        mqtt_host = os.getenv('MQTT_HOST')
        mqtt_port = int(os.getenv('MQTT_PORT'))
        
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        
        # Connect to broker
        client.connect(mqtt_host, mqtt_port, 60)
        
        # Start the loop to process callbacks
        client.loop_start()
        
        # Wait a bit for connection to establish
        import time
        time.sleep(2)
        
        client.loop_stop()
        return True
        
    except Exception as e:
        print(f"✗ MQTT connection error: {e}")
        return False

if __name__ == "__main__":
    test_mqtt_connection()