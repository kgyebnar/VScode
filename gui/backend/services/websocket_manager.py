"""
WebSocket manager for real-time updates
"""

import logging
import json
from typing import Set, Dict, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manage WebSocket connections for real-time updates"""

    def __init__(self):
        # Track active connections per session
        self.active_connections: Dict[str, Set] = defaultdict(set)

    async def connect(self, session_id: str, websocket):
        """Register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[session_id].add(websocket)
        logger.info(f"WebSocket connected to session {session_id}")

    def disconnect(self, session_id: str, websocket):
        """Unregister a WebSocket connection"""
        if websocket in self.active_connections.get(session_id, set()):
            self.active_connections[session_id].remove(websocket)
            logger.info(f"WebSocket disconnected from session {session_id}")

    async def broadcast(self, session_id: str, message: Dict[str, Any]):
        """Broadcast message to all connected clients for a session"""
        try:
            message_json = json.dumps(message)
            disconnected = set()

            for connection in self.active_connections.get(session_id, set()):
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error sending to WebSocket: {e}")
                    disconnected.add(connection)

            # Remove disconnected clients
            for connection in disconnected:
                self.disconnect(session_id, connection)

        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")

    async def broadcast_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients across all sessions"""
        try:
            message_json = json.dumps(message)
            disconnected_sessions = defaultdict(set)

            for session_id, connections in self.active_connections.items():
                for connection in connections:
                    try:
                        await connection.send_text(message_json)
                    except Exception as e:
                        logger.error(f"Error sending to WebSocket: {e}")
                        disconnected_sessions[session_id].add(connection)

            # Remove disconnected clients
            for session_id, connections in disconnected_sessions.items():
                for connection in connections:
                    self.disconnect(session_id, connection)

        except Exception as e:
            logger.error(f"Error broadcasting to all: {e}")

    def get_connection_count(self, session_id: Optional[str] = None) -> int:
        """Get number of active connections"""
        if session_id:
            return len(self.active_connections.get(session_id, set()))
        return sum(len(conns) for conns in self.active_connections.values())


# Global instance
ws_manager = WebSocketManager()
