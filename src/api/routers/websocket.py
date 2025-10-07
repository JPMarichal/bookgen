"""
WebSocket router for real-time notifications
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import logging
from src.websocket.manager import get_websocket_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    user_id: str = Query(None, description="User identifier"),
    job_id: str = Query(None, description="Job identifier to watch")
):
    """
    WebSocket endpoint for real-time notifications
    
    Connect to receive real-time updates about job progress, completions, and errors.
    
    Query Parameters:
    - user_id: Optional user identifier for user-specific notifications
    - job_id: Optional job ID to receive updates for a specific job
    
    Message Format (JSON):
    ```json
    {
        "type": "progress_update|completion|error_alert",
        "job_id": "123",
        "progress": 50.0,
        "phase": "Generating chapter 3",
        "message": "Optional message",
        "timestamp": "2024-01-01T12:00:00Z"
    }
    ```
    """
    manager = get_websocket_client()
    
    await manager.connect(websocket, user_id=user_id, job_id=job_id)
    
    try:
        # Send initial connection confirmation
        await manager.send_personal_message(
            {
                "type": "connection",
                "status": "connected",
                "user_id": user_id,
                "job_id": job_id,
                "message": "WebSocket connection established"
            },
            websocket
        )
        
        # Keep connection alive and handle incoming messages
        while True:
            # Receive messages from client (for ping/pong or other client requests)
            data = await websocket.receive_text()
            
            # Echo back or handle client requests
            if data == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id=user_id, job_id=job_id)
        logger.info(f"WebSocket disconnected: user_id={user_id}, job_id={job_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket, user_id=user_id, job_id=job_id)


@router.get("/status")
async def websocket_status():
    """
    Get WebSocket connection statistics
    
    Returns information about active WebSocket connections.
    """
    manager = get_websocket_client()
    stats = manager.get_connection_count()
    
    return {
        "status": "operational",
        "connections": stats
    }
