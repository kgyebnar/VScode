"""
WebSocket endpoint for real-time session updates
"""

from fastapi import APIRouter, WebSocket, Depends, HTTPException
from sqlalchemy.orm import Session
import asyncio
import json
from datetime import datetime

from database import get_db
from models import UpgradeSession, AuditLogEntry
from services.websocket_manager import ws_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/sessions/{session_id}")
async def websocket_session_updates(websocket: WebSocket, session_id: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time session updates

    Streams:
    - Session status changes
    - Firewall status updates
    - Audit log entries
    - Process status
    """
    try:
        # Verify session exists
        session = db.query(UpgradeSession).filter(
            UpgradeSession.session_id == session_id
        ).first()

        if not session:
            await websocket.close(code=1008, reason="Session not found")
            return

        # Connect client
        await ws_manager.connect(session_id, websocket)

        # Send initial session state
        initial_message = {
            "type": "session_connected",
            "session_id": session_id,
            "status": session.status,
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_json(initial_message)

        # Listen for messages (client can send ping or requests)
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                message = json.loads(data)

                # Handle client messages
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})

            except asyncio.TimeoutError:
                # Send keep-alive ping
                try:
                    await websocket.send_json({"type": "keep_alive"})
                except:
                    break

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        ws_manager.disconnect(session_id, websocket)
