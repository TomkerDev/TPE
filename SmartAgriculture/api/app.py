"""
FastAPI Application for Smart Agriculture Platform
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic
import logging
from datetime import datetime

from .routes import router as api_router
from .auth import get_current_active_user, require_admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Smart Agriculture API",
    description="REST API for Smart Agriculture IoT Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

# Security
security = HTTPBasic()


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Agriculture Platform API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    try:
        from .database import get_db
        from .prediction import get_prediction_engine
        
        db = get_db()
        engine = get_prediction_engine()
        
        # Check databases
        databases = {}
        
        try:
            from .database import get_sensors
            sensors = get_sensors()
            databases['postgresql'] = 'connected'
        except Exception as e:
            databases['postgresql'] = f'error: {str(e)}'
        
        try:
            from .database import get_observations
            obs = get_observations(limit=1)
            databases['timescaledb'] = 'connected'
        except Exception as e:
            databases['timescaledb'] = f'error: {str(e)}'
        
        # Check models
        models = engine.get_available_models()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "databases": databases,
            "models_loaded": len(models),
            "models": [m['model_name'] for m in models]
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@app.get("/protected", tags=["Protected"])
async def protected_route(current_user: dict = Depends(get_current_active_user)):
    """Example protected route requiring authentication"""
    return {
        "message": "This is a protected route",
        "user": current_user['username'],
        "role": current_user['role']
    }


@app.get("/admin", tags=["Admin"])
async def admin_route(current_user: dict = Depends(require_admin)):
    """Example admin-only route"""
    return {
        "message": "This is an admin-only route",
        "user": current_user['username'],
        "role": current_user['role']
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("="*80)
    logger.info("Smart Agriculture API Starting")
    logger.info("="*80)
    logger.info(f"Startup time: {datetime.now().isoformat()}")
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("="*80)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("="*80)
    logger.info("Smart Agriculture API Shutting Down")
    logger.info("="*80)
    
    try:
        from .database import get_db
        db = get_db()
        db.close()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


if __name__ == "__main__":
    import uvicorn
    
    print("Starting Smart Agriculture API...")
    print("="*80)
    print("API Documentation: http://localhost:8000/docs")
    print("Alternative docs: http://localhost:8000/redoc")
    print("="*80)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )