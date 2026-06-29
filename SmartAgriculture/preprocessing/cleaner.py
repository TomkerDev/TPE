"""
Data Cleaning Module
Cleans and prepares sensor data for processing
"""
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """Cleans sensor data"""
    
    def __init__(self):
        self.seen = set()  # For duplicate detection
        self.cleaning_stats = {
            'total_processed': 0,
            'null_values_cleaned': 0,
            'type_conversions': 0,
            'duplicates_removed': 0
        }
        
    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean sensor data
        
        Args:
            data: Dictionary containing sensor data
            
        Returns:
            Cleaned data dictionary
        """
        self.cleaning_stats['total_processed'] += 1
        
        if not data:
            return data
        
        # Clean null values
        data = self._clean_null_values(data)
        
        # Convert types
        data = self._convert_types(data)
        
        # Remove duplicates
        data = self._remove_duplicates(data)
        
        # Clean string values
        data = self._clean_strings(data)
        
        return data
    
    def _clean_null_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean null/None values"""
        for key, value in data.items():
            if value is None:
                # Replace None with NaN for numeric fields
                if key in ['value', 'temperature', 'humidity', 'soil_moisture', 'ph', 
                           'rainfall', 'light_intensity', 'wind_speed', 'wind_direction',
                           'dissolved_oxygen', 'turbidity', 'conductivity',
                           'latitude', 'longitude', 'altitude', 'speed',
                           'activity_level', 'body_temperature', 'heart_rate']:
                    data[key] = np.nan
                    self.cleaning_stats['null_values_cleaned'] += 1
                    logger.debug(f"Replaced None with NaN for field: {key}")
        
        return data
    
    def _convert_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert string values to appropriate types"""
        
        # Convert numeric fields
        numeric_fields = [
            'value', 'temperature', 'humidity', 'soil_moisture', 'ph',
            'rainfall', 'light_intensity', 'wind_speed', 'wind_direction',
            'dissolved_oxygen', 'turbidity', 'conductivity',
            'latitude', 'longitude', 'altitude', 'speed',
            'activity_level', 'body_temperature', 'heart_rate'
        ]
        
        for field in numeric_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = float(data[field])
                    self.cleaning_stats['type_conversions'] += 1
                    logger.debug(f"Converted {field} from string to float: {data[field]}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to convert {field} to float: {e}")
                    data[field] = np.nan
        
        return data
    
    def _remove_duplicates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove duplicate readings based on sensor_id and timestamp"""
        
        sensor_id = data.get('sensor_id')
        timestamp = data.get('timestamp')
        
        if sensor_id and timestamp:
            # Create unique key
            key = (sensor_id, str(timestamp))
            
            if key in self.seen:
                logger.debug(f"Duplicate detected: {sensor_id} at {timestamp}")
                self.cleaning_stats['duplicates_removed'] += 1
                return None  # Signal to remove this duplicate
            
            self.seen.add(key)
        
        return data
    
    def _clean_strings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean string values"""
        
        # Strip whitespace from string fields
        string_fields = ['sensor_id', 'sensor_type', 'unit', 'metric', 'health_status', 'location_zone']
        
        for field in string_fields:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()
        
        return data
    
    def clean_batch(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean a batch of data
        
        Args:
            data_list: List of data dictionaries
            
        Returns:
            List of cleaned data dictionaries (duplicates removed)
        """
        cleaned_data = []
        
        for data in data_list:
            cleaned = self.clean(data)
            if cleaned is not None:  # Not a duplicate
                cleaned_data.append(cleaned)
        
        return cleaned_data
    
    def get_stats(self) -> Dict[str, int]:
        """Get cleaning statistics"""
        return self.cleaning_stats.copy()
    
    def reset_stats(self):
        """Reset cleaning statistics"""
        self.cleaning_stats = {
            'total_processed': 0,
            'null_values_cleaned': 0,
            'type_conversions': 0,
            'duplicates_removed': 0
        }
        self.seen.clear()


def clean_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to clean data
    
    Args:
        data: Dictionary containing sensor data
        
    Returns:
        Cleaned data dictionary
    """
    cleaner = DataCleaner()
    return cleaner.clean(data)


def clean_batch_data(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convenience function to clean batch data
    
    Args:
        data_list: List of data dictionaries
        
    Returns:
        List of cleaned data dictionaries
    """
    cleaner = DataCleaner()
    return cleaner.clean_batch(data_list)