"""
Feature Engineering Module
Creates additional features from sensor data for ML models
"""
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Creates features from sensor data"""
    
    def __init__(self):
        self.feature_stats = {
            'total_processed': 0,
            'features_created': 0
        }
        
    def create_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create features from sensor data
        
        Args:
            data: Dictionary containing sensor data
            
        Returns:
            Data dictionary with additional features
        """
        self.feature_stats['total_processed'] += 1
        
        if not data:
            return data
        
        # Extract timestamp
        timestamp = data.get('timestamp')
        if not timestamp:
            return data
        
        # Convert to datetime if string
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp)
            except Exception as e:
                logger.warning(f"Could not parse timestamp: {e}")
                return data
        elif isinstance(timestamp, datetime):
            dt = timestamp
        else:
            return data
        
        # Create time-based features
        data = self._create_time_features(data, dt)
        
        # Create sensor-specific features
        sensor_type = data.get('sensor_type')
        if sensor_type:
            data = self._create_sensor_specific_features(data, sensor_type)
        
        # Create derived features
        data = self._create_derived_features(data)
        
        self.feature_stats['features_created'] += 1
        
        return data
    
    def _create_time_features(self, data: Dict[str, Any], dt: datetime) -> Dict[str, Any]:
        """Create time-based features"""
        
        # Basic time components
        data['year'] = dt.year
        data['month'] = dt.month
        data['day'] = dt.day
        data['hour'] = dt.hour
        data['minute'] = dt.minute
        data['second'] = dt.second
        data['weekday'] = dt.weekday()  # 0=Monday, 6=Sunday
        data['day_of_year'] = dt.timetuple().tm_yday
        
        # Derived time features
        data['is_weekend'] = 1 if dt.weekday() >= 5 else 0
        data['is_night'] = 1 if dt.hour < 6 or dt.hour > 20 else 0
        data['is_morning'] = 1 if 6 <= dt.hour < 12 else 0
        data['is_afternoon'] = 1 if 12 <= dt.hour < 18 else 0
        data['is_evening'] = 1 if 18 <= dt.hour <= 20 else 0
        
        # Season (Northern hemisphere)
        month = dt.month
        if month in [12, 1, 2]:
            data['season'] = 'winter'
            data['season_num'] = 0
        elif month in [3, 4, 5]:
            data['season'] = 'spring'
            data['season_num'] = 1
        elif month in [6, 7, 8]:
            data['season'] = 'summer'
            data['season_num'] = 2
        else:
            data['season'] = 'fall'
            data['season_num'] = 3
        
        # Time of day in hours (cyclic feature)
        data['hour_sin'] = self._sin_transform(dt.hour, 24)
        data['hour_cos'] = self._cos_transform(dt.hour, 24)
        
        # Month (cyclic feature)
        data['month_sin'] = self._sin_transform(dt.month - 1, 12)
        data['month_cos'] = self._cos_transform(dt.month - 1, 12)
        
        # Day of year (cyclic feature)
        data['day_of_year_sin'] = self._sin_transform(dt.timetuple().tm_yday - 1, 365)
        data['day_of_year_cos'] = self._cos_transform(dt.timetuple().tm_yday - 1, 365)
        
        return data
    
    def _create_sensor_specific_features(self, data: Dict[str, Any], sensor_type: str) -> Dict[str, Any]:
        """Create sensor-specific features"""
        
        if sensor_type == 'temperature':
            data = self._create_temperature_features(data)
        elif sensor_type == 'humidity':
            data = self._create_humidity_features(data)
        elif sensor_type == 'soil_moisture':
            data = self._create_soil_moisture_features(data)
        elif sensor_type == 'ph':
            data = self._create_ph_features(data)
        elif sensor_type == 'rainfall':
            data = self._create_rainfall_features(data)
        elif sensor_type == 'light':
            data = self._create_light_features(data)
        elif sensor_type == 'wind':
            data = self._create_wind_features(data)
        elif sensor_type == 'water_quality':
            data = self._create_water_quality_features(data)
        elif sensor_type == 'gps':
            data = self._create_gps_features(data)
        elif sensor_type == 'animal':
            data = self._create_animal_features(data)
        
        return data
    
    def _create_temperature_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create temperature-specific features"""
        
        temp = data.get('temperature')
        
        if temp is not None and not (isinstance(temp, float) and temp != temp):
            # Temperature categories
            if temp < 10:
                data['temp_category'] = 'cold'
                data['temp_category_num'] = 0
            elif temp < 20:
                data['temp_category'] = 'cool'
                data['temp_category_num'] = 1
            elif temp < 30:
                data['temp_category'] = 'moderate'
                data['temp_category_num'] = 2
            else:
                data['temp_category'] = 'hot'
                data['temp_category_num'] = 3
            
            # Growing degree days (base 10°C)
            if temp > 10:
                data['gdd'] = temp - 10
            else:
                data['gdd'] = 0
        
        return data
    
    def _create_humidity_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create humidity-specific features"""
        
        humidity = data.get('humidity')
        
        if humidity is not None and not (isinstance(humidity, float) and humidity != humidity):
            # Humidity categories
            if humidity < 30:
                data['humidity_category'] = 'dry'
                data['humidity_category_num'] = 0
            elif humidity < 60:
                data['humidity_category'] = 'moderate'
                data['humidity_category_num'] = 1
            else:
                data['humidity_category'] = 'humid'
                data['humidity_category_num'] = 2
            
            # Dew point approximation (simplified)
            temp = data.get('temperature')
            if temp is not None:
                # Simplified dew point calculation
                data['dew_point'] = temp - ((100 - humidity) / 5)
        
        return data
    
    def _create_soil_moisture_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create soil moisture-specific features"""
        
        moisture = data.get('soil_moisture')
        
        if moisture is not None and not (isinstance(moisture, float) and moisture != moisture):
            # Moisture status
            if moisture < 30:
                data['moisture_status'] = 'dry'
                data['moisture_status_num'] = 0
            elif moisture < 60:
                data['moisture_status'] = 'optimal'
                data['moisture_status_num'] = 1
            else:
                data['moisture_status'] = 'wet'
                data['moisture_status_num'] = 2
        
        return data
    
    def _create_ph_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create pH-specific features"""
        
        ph = data.get('ph')
        
        if ph is not None and not (isinstance(ph, float) and ph != ph):
            # pH categories
            if ph < 6.0:
                data['ph_category'] = 'acidic'
                data['ph_category_num'] = 0
            elif ph < 7.0:
                data['ph_category'] = 'slightly_acidic'
                data['ph_category_num'] = 1
            elif ph == 7.0:
                data['ph_category'] = 'neutral'
                data['ph_category_num'] = 2
            elif ph <= 8.0:
                data['ph_category'] = 'slightly_alkaline'
                data['ph_category_num'] = 3
            else:
                data['ph_category'] = 'alkaline'
                data['ph_category_num'] = 4
            
            # Suitability for most crops (optimal: 6.0-7.0)
            data['ph_suitable'] = 1 if 6.0 <= ph <= 7.0 else 0
        
        return data
    
    def _create_rainfall_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create rainfall-specific features"""
        
        rainfall = data.get('rainfall')
        
        if rainfall is not None and not (isinstance(rainfall, float) and rainfall != rainfall):
            # Rainfall intensity
            if rainfall == 0:
                data['rainfall_intensity'] = 'none'
                data['rainfall_intensity_num'] = 0
            elif rainfall < 2.5:
                data['rainfall_intensity'] = 'light'
                data['rainfall_intensity_num'] = 1
            elif rainfall < 10:
                data['rainfall_intensity'] = 'moderate'
                data['rainfall_intensity_num'] = 2
            elif rainfall < 25:
                data['rainfall_intensity'] = 'heavy'
                data['rainfall_intensity_num'] = 3
            else:
                data['rainfall_intensity'] = 'extreme'
                data['rainfall_intensity_num'] = 4
            
            # Cumulative rainfall indicator
            data['has_rain'] = 1 if rainfall > 0 else 0
        
        return data
    
    def _create_light_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create light-specific features"""
        
        light = data.get('light_intensity')
        hour = data.get('hour')
        
        if light is not None and not (isinstance(light, float) and light != light):
            # Light intensity categories
            if light < 100:
                data['light_category'] = 'very_dark'
                data['light_category_num'] = 0
            elif light < 1000:
                data['light_category'] = 'dark'
                data['light_category_num'] = 1
            elif light < 10000:
                data['light_category'] = 'moderate'
                data['light_category_num'] = 2
            elif light < 50000:
                data['light_category'] = 'bright'
                data['light_category_num'] = 3
            else:
                data['light_category'] = 'very_bright'
                data['light_category_num'] = 4
            
            # Photosynthetically active radiation approximation
            data['par_approx'] = light * 0.02  # Rough approximation
        
        return data
    
    def _create_wind_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create wind-specific features"""
        
        wind_speed = data.get('wind_speed')
        
        if wind_speed is not None and not (isinstance(wind_speed, float) and wind_speed != wind_speed):
            # Wind speed categories (Beaufort scale simplified)
            if wind_speed < 1:
                data['wind_category'] = 'calm'
                data['wind_category_num'] = 0
            elif wind_speed < 6:
                data['wind_category'] = 'light'
                data['wind_category_num'] = 1
            elif wind_speed < 12:
                data['wind_category'] = 'moderate'
                data['wind_category_num'] = 2
            elif wind_speed < 20:
                data['wind_category'] = 'strong'
                data['wind_category_num'] = 3
            else:
                data['wind_category'] = 'very_strong'
                data['wind_category_num'] = 4
            
            # Wind direction cardinal
            direction = data.get('wind_direction')
            if direction is not None:
                data['wind_cardinal'] = self._get_wind_cardinal(direction)
        
        return data
    
    def _create_water_quality_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create water quality-specific features"""
        
        ph = data.get('ph')
        dissolved_oxygen = data.get('dissolved_oxygen')
        turbidity = data.get('turbidity')
        
        # Water quality index (simplified)
        quality_score = 0
        features_count = 0
        
        if ph is not None and not (isinstance(ph, float) and ph != ph):
            # Optimal pH: 6.5-8.5
            if 6.5 <= ph <= 8.5:
                quality_score += 1
            features_count += 1
        
        if dissolved_oxygen is not None and not (isinstance(dissolved_oxygen, float) and dissolved_oxygen != dissolved_oxygen):
            # Optimal DO: > 6 mg/L
            if dissolved_oxygen >= 6:
                quality_score += 1
            features_count += 1
        
        if turbidity is not None and not (isinstance(turbidity, float) and turbidity != turbidity):
            # Optimal turbidity: < 5 NTU
            if turbidity < 5:
                quality_score += 1
            features_count += 1
        
        if features_count > 0:
            data['water_quality_index'] = quality_score / features_count
        
        return data
    
    def _create_gps_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create GPS-specific features"""
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        altitude = data.get('altitude')
        speed = data.get('speed')
        
        if latitude is not None and longitude is not None:
            # Hemisphere
            data['hemisphere'] = 'N' if latitude >= 0 else 'S'
            data['hemisphere_num'] = 0 if latitude >= 0 else 1
            
            # Approximate climate zone (very simplified)
            abs_lat = abs(latitude)
            if abs_lat < 23.5:
                data['climate_zone'] = 'tropical'
            elif abs_lat < 35:
                data['climate_zone'] = 'subtropical'
            elif abs_lat < 66.5:
                data['climate_zone'] = 'temperate'
            else:
                data['climate_zone'] = 'polar'
        
        if speed is not None and not (isinstance(speed, float) and speed != speed):
            # Movement indicator
            data['is_moving'] = 1 if speed > 0.5 else 0
        
        return data
    
    def _create_animal_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create animal-specific features"""
        
        activity = data.get('activity_level')
        body_temp = data.get('body_temperature')
        heart_rate = data.get('heart_rate')
        
        if activity is not None and not (isinstance(activity, float) and activity != activity):
            # Activity level categories
            if activity < 30:
                data['activity_category'] = 'resting'
                data['activity_category_num'] = 0
            elif activity < 60:
                data['activity_category'] = 'moderate'
                data['activity_category_num'] = 1
            else:
                data['activity_category'] = 'active'
                data['activity_category_num'] = 2
        
        if body_temp is not None and not (isinstance(body_temp, float) and body_temp != body_temp):
            # Temperature status (for cattle)
            if body_temp < 37.5:
                data['temp_status'] = 'low'
                data['temp_status_num'] = 0
            elif body_temp <= 39.0:
                data['temp_status'] = 'normal'
                data['temp_status_num'] = 1
            else:
                data['temp_status'] = 'high'
                data['temp_status_num'] = 2
        
        if heart_rate is not None and not (isinstance(heart_rate, float) and heart_rate != heart_rate):
            # Heart rate status (for cattle: 40-80 bpm normal)
            if heart_rate < 40 or heart_rate > 80:
                data['heart_rate_status'] = 'abnormal'
                data['heart_rate_status_num'] = 0
            else:
                data['heart_rate_status'] = 'normal'
                data['heart_rate_status_num'] = 1
        
        return data
    
    def _create_derived_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create derived features from multiple fields"""
        
        # Comfort index (temperature + humidity)
        temp = data.get('temperature')
        humidity = data.get('humidity')
        
        if temp is not None and humidity is not None:
            if not (isinstance(temp, float) and temp != temp) and not (isinstance(humidity, float) and humidity != humidity):
                # Simplified heat index
                data['heat_index'] = temp + (humidity / 100) * 5
        
        return data
    
    def _sin_transform(self, value: float, period: float) -> float:
        """Sine transformation for cyclic features"""
        import math
        return math.sin(2 * math.pi * value / period)
    
    def _cos_transform(self, value: float, period: float) -> float:
        """Cosine transformation for cyclic features"""
        import math
        return math.cos(2 * math.pi * value / period)
    
    def _get_wind_cardinal(self, direction: float) -> str:
        """Convert wind direction degrees to cardinal direction"""
        
        directions = [
            'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'
        ]
        
        index = round(direction / 22.5) % 16
        return directions[index]
    
    def create_features_batch(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create features for a batch of data
        
        Args:
            data_list: List of data dictionaries
            
        Returns:
            List of data dictionaries with features
        """
        return [self.create_features(data) for data in data_list]
    
    def get_stats(self) -> Dict[str, int]:
        """Get feature engineering statistics"""
        return self.feature_stats.copy()
    
    def reset_stats(self):
        """Reset feature engineering statistics"""
        self.feature_stats = {
            'total_processed': 0,
            'features_created': 0
        }


def create_features(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to create features
    
    Args:
        data: Dictionary containing sensor data
        
    Returns:
        Data dictionary with additional features
    """
    engineer = FeatureEngineer()
    return engineer.create_features(data)


def create_features_batch(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convenience function to create features for batch
    
    Args:
        data_list: List of data dictionaries
        
    Returns:
        List of data dictionaries with features
    """
    engineer = FeatureEngineer()
    return engineer.create_features_batch(data_list)