"""
Pydantic Models for Smart Agriculture API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SensorType(str, Enum):
    """Sensor type enumeration"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    SOIL_MOISTURE = "soil_moisture"
    PH = "ph"
    RAINFALL = "rainfall"
    LIGHT = "light"
    WIND = "wind"
    WATER_QUALITY = "water_quality"
    GPS = "gps"
    ANIMAL = "animal"


class Sensor(BaseModel):
    """Sensor model"""
    sensor_id: str
    sensor_type: SensorType
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str = "active"
    installation_date: Optional[datetime] = None
    last_maintenance: Optional[datetime] = None


class SensorData(BaseModel):
    """Sensor data reading model"""
    sensor_id: str
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime
    location: str
    quality_score: Optional[float] = None


class PredictionRequest(BaseModel):
    """Prediction request model"""
    features: List[float] = Field(..., description="List of feature values")
    model_type: Optional[str] = Field("random_forest", description="Model to use for prediction")


class PredictionResponse(BaseModel):
    """Prediction response model"""
    prediction: Any
    confidence: Optional[float] = None
    model_used: str
    timestamp: datetime = Field(default_factory=datetime.now)


class Alert(BaseModel):
    """Alert model"""
    alert_id: str
    sensor_id: str
    alert_type: str
    severity: str = "warning"  # info, warning, critical
    message: str
    value: float
    threshold: float
    timestamp: datetime = Field(default_factory=datetime.now)
    acknowledged: bool = False


class Statistics(BaseModel):
    """Statistics model"""
    sensor_type: str
    count: int
    mean: float
    std: float
    min: float
    max: float
    median: float
    q25: float
    q75: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    databases: Dict[str, str]
    models_loaded: int


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str
    timestamp: datetime = Field(default_factory=datetime.now)


# Request/Response models for specific endpoints
class SensorListResponse(BaseModel):
    """Sensor list response"""
    sensors: List[Sensor]
    total: int


class ObservationListResponse(BaseModel):
    """Observation list response"""
    observations: List[SensorData]
    total: int


class ModelInfo(BaseModel):
    """Model information"""
    model_name: str
    model_type: str
    task_type: str
    metrics: Dict[str, Any]
    training_time: float
    file_path: str


class ModelListResponse(BaseModel):
    """Model list response"""
    models: List[ModelInfo]
    total: int


class TimeSeriesData(BaseModel):
    """Time series data point"""
    timestamp: datetime
    value: float
    sensor_id: str


class TimeSeriesResponse(BaseModel):
    """Time series response"""
    sensor_type: str
    data: List[TimeSeriesData]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None