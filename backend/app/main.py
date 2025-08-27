# backend/app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🐱 Purretys API starting up...")
    logger.info("Database connections would be initialized here")
    yield
    # Shutdown
    logger.info("Purretys API shutting down...")
    logger.info("Cleanup tasks would run here")

# Create FastAPI instance
app = FastAPI(
    title="Purretys API",
    description="Backend API for the collaborative virtual pet care game",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS with simple origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint returning API information"""
    return {
        "message": "Welcome to Purretys API",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "ok",
        "service": "purretys-api",
        "database": "not_configured",
        "redis": "not_configured"
    }

# API v1 endpoints placeholder
@app.get("/api/v1/status", response_model=Dict[str, str])
async def api_status():
    """API v1 status endpoint"""
    return {
        "api_version": "v1",
        "status": "ready",
        "message": "API v1 is ready for implementation"
    }

# Test endpoint for frontend connection
@app.get("/api/v1/test", response_model=Dict[str, Any])
async def test_endpoint():
    """Test endpoint to verify frontend-backend connection"""
    return {
        "success": True,
        "message": "Backend is connected!",
        "data": {
            "test": "This is test data from the backend",
            "features": ["authentication", "pets", "tasks", "real-time updates"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)