# backend/app/api/v1/api.py
"""
Main API router that combines all endpoint routers
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, pets, tasks, metrics, websocket

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    pets.router,
    prefix="/pets",
    tags=["Pets"]
)

api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Tasks"]
)

api_router.include_router(
    metrics.router,
    prefix="/metrics",
    tags=["Pet Metrics"]
)

api_router.include_router(
    websocket.router,
    prefix="/ws",
    tags=["WebSocket"]
)