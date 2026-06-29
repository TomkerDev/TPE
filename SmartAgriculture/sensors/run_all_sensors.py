#!/usr/bin/env python3
"""
Run all sensors simultaneously for Smart Agriculture System
This script starts all sensor types and publishes data to MQTT and Kafka
"""

import time
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import all sensor classes
from sensors.temperature_sensor import TemperatureSensor
from sensors.humidity_sensor import HumiditySensor
from sensors.soil_moisture_sensor import SoilMoistureSensor
from sensors.ph_sensor import PHSensor
from sensors.rainfall_sensor import RainfallSensor
from sensors.light_sensor import LightSensor
from sensors.wind_sensor import WindSensor
from sensors.water_quality_sensor import WaterQualitySensor
from sensors.gps_sensor import GPSSensor
from sensors.animal_sensor import AnimalSensor


class SensorManager:
    """Manager class to run all sensors"""
    
    def __init__(self):
        self.sensors = []
        self.running = True
        
    def create_sensors(self):
        """Create instances of all sensors"""
        print("=" * 60)
        print("Initializing Smart Agriculture Sensors...")
        print("=" * 60)
        
        self.sensors = [
            ("Temperature", TemperatureSensor()),
            ("Humidity", HumiditySensor()),
            ("Soil Moisture", SoilMoistureSensor()),
            ("pH", PHSensor()),
            ("Rainfall", RainfallSensor()),
            ("Light", LightSensor()),
            ("Wind", WindSensor()),
            ("Water Quality", WaterQualitySensor()),
            ("GPS", GPSSensor()),
            ("Animal", AnimalSensor())
        ]
        
        print(f"✓ {len(self.sensors)} sensors initialized successfully\n")
    
    def run_sensor(self, name, sensor, interval=5):
        """Run a single sensor"""
        try:
            print(f"[{name}] Starting...")
            sensor.run(interval=interval)
        except Exception as e:
            print(f"[{name}] Error: {e}")
        finally:
            print(f"[{name}] Stopped")
    
    def run_all_sequential(self, interval=5):
        """Run all sensors sequentially (one after another)"""
        print("\n" + "=" * 60)
        print("Running sensors SEQUENTIALLY")
        print("=" * 60 + "\n")
        
        for name, sensor in self.sensors:
            if not self.running:
                break
            self.run_sensor(name, sensor, interval)
    
    def run_all_parallel(self, interval=5):
        """Run all sensors in parallel (simultaneously)"""
        print("\n" + "=" * 60)
        print("Running sensors in PARALLEL")
        print("=" * 60 + "\n")
        
        with ThreadPoolExecutor(max_workers=len(self.sensors)) as executor:
            futures = {
                executor.submit(self.run_sensor, name, sensor, interval): name
                for name, sensor in self.sensors
            }
            
            try:
                for future in as_completed(futures):
                    name = futures[future]
                    try:
                        future.result()
                    except Exception as e:
                        print(f"[{name}] Exception: {e}")
            except KeyboardInterrupt:
                print("\n\n⚠ Interrupt received, stopping all sensors...")
                self.running = False
    
    def stop_all(self):
        """Stop all sensors"""
        print("\n" + "=" * 60)
        print("Stopping all sensors...")
        print("=" * 60)
        self.running = False
        for name, sensor in self.sensors:
            if hasattr(sensor, 'publisher'):
                sensor.publisher.stop()
                print(f"[{name}] Stopped")


def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print("\n\n⚠ Signal received, shutting down gracefully...")
    sys.exit(0)


def main():
    """Main function"""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create sensor manager
    manager = SensorManager()
    manager.create_sensors()
    
    # Ask user for mode
    print("Select running mode:")
    print("1. Sequential (one sensor at a time)")
    print("2. Parallel (all sensors simultaneously)")
    
    try:
        choice = input("\nEnter your choice (1 or 2, default=2): ").strip()
        if choice == "1":
            manager.run_all_sequential(interval=5)
        else:
            manager.run_all_parallel(interval=5)
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupt received")
    finally:
        manager.stop_all()
        print("\n✓ All sensors stopped. Goodbye!")


if __name__ == "__main__":
    main()