"""
WebSocket Manager for real-time notifications
"""
from typing import Dict, Set, Optional
import logging
import json
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates
    """
    
    def __init__(self):
        """Initialize connection manager"""
        # Active connections: {user_id: Set[WebSocket]}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Job-specific connections: {job_id: Set[WebSocket]}
        self.job_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None, job_id: str = None):
        """
        Accept new WebSocket connection
        
        Args:
            websocket: WebSocket connection
            user_id: Optional user identifier
            job_id: Optional job identifier for job-specific updates
        """
        await websocket.accept()
        
        if user_id:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)
            logger.info(f"WebSocket connected for user: {user_id}")
        
        if job_id:
            if job_id not in self.job_connections:
                self.job_connections[job_id] = set()
            self.job_connections[job_id].add(websocket)
            logger.info(f"WebSocket connected for job: {job_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str = None, job_id: str = None):
        """
        Remove WebSocket connection
        
        Args:
            websocket: WebSocket connection to remove
            user_id: Optional user identifier
            job_id: Optional job identifier
        """
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected for user: {user_id}")
        
        if job_id and job_id in self.job_connections:
            self.job_connections[job_id].discard(websocket)
            if not self.job_connections[job_id]:
                del self.job_connections[job_id]
            logger.info(f"WebSocket disconnected for job: {job_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send message to specific WebSocket
        
        Args:
            message: Message to send
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
    
    async def send_to_user(self, message: dict, user_id: str):
        """
        Send message to all connections for a user
        
        Args:
            message: Message to send
            user_id: Target user identifier
        """
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.active_connections[user_id].discard(connection)
    
    async def send_to_job(self, message: dict, job_id: str):
        """
        Send message to all connections watching a specific job
        
        Args:
            message: Message to send
            job_id: Target job identifier
        """
        if job_id in self.job_connections:
            disconnected = []
            for connection in self.job_connections[job_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to job {job_id}: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.job_connections[job_id].discard(connection)
    
    async def broadcast(self, message: dict):
        """
        Broadcast message to all active connections
        
        Args:
            message: Message to broadcast
        """
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting message: {e}")
    
    async def send_progress_update(self, job_id: str, progress: float, phase: str, message: str = None):
        """
        Send progress update for a job
        
        Args:
            job_id: Job identifier
            progress: Progress percentage (0-100)
            phase: Current phase description
            message: Optional additional message
        """
        update_message = {
            "type": "progress_update",
            "job_id": job_id,
            "progress": progress,
            "phase": phase,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await self.send_to_job(update_message, job_id)
    
    async def send_completion_notification(self, job_id: str, biography_id: int, success: bool = True):
        """
        Send job completion notification
        
        Args:
            job_id: Job identifier
            biography_id: Biography ID
            success: Whether job completed successfully
        """
        completion_message = {
            "type": "completion",
            "job_id": job_id,
            "biography_id": biography_id,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await self.send_to_job(completion_message, job_id)
    
    async def send_error_alert(self, job_id: str, error: str, severity: str = "error"):
        """
        Send error alert
        
        Args:
            job_id: Job identifier
            error: Error message
            severity: Error severity (error, warning, critical)
        """
        error_message = {
            "type": "error_alert",
            "job_id": job_id,
            "error": error,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await self.send_to_job(error_message, job_id)
    
    def get_connection_count(self) -> dict:
        """
        Get current connection statistics
        
        Returns:
            Dictionary with connection counts
        """
        return {
            "total_users": len(self.active_connections),
            "total_user_connections": sum(len(conns) for conns in self.active_connections.values()),
            "total_jobs": len(self.job_connections),
            "total_job_connections": sum(len(conns) for conns in self.job_connections.values()),
        }
    
    def is_connected(self, user_id: str = None, job_id: str = None) -> bool:
        """
        Check if there are active connections
        
        Args:
            user_id: Optional user identifier to check
            job_id: Optional job identifier to check
        
        Returns:
            True if connections exist, False otherwise
        """
        if user_id:
            return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
        if job_id:
            return job_id in self.job_connections and len(self.job_connections[job_id]) > 0
        return len(self.active_connections) > 0 or len(self.job_connections) > 0


# Global connection manager instance
manager = ConnectionManager()


def get_websocket_client() -> ConnectionManager:
    """
    Get the global WebSocket connection manager
    
    Returns:
        ConnectionManager instance
    """
    return manager
