"""
API Routes for Smart Agriculture Platform
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from .database import get_db, execute_query, get_sensors, get_observations, get_sensor_data
from .models import (
    Sensor, SensorData, PredictionRequest, PredictionResponse,
    Alert, Statistics, HealthResponse, SensorListResponse,
    ObservationListResponse, TimeSeriesResponse
)
from .prediction import get_prediction_engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/", tags=["Health"])
async def home():
    """API home endpoint"""
    return {
        "message": "Smart Agriculture Platform API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "sensors": "/sensors",
            "observations": "/observations",
            "predict": "/predict",
            "health": "/health"
        }
    }


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        db = get_db()
        
        # Check database connections
        databases = {}
        
        try:
            sensors = get_sensors()
            databases['postgresql'] = 'connected'
        except:
            databases['postgresql'] = 'disconnected'
        
        try:
            observations = get_observations(limit=1)
            databases['timescaledb'] = 'connected'
        except:
            databases['timescaledb'] = 'disconnected'
        
        # Check models
        engine = get_prediction_engine()
        models_loaded = len(engine.get_available_models())
        
        return HealthResponse(
            status="healthy",
            databases=databases,
            models_loaded=models_loaded
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Sensor endpoints
@router.get("/sensors", response_model=SensorListResponse, tags=["Sensors"])
async def get_all_sensors():
    """Get list of all sensors"""
    try:
        sensors_data = get_sensors()
        
        sensors = [Sensor(**sensor) for sensor in sensors_data]
        
        return SensorListResponse(
            sensors=sensors,
            total=len(sensors)
        )
        
    except Exception as e:
        logger.error(f"Failed to get sensors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sensors/{sensor_id}", tags=["Sensors"])
async def get_sensor(sensor_id: str):
    """Get specific sensor information"""
    try:
        query = "SELECT * FROM sensors WHERE sensor_id = :sensor_id"
        results = execute_query(query, {'sensor_id': sensor_id})
        
        if not results:
            raise HTTPException(status_code=404, detail="Sensor not found")
        
        return results[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sensor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sensors/type/{sensor_type}", tags=["Sensors"])
async def get_sensors_by_type(sensor_type: str):
    """Get sensors by type"""
    try:
        query = "SELECT * FROM sensors WHERE sensor_type = :sensor_type"
        results = execute_query(query, {'sensor_type': sensor_type})
        
        return {
            'sensor_type': sensor_type,
            'sensors': results,
            'total': len(results)
        }
        
    except Exception as e:
        logger.error(f"Failed to get sensors by type: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Observation endpoints
@router.get("/observations", response_model=ObservationListResponse, tags=["Observations"])
async def get_observations_endpoint(
    limit: int = Query(100, ge=1, le=1000),
    sensor_type: Optional[str] = None
):
    """Get latest observations"""
    try:
        if sensor_type:
            query = """
            SELECT * FROM sensor_data 
            WHERE sensor_type = :sensor_type
            ORDER BY timestamp DESC 
            LIMIT :limit
            """
            params = {'sensor_type': sensor_type, 'limit': limit}
        else:
            query = """
            SELECT * FROM sensor_data 
            ORDER BY timestamp DESC 
            LIMIT :limit
            """
            params = {'limit': limit}
        
        results = execute_query(query, params)
        
        observations = [SensorData(**obs) for obs in results]
        
        return ObservationListResponse(
            observations=observations,
            total=len(observations)
        )
        
    except Exception as e:
        logger.error(f"Failed to get observations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/observations/sensor/{sensor_id}", tags=["Observations"])
async def get_sensor_observations(
    sensor_id: str,
    limit: int = Query(100, ge=1, le=1000),
    hours: Optional[int] = None
):
    """Get observations for a specific sensor"""
    try:
        if hours:
            start_time = datetime.now() - timedelta(hours=hours)
            query = """
            SELECT * FROM sensor_data 
            WHERE sensor_id = :sensor_id AND timestamp >= :start_time
            ORDER BY timestamp DESC 
            LIMIT :limit
            """
            params = {'sensor_id': sensor_id, 'start_time': start_time, 'limit': limit}
        else:
            query = """
            SELECT * FROM sensor_data 
            WHERE sensor_id = :sensor_id
            ORDER BY timestamp DESC 
            LIMIT :limit
            """
            params = {'sensor_id': sensor_id, 'limit': limit}
        
        results = execute_query(query, params)
        
        return {
            'sensor_id': sensor_id,
            'observations': results,
            'total': len(results)
        }
        
    except Exception as e:
        logger.error(f"Failed to get sensor observations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/observations/latest", tags=["Observations"])
async def get_latest_observations():
    """Get latest observation for each sensor"""
    try:
        query = """
        SELECT DISTINCT ON (sensor_id) 
            sensor_id, sensor_type, value, unit, timestamp, location
        FROM sensor_data
        ORDER BY sensor_id, timestamp DESC
        """
        
        results = execute_query(query)
        
        return {
            'observations': results,
            'total': len(results)
        }
        
    except Exception as e:
        logger.error(f"Failed to get latest observations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Time series endpoints
@router.get("/timeseries/{sensor_type}", response_model=TimeSeriesResponse, tags=["Time Series"])
async def get_time_series(
    sensor_type: str,
    hours: int = Query(24, ge=1, le=720),
    limit: int = Query(1000, ge=1, le=10000)
):
    """Get time series data for a sensor type"""
    try:
        start_time = datetime.now() - timedelta(hours=hours)
        
        query = """
        SELECT timestamp, value, sensor_id
        FROM sensor_data
        WHERE sensor_type = :sensor_type AND timestamp >= :start_time
        ORDER BY timestamp ASC
        LIMIT :limit
        """
        
        params = {
            'sensor_type': sensor_type,
            'start_time': start_time,
            'limit': limit
        }
        
        results = execute_query(query, params)
        
        return TimeSeriesResponse(
            sensor_type=sensor_type,
            data=[TimeSeriesData(**r) for r in results],
            start_time=start_time,
            end_time=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Failed to get time series: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Statistics endpoints
@router.get("/statistics/{sensor_type}", response_model=Statistics, tags=["Statistics"])
async def get_statistics(sensor_type: str, hours: int = Query(24, ge=1, le=720)):
    """Get statistics for a sensor type"""
    try:
        start_time = datetime.now() - timedelta(hours=hours)
        
        query = """
        SELECT 
            COUNT(*) as count,
            AVG(value) as mean,
            STDDEV(value) as std,
            MIN(value) as min,
            MAX(value) as max,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY value) as median,
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY value) as q25,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY value) as q75
        FROM sensor_data
        WHERE sensor_type = :sensor_type AND timestamp >= :start_time
        """
        
        params = {
            'sensor_type': sensor_type,
            'start_time': start_time
        }
        
        results = execute_query(query, params)
        
        if not results:
            raise HTTPException(status_code=404, detail="No data found")
        
        stats = results[0]
        
        return Statistics(
            sensor_type=sensor_type,
            count=int(stats['count']),
            mean=float(stats['mean']),
            std=float(stats['std']),
            min=float(stats['min']),
            max=float(stats['max']),
            median=float(stats['median']),
            q25=float(stats['q25']),
            q75=float(stats['q75'])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Prediction endpoints
@router.post("/predict", response_model=PredictionResponse, tags=["AI Prediction"])
async def predict(request: PredictionRequest):
    """Make AI prediction"""
    try:
        engine = get_prediction_engine()
        
        result = engine.predict(
            model_name=request.model_type,
            features=request.features,
            return_probabilities=True
        )
        
        return PredictionResponse(
            prediction=result['prediction'],
            confidence=result.get('confidence'),
            model_used=result['model_used'],
            timestamp=datetime.fromisoformat(result['timestamp'])
        )
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/best", response_model=PredictionResponse, tags=["AI Prediction"])
async def predict_with_best_model(
    features: List[float],
    task_type: str = "classification"
):
    """Make prediction using the best available model"""
    try:
        engine = get_prediction_engine()
        
        result = engine.predict_with_best_model(
            features=features,
            task_type=task_type,
            return_probabilities=True
        )
        
        return PredictionResponse(
            prediction=result['prediction'],
            confidence=result.get('confidence'),
            model_used=result['model_used'],
            timestamp=datetime.fromisoformat(result['timestamp'])
        )
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", tags=["AI Models"])
async def get_models():
    """Get list of available AI models"""
    try:
        engine = get_prediction_engine()
        models = engine.get_available_models()
        
        return {
            'models': models,
            'total': len(models)
        }
        
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_name}", tags=["AI Models"])
async def get_model_info(model_name: str):
    """Get information about a specific model"""
    try:
        engine = get_prediction_engine()
        info = engine.get_model_info(model_name)
        
        if not info:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Alert endpoints
@router.get("/alerts", tags=["Alerts"])
async def get_alerts(
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get alerts"""
    try:
        query = "SELECT * FROM alerts WHERE 1=1"
        params = {}
        
        if severity:
            query += " AND severity = :severity"
            params['severity'] = severity
        
        if acknowledged is not None:
            query += " AND acknowledged = :acknowledged"
            params['acknowledged'] = acknowledged
        
        query += " ORDER BY timestamp DESC LIMIT :limit"
        params['limit'] = limit
        
        results = execute_query(query, params)
        
        return {
            'alerts': [Alert(**a) for a in results],
            'total': len(results)
        }
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/acknowledge", tags=["Alerts"])
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    try:
        query = """
        UPDATE alerts 
        SET acknowledged = TRUE, acknowledged_at = :timestamp
        WHERE alert_id = :alert_id
        """
        
        params = {
            'alert_id': alert_id,
            'timestamp': datetime.now()
        }
        
        execute_query(query, params)
        
        return {"message": "Alert acknowledged", "alert_id": alert_id}
        
    except Exception as e:
        logger.error(f"Failed to acknowledge alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Data export endpoints
@router.get("/export/csv", tags=["Export"])
async def export_csv(
    sensor_type: Optional[str] = None,
    hours: int = Query(24, ge=1, le=720)
):
    """Export data as CSV"""
    try:
        import pandas as pd
        import io
        
        data = get_sensor_data(
            sensor_type=sensor_type,
            start_time=(datetime.now() - timedelta(hours=hours)).isoformat(),
            limit=10000
        )
        
        if not data:
            raise HTTPException(status_code=404, detail="No data found")
        
        df = pd.DataFrame(data)
        
        # Convert to CSV
        output = io.StringIO()
        df.to_csv(output, index=False)
        
        return {
            'csv': output.getvalue(),
            'rows': len(df),
            'columns': list(df.columns)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Test routes
    print("Testing API Routes...")
    print("="*80)
    
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    
    print("\n✓ Routes configured successfully!")
    print("\nAvailable endpoints:")
    for route in router.routes:
        print(f"  {route.methods} {route.path}")