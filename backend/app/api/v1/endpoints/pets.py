# backend/app/api/v1/endpoints/pets.py
"""
Pet management endpoints
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user
from app.core.websocket import websocket_manager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Pydantic models
class PetCreate(BaseModel):
    """Schema for creating a new pet"""
    name: str = Field(..., min_length=1, max_length=50)
    sprite_id: Optional[int] = 1  # Default sprite
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Whiskers",
                "sprite_id": 1
            }
        }

class PetMetrics(BaseModel):
    """Pet metrics schema"""
    happiness: int = Field(ge=0, le=100, default=50)
    hunger: int = Field(ge=0, le=100, default=50)
    health: int = Field(ge=0, le=100, default=50)
    energy: int = Field(ge=0, le=100, default=50)
    currency: int = Field(ge=0, default=50)

class PetResponse(BaseModel):
    """Pet response schema"""
    id: int
    name: str
    sprite_id: int
    created_at: datetime
    created_by: int
    metrics: PetMetrics
    owners: List[Dict[str, Any]]
    is_sleeping: bool = False

class PetInvite(BaseModel):
    """Schema for inviting users to co-own a pet"""
    user_email: str = Field(..., description="Email of user to invite")
    role: str = Field(default="co-owner", description="Role for the invited user")

class FeedPet(BaseModel):
    """Schema for feeding a pet"""
    food_item: str = Field(default="catnip", description="Food item to give")
    
class PetAction(BaseModel):
    """Schema for pet interactions"""
    action: str = Field(..., description="Action to perform (pet, play, sleep)")

# Endpoints
@router.post("/", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
async def create_pet(
    pet_data: PetCreate,
    current_user: Dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new pet
    
    - **name**: Pet's name
    - **sprite_id**: Visual appearance ID
    """
    try:
        # Mock pet creation
        new_pet = {
            "id": 1,
            "name": pet_data.name,
            "sprite_id": pet_data.sprite_id,
            "created_at": datetime.utcnow(),
            "created_by": current_user["id"],
            "metrics": {
                "happiness": 50,
                "hunger": 50,
                "health": 100,
                "energy": 100,
                "currency": 50
            },
            "owners": [{
                "user_id": current_user["id"],
                "email": current_user["email"],
                "role": "owner",
                "joined_at": datetime.utcnow().isoformat()
            }],
            "is_sleeping": False
        }
        
        logger.info(f"User {current_user['id']} created pet: {pet_data.name}")
        
        # Send WebSocket notification
        await websocket_manager.broadcast(
            {
                "type": "PET_CREATED",
                "pet": new_pet,
                "created_by": current_user["email"]
            }
        )
        
        return new_pet
        
    except Exception as e:
        logger.error(f"Error creating pet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create pet"
        )

@router.get("/", response_model=List[PetResponse])
async def get_user_pets(
    current_user: Dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all pets owned or co-owned by the current user
    """
    try:
        # Mock response
        pets = [{
            "id": 1,
            "name": "Whiskers",
            "sprite_id": 1,
            "created_at": datetime.utcnow(),
            "created_by": current_user["id"],
            "metrics": {
                "happiness": 75,
                "hunger": 40,
                "health": 90,
                "energy": 60,
                "currency": 125
            },
            "owners": [{
                "user_id": current_user["id"],
                "email": current_user["email"],
                "role": "owner",
                "joined_at": datetime.utcnow().isoformat()
            }],
            "is_sleeping": False
        }]
        
        return pets
        
    except Exception as e:
        logger.error(f"Error fetching pets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pets"
        )

@router.get("/{pet_id}", response_model=PetResponse)
async def get_pet(
    pet_id: int,
    current_user: Dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific pet by ID
    """
    try:
        # Mock response
        # In production, verify user has access to this pet
        pet = {
            "id": pet_id,
            "name": "Whiskers",
            "sprite_id": 1,
            "created_at": datetime.utcnow(),
            "created_by": 1,
            "metrics": {
                "happiness": 75,
                "hunger": 40,
                "health": 90,
                "energy": 60,
                "currency": 125
            },
            "owners": [{
                "user_id": current_user["id"],
                "email": current_user["email"],
                "role": "owner",
                "joined_at": datetime.utcnow().isoformat()
            }],
            "is_sleeping": False
        }
        
        return pet
        
    except Exception as e:
        logger.error(f"Error fetching pet {pet_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )

@router.post("/{pet_id}/feed", response_model=Dict[str, Any])
async def feed_pet(
    pet_id: int,
    feed_data: FeedPet,
    current_user: Dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Feed a pet with food items
    
    - Catnip costs 10 currency
    - Increases happiness and decreases hunger
    """
    try:
        # Mock feeding logic
        food_effects = {
            "catnip": {
                "happiness": 20,
                "hunger": -30,
                "energy": 10,
                "cost": 10
            }
        }
        
        effect = food_effects.get(feed_data.food_item, food_effects["catnip"])
        
        # Update metrics (mock)
        new_metrics = {
            "happiness": min(100, 75 + effect["happiness"]),
            "hunger": max(0, 40 + effect["hunger"]),
            "health": 90,
            "energy": min(100, 60 + effect["energy"]),
            "currency": 125 - effect["cost"]
        }
        
        # Send WebSocket update
        await websocket_manager.send_pet_metrics_update(
            str(pet_id),
            new_metrics
        )
        
        return {
            "success": True,
            "message": f"Fed {feed_data.food_item} to pet",
            "new_metrics": new_metrics,
            "cost": effect["cost"]
        }
        
    except Exception as e:
        logger.error(f"Error feeding pet {pet_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to feed pet"
        )

@router.post("/{pet_id}/interact", response_model=Dict[str, Any])
async def interact_with_pet(
    pet_id: int,
    action_data: PetAction,
    current_user: Dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Interact with a pet (pet, play, make sleep)
    
    - **pet**: Increases happiness by 5
    - **play**: Increases happiness, decreases energy
    - **sleep**: Pet sleeps to restore energy
    """
    try:
        action_effects = {
            "pet": {"happiness": 5, "energy": 0},
            "play": {"happiness": 10, "energy": -15},
            "sleep": {"energy": 50, "happiness": 0}
        }
        
        effect = action_effects.get(action_data.action, {"happiness": 0, "energy": 0})
        
        # Mock metric update
        result = {
            "success": True,
            "action": action_data.action,
            "message": f"You {action_data.action} the pet!",
            "effect": effect,
            "animation": action_data.action  # Trigger animation on frontend
        }
        
        # Send WebSocket notification for pet interaction
        await websocket_manager.broadcast_to_pet(
            str(pet_id),
            {
                "type": "PET_INTERACTION",
                "user": current_user["email"],
                "action": action_data.action,
                "effect": effect
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error interacting with pet {pet_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to interact with pet"
        )

@router.post("/{pet_id}/invite", response_model=Dict[str, Any])
async def invite_co_owner(
    pet_id: int,
    invite_data: PetInvite,
    current_user: Dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Invite another user to co-own a pet
    
    Only the pet owner can invite others
    """
    try:
        # In production:
        # 1. Verify current user is the owner
        # 2. Check if invited user exists
        # 3. Send invitation (email or in-app notification)
        # 4. Create pending invitation record
        
        result = {
            "success": True,
            "message": f"Invitation sent to {invite_data.user_email}",
            "pet_id": pet_id,
            "invited_user": invite_data.user_email,
            "role": invite_data.role,
            "status": "pending"
        }
        
        logger.info(f"User {current_user['id']} invited {invite_data.user_email} to pet {pet_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error inviting co-owner: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send invitation"
        )

@router.delete("/{pet_id}/owners/{user_id}", response_model=Dict[str, Any])
async def remove_co_owner(
    pet_id: int,
    user_id: int,
    current_user: Dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove a co-owner from a pet
    
    Only the pet owner can remove co-owners
    """
    try:
        # In production, verify permissions and remove user
        
        result = {
            "success": True,
            "message": f"User {user_id} removed from pet {pet_id}",
            "pet_id": pet_id,
            "removed_user_id": user_id
        }
        
        # Notify via WebSocket
        await websocket_manager.broadcast_to_pet(
            str(pet_id),
            {
                "type": "OWNER_REMOVED",
                "removed_user_id": user_id,
                "removed_by": current_user["email"]
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error removing co-owner: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove co-owner"
        )

@router.get("/{pet_id}/metrics/history", response_model=List[Dict[str, Any]])
async def get_metrics_history(
    pet_id: int,
    hours: int = Query(default=24, description="Hours of history to retrieve"),
    current_user: Dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get historical metrics for a pet
    
    Useful for charts and tracking pet health over time
    """
    try:
        # Mock historical data
        import random
        from datetime import timedelta
        
        history = []
        base_time = datetime.utcnow()
        
        for i in range(hours):
            history.append({
                "timestamp": (base_time - timedelta(hours=i)).isoformat(),
                "metrics": {
                    "happiness": random.randint(40, 90),
                    "hunger": random.randint(20, 80),
                    "health": random.randint(60, 100),
                    "energy": random.randint(30, 100),
                    "currency": 125 + random.randint(-20, 20)
                }
            })
        
        return history
        
    except Exception as e:
        logger.error(f"Error fetching metrics history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch metrics history"
        )