"""
API endpoints for audit log retrieval and filtering
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import AuditLogEntry
from services.audit_logger import AuditLogger

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/sessions/{session_id}")
async def get_session_audit_log(
    session_id: str,
    limit: int = 1000,
    severity: str = None,
    event_type: str = None,
    firewall_id: str = None,
    db: Session = Depends(get_db)
) -> dict:
    """Get audit log entries for a session with optional filtering"""
    try:
        events = AuditLogger.get_events(
            db,
            session_id=session_id,
            firewall_id=firewall_id,
            event_type=event_type,
            severity=severity,
            limit=limit
        )

        return {
            "session_id": session_id,
            "total": len(events),
            "events": [
                {
                    "id": event.id,
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "phase": event.phase,
                    "severity": event.severity,
                    "firewall_id": event.firewall_id,
                    "message": event.message,
                    "details": event.details,
                }
                for event in events
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/summary")
async def get_session_summary(session_id: str, db: Session = Depends(get_db)) -> dict:
    """Get summary statistics for a session's audit log"""
    try:
        summary = AuditLogger.get_session_summary(db, session_id)
        return {
            "session_id": session_id,
            **summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/firewalls/{firewall_id}")
async def get_firewall_audit_log(
    firewall_id: str,
    limit: int = 500,
    db: Session = Depends(get_db)
) -> dict:
    """Get audit log entries for a specific firewall"""
    try:
        events = AuditLogger.get_events(
            db,
            firewall_id=firewall_id,
            limit=limit
        )

        return {
            "firewall_id": firewall_id,
            "total": len(events),
            "events": [
                {
                    "id": event.id,
                    "timestamp": event.timestamp.isoformat(),
                    "session_id": event.session_id,
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "message": event.message,
                }
                for event in events
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_type}")
async def get_events_by_type(
    event_type: str,
    limit: int = 500,
    db: Session = Depends(get_db)
) -> dict:
    """Get audit log entries of a specific type"""
    try:
        events = AuditLogger.get_events(
            db,
            event_type=event_type,
            limit=limit
        )

        return {
            "event_type": event_type,
            "total": len(events),
            "events": [
                {
                    "id": event.id,
                    "timestamp": event.timestamp.isoformat(),
                    "session_id": event.session_id,
                    "firewall_id": event.firewall_id,
                    "severity": event.severity,
                    "message": event.message,
                }
                for event in events
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
