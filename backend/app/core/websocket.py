# backend/app/core/websocket.py
"""
WebSocket connection manager for real-time updates
Handles pet metric updates, task completions, and multi-user synchronization
"""

from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class MessageType(str, Enum):
    """WebSocket message types"""
    # Connection
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    HEARTBEAT = "heartbeat"
    
    # Pet updates
    PET_METRICS_UPDATE = "pet_metrics_update"
    PET_STATE_CHANGE = "pet_state_change"
    PET_FEED = "pet_feed"
    PET_PLAY = "pet_play"
    
    # Task updates
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    TASK_ASSIGNED = "task_assigned"
    
    # User actions
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    USER_ONLINE = "user_online"
    
    # Currency
    CURRENCY_UPDATE = "currency_update"
    TRANSACTION = "transaction"
    
    # Notifications
    NOTIFICATION = "notification"
    ALERT = "alert"
    
    # Chat
    MESSAGE = "message"

class ConnectionManager:
    """
    Manages WebSocket connections for real-time communication
    """
    
    def __init__(self):
        # Store active connections by client_id
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Store pet rooms (multiple users can be in same pet room)
        self.pet_rooms: Dict[str, Set[str]] = {}  # pet_id -> set of client_ids
        
        # Store user -> pet mapping
        self.user_pets: Dict[str, str] = {}  # client_id -> pet_id
        
        # Heartbeat tracking
        self.last_heartbeat: Dict[str, datetime] = {}
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
    
    async def startup(self):
        """Initialize the WebSocket manager"""
        logger.info("WebSocket manager starting up...")
        # Start heartbeat checker
        task = asyncio.create_task(self._heartbeat_checker())
        self.background_tasks.append(task)
    
    async def shutdown(self):
        """Cleanup on shutdown"""
        logger.info("WebSocket manager shutting down...")
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Close all connections
        for client_id in list(self.active_connections.keys()):
            await self.disconnect(client_id)
    
    async def connect(self, websocket: WebSocket, client_id: str, pet_id: Optional[str] = None):
        """
        Accept a new WebSocket connection
        
        Args:
            websocket: The WebSocket connection
            client_id: Unique identifier for the client (usually user_id)
            pet_id: Optional pet_id to join a pet room
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.last_heartbeat[client_id] = datetime.now()
        
        # Join pet room if specified
        if pet_id:
            await self.join_pet_room(client_id, pet_id)
        
        # Send connection confirmation
        await self.send_personal_message(
            client_id,
            {
                "type": MessageType.CONNECT,
                "message": "Connected successfully",
                "client_id": client_id,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        logger.info(f"Client {client_id} connected")
    
    async def disconnect(self, client_id: str):
        """
        Handle client disconnection
        
        Args:
            client_id: The client to disconnect
        """
        if client_id in self.active_connections:
            # Leave pet room
            if client_id in self.user_pets:
                pet_id = self.user_pets[client_id]
                await self.leave_pet_room(client_id, pet_id)
            
            # Remove from tracking
            del self.active_connections[client_id]
            if client_id in self.last_heartbeat:
                del self.last_heartbeat[client_id]
            
            logger.info(f"Client {client_id} disconnected")
    
    async def join_pet_room(self, client_id: str, pet_id: str):
        """
        Add a client to a pet room for synchronized updates
        
        Args:
            client_id: The client joining the room
            pet_id: The pet room to join
        """
        if pet_id not in self.pet_rooms:
            self.pet_rooms[pet_id] = set()
        
        self.pet_rooms[pet_id].add(client_id)
        self.user_pets[client_id] = pet_id
        
        # Notify other users in the room
        await self.broadcast_to_pet(
            pet_id,
            {
                "type": MessageType.USER_JOINED,
                "user_id": client_id,
                "pet_id": pet_id,
                "timestamp": datetime.now().isoformat()
            },
            exclude=[client_id]
        )
        
        logger.info(f"Client {client_id} joined pet room {pet_id}")
    
    async def leave_pet_room(self, client_id: str, pet_id: str):
        """
        Remove a client from a pet room
        
        Args:
            client_id: The client leaving the room
            pet_id: The pet room to leave
        """
        if pet_id in self.pet_rooms and client_id in self.pet_rooms[pet_id]:
            self.pet_rooms[pet_id].remove(client_id)
            
            # Clean up empty rooms
            if not self.pet_rooms[pet_id]:
                del self.pet_rooms[pet_id]
            
            # Notify other users
            await self.broadcast_to_pet(
                pet_id,
                {
                    "type": MessageType.USER_LEFT,
                    "user_id": client_id,
                    "pet_id": pet_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        if client_id in self.user_pets:
            del self.user_pets[client_id]
        
        logger.info(f"Client {client_id} left pet room {pet_id}")
    
    async def send_personal_message(self, client_id: str, message: Dict[str, Any]):
        """
        Send a message to a specific client
        
        Args:
            client_id: The target client
            message: The message to send (will be JSON encoded)
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                await self.disconnect(client_id)
    
    async def broadcast(self, message: Dict[str, Any], exclude: List[str] = None):
        """
        Broadcast a message to all connected clients
        
        Args:
            message: The message to broadcast
            exclude: List of client_ids to exclude from broadcast
        """
        exclude = exclude or []
        disconnected = []
        
        for client_id, connection in self.active_connections.items():
            if client_id not in exclude:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            await self.disconnect(client_id)
    
    async def broadcast_to_pet(self, pet_id: str, message: Dict[str, Any], exclude: List[str] = None):
        """
        Broadcast a message to all users in a pet room
        
        Args:
            pet_id: The pet room to broadcast to
            message: The message to broadcast
            exclude: List of client_ids to exclude
        """
        exclude = exclude or []
        
        if pet_id in self.pet_rooms:
            for client_id in self.pet_rooms[pet_id]:
                if client_id not in exclude:
                    await self.send_personal_message(client_id, message)
    
    async def send_pet_metrics_update(self, pet_id: str, metrics: Dict[str, Any]):
        """
        Send pet metrics update to all users caring for the pet
        
        Args:
            pet_id: The pet whose metrics updated
            metrics: The updated metrics
        """
        message = {
            "type": MessageType.PET_METRICS_UPDATE,
            "pet_id": pet_id,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_to_pet(pet_id, message)
    
    async def send_task_update(self, pet_id: str, task_type: MessageType, task_data: Dict[str, Any]):
        """
        Send task-related updates to pet room
        
        Args:
            pet_id: The pet associated with the task
            task_type: Type of task update
            task_data: Task information
        """
        message = {
            "type": task_type,
            "pet_id": pet_id,
            "task": task_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_to_pet(pet_id, message)
    
    async def send_notification(self, client_id: str, notification: Dict[str, Any], priority: str = "normal"):
        """
        Send a notification to a specific user
        
        Args:
            client_id: The target client
            notification: Notification content
            priority: Notification priority (low, normal, high, critical)
        """
        message = {
            "type": MessageType.NOTIFICATION if priority != "critical" else MessageType.ALERT,
            "notification": notification,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(client_id, message)
    
    def active_connections_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
    
    def get_pet_room_users(self, pet_id: str) -> List[str]:
        """Get list of users in a pet room"""
        return list(self.pet_rooms.get(pet_id, set()))
    
    def get_online_users(self) -> List[str]:
        """Get list of all online users"""
        return list(self.active_connections.keys())
    
    async def _heartbeat_checker(self):
        """
        Background task to check client heartbeats and remove stale connections
        """
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                now = datetime.now()
                stale_clients = []
                
                for client_id, last_beat in self.last_heartbeat.items():
                    # If no heartbeat for 60 seconds, consider stale
                    if (now - last_beat).total_seconds() > 60:
                        stale_clients.append(client_id)
                
                # Disconnect stale clients
                for client_id in stale_clients:
                    logger.warning(f"Client {client_id} heartbeat timeout")
                    await self.disconnect(client_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat checker: {e}")
    
    async def handle_heartbeat(self, client_id: str):
        """Update heartbeat timestamp for a client"""
        if client_id in self.active_connections:
            self.last_heartbeat[client_id] = datetime.now()
            await self.send_personal_message(
                client_id,
                {"type": MessageType.HEARTBEAT, "status": "alive"}
            )

# Create global WebSocket manager instance
websocket_manager = ConnectionManager()