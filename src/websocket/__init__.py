"""
WebSocket package for real-time notifications
"""
from .manager import ConnectionManager, manager, get_websocket_client

__all__ = ["ConnectionManager", "manager", "get_websocket_client"]
