"""
Data Validation Module
Validates sensor data for completeness and correctness
"""
from datetime import datetime
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates sensor data"""
    
    REQUIRED_FIELDS = [
        "sensor_id",
        "timestamp"
    ]
    
    SENSOR_TYPE_FIELD = "sensor_type"
    
    def __init__(self):
        self.validation_errors = []
        
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate sensor data
        
        Args:
            data: Dictionary containing sensor data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        self.validation_errors = []
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                error_msg = f"Champ manquant : {field}"
                self.validation_errors.append(error_msg)
                return False, error_msg
        
        # Validate timestamp
        timestamp_valid, timestamp_msg = self._validate_timestamp(data.get("timestamp"))
        if not timestamp_valid:
            self.validation_errors.append(timestamp_msg)
            return False, timestamp_msg
        
        # Validate sensor type
        if self.SENSOR_TYPE_FIELD not in data:
            error_msg = f"Champ manquant : {self.SENSOR_TYPE_FIELD}"
            self.validation_errors.append(error_msg)
            return False, error_msg
        
        # Validate value if present
        if "value" in data:
            value_valid, value_msg = self._validate_value(data.get("value"))
            if not value_valid:
                self.validation_errors.append(value_msg)
                return False, value_msg
        
        # Validate sensor-specific fields
        sensor_type = data.get("sensor_type")
        sensor_valid, sensor_msg = self._validate_sensor_specific(data, sensor_type)
        if not sensor_valid:
            self.validation_errors.append(sensor_msg)
            return False, sensor_msg
        
        return True, "OK"
    
    def _validate_timestamp(self, timestamp) -> Tuple[bool, str]:
        """Validate timestamp field"""
        try:
            if isinstance(timestamp, str):
                datetime.fromisoformat(timestamp)
            elif isinstance(timestamp, datetime):
                pass  # Valid datetime object
            else:
                return False, "Timestamp invalide"
            return True, "OK"
        except Exception as e:
            return False, f"Timestamp invalide: {str(e)}"
    
    def _validate_value(self, value) -> Tuple[bool, str]:
        """Validate numeric value"""
        try:
            if value is None:
                return True, "OK"  # None values are handled by cleaner
            
            float(value)
            return True, "OK"
        except (ValueError, TypeError) as e:
            return False, f"Valeur numérique invalide: {str(e)}"
    
    def _validate_sensor_specific(self, data: Dict[str, Any], sensor_type: str) -> Tuple[bool, str]:
        """Validate sensor-specific fields"""
        
        # Temperature sensor
        if sensor_type == "temperature":
            if "temperature" not in data:
                return False, "Champ manquant : temperature"
        
        # Humidity sensor
        elif sensor_type == "humidity":
            if "humidity" not in data:
                return False, "Champ manquant : humidity"
        
        # Soil moisture sensor
        elif sensor_type == "soil_moisture":
            if "soil_moisture" not in data:
                return False, "Champ manquant : soil_moisture"
        
        # pH sensor
        elif sensor_type == "ph":
            if "ph" not in data:
                return False, "Champ manquant : ph"
        
        # Rainfall sensor
        elif sensor_type == "rainfall":
            if "rainfall" not in data:
                return False, "Champ manquant : rainfall"
        
        # Light sensor
        elif sensor_type == "light":
            if "light_intensity" not in data:
                return False, "Champ manquant : light_intensity"
        
        # Wind sensor
        elif sensor_type == "wind":
            if "wind_speed" not in data:
                return False, "Champ manquant : wind_speed"
            if "wind_direction" not in data:
                return False, "Champ manquant : wind_direction"
        
        # Water quality sensor
        elif sensor_type == "water_quality":
            required = ["ph", "dissolved_oxygen", "turbidity", "conductivity"]
            for field in required:
                if field not in data:
                    return False, f"Champ manquant : {field}"
        
        # GPS sensor
        elif sensor_type == "gps":
            required = ["latitude", "longitude"]
            for field in required:
                if field not in data:
                    return False, f"Champ manquant : {field}"
        
        # Animal sensor
        elif sensor_type == "animal":
            required = ["animal_id", "activity_level", "body_temperature", "heart_rate"]
            for field in required:
                if field not in data:
                    return False, f"Champ manquant : {field}"
        
        return True, "OK"
    
    def get_errors(self) -> list:
        """Get list of validation errors"""
        return self.validation_errors


def validate_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Convenience function to validate data
    
    Args:
        data: Dictionary containing sensor data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    validator = DataValidator()
    return validator.validate(data)


def validate_batch(data_list: list) -> Tuple[int, int, list]:
    """
    Validate a batch of data
    
    Args:
        data_list: List of data dictionaries
        
    Returns:
        Tuple of (valid_count, invalid_count, invalid_items)
    """
    validator = DataValidator()
    valid_count = 0
    invalid_count = 0
    invalid_items = []
    
    for i, data in enumerate(data_list):
        is_valid, error_msg = validator.validate(data)
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
            invalid_items.append({
                'index': i,
                'data': data,
                'error': error_msg
            })
    
    return valid_count, invalid_count, invalid_items