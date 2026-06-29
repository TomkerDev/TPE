"""
Data Normalization Module
Normalizes units and values across different sensor types
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class DataNormalizer:
    """Normalizes sensor data units and values"""
    
    # Unit conversion mappings
    UNIT_CONVERSIONS = {
        'temperature': {
            'K': ('°C', lambda x: x - 273.15),
            'F': ('°C', lambda x: (x - 32) * 5/9),
            'celsius': ('°C', lambda x: x),
            'C': ('°C', lambda x: x),
        },
        'humidity': {
            'percent': ('%', lambda x: x),
            '%': ('%', lambda x: x),
        },
        'soil_moisture': {
            'percent': ('%', lambda x: x),
            '%': ('%', lambda x: x),
            'VWC': ('%', lambda x: x * 100),  # Volumetric Water Content to percent
        },
        'ph': {
            'pH': ('pH', lambda x: x),
            'ph': ('pH', lambda x: x),
        },
        'rainfall': {
            'mm': ('mm', lambda x: x),
            'cm': ('mm', lambda x: x * 10),
            'in': ('mm', lambda x: x * 25.4),
        },
        'light': {
            'lux': ('Lux', lambda x: x),
            'Lux': ('Lux', lambda x: x),
            'W/m2': ('Lux', lambda x: x * 126.7),  # Approximate conversion
        },
        'wind': {
            'km/h': ('km/h', lambda x: x),
            'm/s': ('km/h', lambda x: x * 3.6),
            'mph': ('km/h', lambda x: x * 1.60934),
        },
        'water_quality': {
            'mg/L': ('mg/L', lambda x: x),
            'NTU': ('NTU', lambda x: x),
            'µS/cm': ('µS/cm', lambda x: x),
        },
        'gps': {
            'degrees': ('degrees', lambda x: x),
            'm': ('m', lambda x: x),
            'km/h': ('km/h', lambda x: x),
        },
        'animal': {
            'celsius': ('°C', lambda x: x),
            'bpm': ('bpm', lambda x: x),
            '%': ('%', lambda x: x),
        }
    }
    
    def __init__(self):
        self.normalization_stats = {
            'total_processed': 0,
            'units_normalized': 0,
            'values_converted': 0
        }
        
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize sensor data
        
        Args:
            data: Dictionary containing sensor data
            
        Returns:
            Normalized data dictionary
        """
        self.normalization_stats['total_processed'] += 1
        
        if not data:
            return data
        
        sensor_type = data.get('sensor_type')
        
        if not sensor_type:
            logger.warning("No sensor_type specified, skipping normalization")
            return data
        
        # Normalize based on sensor type
        if sensor_type == 'temperature':
            data = self._normalize_temperature(data)
        elif sensor_type == 'humidity':
            data = self._normalize_humidity(data)
        elif sensor_type == 'soil_moisture':
            data = self._normalize_soil_moisture(data)
        elif sensor_type == 'ph':
            data = self._normalize_ph(data)
        elif sensor_type == 'rainfall':
            data = self._normalize_rainfall(data)
        elif sensor_type == 'light':
            data = self._normalize_light(data)
        elif sensor_type == 'wind':
            data = self._normalize_wind(data)
        elif sensor_type == 'water_quality':
            data = self._normalize_water_quality(data)
        elif sensor_type == 'gps':
            data = self._normalize_gps(data)
        elif sensor_type == 'animal':
            data = self._normalize_animal(data)
        
        return data
    
    def _normalize_temperature(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize temperature data"""
        if 'temperature' in data and 'unit' in data:
            unit = data['unit']
            value = data['temperature']
            
            if unit in self.UNIT_CONVERSIONS['temperature']:
                target_unit, converter = self.UNIT_CONVERSIONS['temperature'][unit]
                if unit != target_unit:
                    data['temperature'] = round(converter(value), 2)
                    data['unit'] = target_unit
                    self.normalization_stats['values_converted'] += 1
                    logger.debug(f"Converted temperature from {unit} to {target_unit}: {value} -> {data['temperature']}")
        
        return data
    
    def _normalize_humidity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize humidity data"""
        if 'humidity' in data:
            # Ensure humidity is in percentage
            if 'unit' in data and data['unit'] not in ['%', 'percent']:
                # Convert if needed
                unit = data['unit']
                value = data['humidity']
                
                if unit in self.UNIT_CONVERSIONS['humidity']:
                    target_unit, converter = self.UNIT_CONVERSIONS['humidity'][unit]
                    data['humidity'] = round(converter(value), 2)
                    data['unit'] = target_unit
                    self.normalization_stats['values_converted'] += 1
            
            # Always set unit to %
            data['unit'] = '%'
            self.normalization_stats['units_normalized'] += 1
        
        return data
    
    def _normalize_soil_moisture(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize soil moisture data"""
        if 'soil_moisture' in data:
            # Ensure soil moisture is in percentage
            if 'unit' in data and data['unit'] not in ['%', 'percent']:
                unit = data['unit']
                value = data['soil_moisture']
                
                if unit in self.UNIT_CONVERSIONS['soil_moisture']:
                    target_unit, converter = self.UNIT_CONVERSIONS['soil_moisture'][unit]
                    data['soil_moisture'] = round(converter(value), 2)
                    data['unit'] = target_unit
                    self.normalization_stats['values_converted'] += 1
            
            # Always set unit to %
            data['unit'] = '%'
            self.normalization_stats['units_normalized'] += 1
        
        return data
    
    def _normalize_ph(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize pH data"""
        if 'ph' in data:
            # Ensure pH unit is standardized
            if 'unit' in data:
                data['unit'] = 'pH'
                self.normalization_stats['units_normalized'] += 1
            
            # Validate pH range
            ph_value = data['ph']
            if ph_value < 0 or ph_value > 14:
                logger.warning(f"pH value {ph_value} is outside normal range [0-14]")
        
        return data
    
    def _normalize_rainfall(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize rainfall data"""
        if 'rainfall' in data and 'unit' in data:
            unit = data['unit']
            value = data['rainfall']
            
            if unit in self.UNIT_CONVERSIONS['rainfall']:
                target_unit, converter = self.UNIT_CONVERSIONS['rainfall'][unit]
                if unit != target_unit:
                    data['rainfall'] = round(converter(value), 2)
                    data['unit'] = target_unit
                    self.normalization_stats['values_converted'] += 1
        
        return data
    
    def _normalize_light(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize light intensity data"""
        if 'light_intensity' in data and 'unit' in data:
            unit = data['unit']
            value = data['light_intensity']
            
            if unit in self.UNIT_CONVERSIONS['light']:
                target_unit, converter = self.UNIT_CONVERSIONS['light'][unit]
                if unit != target_unit:
                    data['light_intensity'] = round(converter(value), 2)
                    data['unit'] = target_unit
                    self.normalization_stats['values_converted'] += 1
            else:
                # Default to Lux
                data['unit'] = 'Lux'
                self.normalization_stats['units_normalized'] += 1
        
        return data
    
    def _normalize_wind(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize wind data"""
        if 'wind_speed' in data and 'unit_speed' in data:
            unit = data['unit_speed']
            value = data['wind_speed']
            
            if unit in self.UNIT_CONVERSIONS['wind']:
                target_unit, converter = self.UNIT_CONVERSIONS['wind'][unit]
                if unit != target_unit:
                    data['wind_speed'] = round(converter(value), 2)
                    data['unit_speed'] = target_unit
                    self.normalization_stats['values_converted'] += 1
        
        # Normalize wind direction to degrees
        if 'wind_direction' in data and 'unit_direction' in data:
            data['unit_direction'] = 'degrees'
            self.normalization_stats['units_normalized'] += 1
        
        return data
    
    def _normalize_water_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize water quality data"""
        # Standardize units for water quality parameters
        if 'ph' in data:
            data['unit_ph'] = 'pH'
        
        if 'dissolved_oxygen' in data:
            data['unit_do'] = 'mg/L'
        
        if 'turbidity' in data:
            data['unit_turbidity'] = 'NTU'
        
        if 'conductivity' in data:
            data['unit_conductivity'] = 'µS/cm'
        
        self.normalization_stats['units_normalized'] += 4
        
        return data
    
    def _normalize_gps(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize GPS data"""
        # Ensure coordinates are in decimal degrees
        if 'latitude' in data:
            data['unit_latitude'] = 'degrees'
        
        if 'longitude' in data:
            data['unit_longitude'] = 'degrees'
        
        if 'altitude' in data:
            if 'unit_altitude' in data and data['unit_altitude'] != 'm':
                # Convert to meters if needed
                unit = data['unit_altitude']
                value = data['altitude']
                
                if unit == 'ft':
                    data['altitude'] = round(value * 0.3048, 2)
                    self.normalization_stats['values_converted'] += 1
                
                data['unit_altitude'] = 'm'
            
            self.normalization_stats['units_normalized'] += 1
        
        if 'speed' in data:
            if 'unit_speed' in data and data['unit_speed'] != 'km/h':
                unit = data['unit_speed']
                value = data['speed']
                
                if unit == 'm/s':
                    data['speed'] = round(value * 3.6, 2)
                    self.normalization_stats['values_converted'] += 1
                elif unit == 'mph':
                    data['speed'] = round(value * 1.60934, 2)
                    self.normalization_stats['values_converted'] += 1
                
                data['unit_speed'] = 'km/h'
            
            self.normalization_stats['units_normalized'] += 1
        
        return data
    
    def _normalize_animal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize animal sensor data"""
        # Standardize units
        if 'body_temperature' in data:
            data['unit_temperature'] = '°C'
        
        if 'heart_rate' in data:
            data['unit_heart_rate'] = 'bpm'
        
        if 'activity_level' in data:
            data['unit_activity'] = '%'
        
        self.normalization_stats['units_normalized'] += 3
        
        return data
    
    def get_stats(self) -> Dict[str, int]:
        """Get normalization statistics"""
        return self.normalization_stats.copy()
    
    def reset_stats(self):
        """Reset normalization statistics"""
        self.normalization_stats = {
            'total_processed': 0,
            'units_normalized': 0,
            'values_converted': 0
        }


def normalize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to normalize data
    
    Args:
        data: Dictionary containing sensor data
        
    Returns:
        Normalized data dictionary
    """
    normalizer = DataNormalizer()
    return normalizer.normalize(data)


def normalize_batch_data(data_list: list) -> list:
    """
    Normalize a batch of data
    
    Args:
        data_list: List of data dictionaries
        
    Returns:
        List of normalized data dictionaries
    """
    normalizer = DataNormalizer()
    return [normalizer.normalize(data) for data in data_list]