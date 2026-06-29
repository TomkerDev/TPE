"""
Outlier Detection Module
Detects and handles anomalous sensor readings
"""
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class OutlierDetector:
    """Detects outliers in sensor data"""
    
    # Sensor-specific limits (min, max)
    LIMITS = {
        "temperature": (-20, 60),
        "humidity": (0, 100),
        "soil_moisture": (0, 100),
        "ph": (0, 14),
        "wind": (0, 150),
        "light": (0, 120000),
        "rainfall": (0, 500),
        "water_quality": (0, 100),
        "gps": {
            "latitude": (-90, 90),
            "longitude": (-180, 180),
            "altitude": (-500, 10000),
            "speed": (0, 500)
        },
        "animal": {
            "activity_level": (0, 100),
            "body_temperature": (35, 42),
            "heart_rate": (20, 200)
        }
    }
    
    def __init__(self):
        self.outlier_stats = {
            'total_checked': 0,
            'outliers_detected': 0,
            'outliers_by_type': {}
        }
        
    def detect(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Detect if data contains outliers
        
        Args:
            data: Dictionary containing sensor data
            
        Returns:
            Tuple of (is_outlier, reason)
        """
        self.outlier_stats['total_checked'] += 1
        
        if not data:
            return False, ""
        
        sensor_type = data.get("sensor_type")
        
        if not sensor_type:
            return False, ""
        
        # Check sensor-specific limits
        if sensor_type in self.LIMITS:
            limits = self.LIMITS[sensor_type]
            
            # Handle simple (min, max) limits
            if isinstance(limits, tuple):
                is_outlier, reason = self._check_value_limits(data, sensor_type, limits)
                if is_outlier:
                    self._record_outlier(sensor_type)
                    return True, reason
            
            # Handle nested limits (for complex sensors like GPS, animal)
            elif isinstance(limits, dict):
                is_outlier, reason = self._check_nested_limits(data, limits)
                if is_outlier:
                    self._record_outlier(sensor_type)
                    return True, reason
        
        return False, ""
    
    def _check_value_limits(self, data: Dict[str, Any], sensor_type: str, 
                           limits: Tuple[float, float]) -> Tuple[bool, str]:
        """Check if value is within limits"""
        
        # Get the value field based on sensor type
        value_field = self._get_value_field(sensor_type)
        
        if not value_field or value_field not in data:
            return False, ""
        
        value = data.get(value_field)
        
        if value is None or (isinstance(value, float) and (value != value)):  # NaN check
            return False, ""
        
        try:
            value_float = float(value)
            min_val, max_val = limits
            
            if value_float < min_val:
                return True, f"Valeur {value_float} inférieure au minimum {min_val}"
            
            if value_float > max_val:
                return True, f"Valeur {value_float} supérieure au maximum {max_val}"
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not convert value to float: {e}")
            return False, ""
        
        return False, ""
    
    def _check_nested_limits(self, data: Dict[str, Any], 
                            limits: Dict[str, Tuple[float, float]]) -> Tuple[bool, str]:
        """Check nested limits for complex sensors"""
        
        for field, (min_val, max_val) in limits.items():
            if field in data:
                value = data.get(field)
                
                if value is None or (isinstance(value, float) and (value != value)):  # NaN check
                    continue
                
                try:
                    value_float = float(value)
                    
                    if value_float < min_val:
                        return True, f"{field}: valeur {value_float} inférieure au minimum {min_val}"
                    
                    if value_float > max_val:
                        return True, f"{field}: valeur {value_float} supérieure au maximum {max_val}"
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Could not convert {field} to float: {e}")
                    continue
        
        return False, ""
    
    def _get_value_field(self, sensor_type: str) -> str:
        """Get the main value field for a sensor type"""
        
        value_fields = {
            "temperature": "temperature",
            "humidity": "humidity",
            "soil_moisture": "soil_moisture",
            "ph": "ph",
            "rainfall": "rainfall",
            "light": "light_intensity",
            "wind": "wind_speed",
            "water_quality": "ph",  # Use pH as primary value
            "gps": "latitude",  # Use latitude as primary
            "animal": "activity_level"  # Use activity level as primary
        }
        
        return value_fields.get(sensor_type)
    
    def _record_outlier(self, sensor_type: str):
        """Record outlier detection"""
        self.outlier_stats['outliers_detected'] += 1
        
        if sensor_type not in self.outlier_stats['outliers_by_type']:
            self.outlier_stats['outliers_by_type'][sensor_type] = 0
        
        self.outlier_stats['outliers_by_type'][sensor_type] += 1
    
    def detect_batch(self, data_list: List[Dict[str, Any]]) -> List[Tuple[int, bool, str]]:
        """
        Detect outliers in a batch of data
        
        Args:
            data_list: List of data dictionaries
            
        Returns:
            List of tuples (index, is_outlier, reason)
        """
        results = []
        
        for i, data in enumerate(data_list):
            is_outlier, reason = self.detect(data)
            results.append((i, is_outlier, reason))
        
        return results
    
    def filter_outliers(self, data_list: List[Dict[str, Any]], 
                       remove: bool = False) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filter outliers from data list
        
        Args:
            data_list: List of data dictionaries
            remove: If True, remove outliers; if False, return them separately
            
        Returns:
            Tuple of (valid_data, outlier_data)
        """
        valid_data = []
        outlier_data = []
        
        for data in data_list:
            is_outlier, reason = self.detect(data)
            
            if is_outlier:
                data['outlier_reason'] = reason
                outlier_data.append(data)
                
                if not remove:
                    valid_data.append(data)
            else:
                valid_data.append(data)
        
        return valid_data, outlier_data
    
    def get_stats(self) -> Dict[str, Any]:
        """Get outlier detection statistics"""
        return self.outlier_stats.copy()
    
    def reset_stats(self):
        """Reset outlier detection statistics"""
        self.outlier_stats = {
            'total_checked': 0,
            'outliers_detected': 0,
            'outliers_by_type': {}
        }


def detect_outlier(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Convenience function to detect outliers
    
    Args:
        data: Dictionary containing sensor data
        
    Returns:
        Tuple of (is_outlier, reason)
    """
    detector = OutlierDetector()
    return detector.detect(data)


def detect_outliers_batch(data_list: List[Dict[str, Any]]) -> List[Tuple[int, bool, str]]:
    """
    Convenience function to detect outliers in batch
    
    Args:
        data_list: List of data dictionaries
        
    Returns:
        List of tuples (index, is_outlier, reason)
    """
    detector = OutlierDetector()
    return detector.detect_batch(data_list)


def filter_outliers(data_list: List[Dict[str, Any]], 
                   remove: bool = False) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Convenience function to filter outliers
    
    Args:
        data_list: List of data dictionaries
        remove: If True, remove outliers; if False, return them separately
        
    Returns:
        Tuple of (valid_data, outlier_data)
    """
    detector = OutlierDetector()
    return detector.filter_outliers(data_list, remove)