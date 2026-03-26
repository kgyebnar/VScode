"""
API endpoints for session management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from database import get_db
from models import UpgradeSession, FirewallStatus
from services.audit_logger import AuditLogger
from services.playbook_executor import PlaybookExecutor
from utils.yaml_parser import InventoryParser

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

# Pydantic models for request/response
class SessionCreate(BaseModel):
    inventory_file: str
    target_firmware_version: str
    execution_mode: str = "sequential"
    extra_vars: Optional[dict] = None
    notes: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    inventory_file: str
    target_firmware_version: str
    total_firewalls: int
    execution_mode: str

    class Config:
        from_attributes = True


class SessionStartRequest(BaseModel):
    """Request to start an existing session"""
    pass


# Executor instance
executor = PlaybookExecutor()


@router.get("")
async def list_sessions(db: Session = Depends(get_db)) -> dict:
    """List all upgrade sessions"""
    try:
        sessions = db.query(UpgradeSession).order_by(UpgradeSession.created_at.desc()).all()
        return {
            "total": len(sessions),
            "sessions": [
                {
                    "session_id": s.session_id,
                    "status": s.status,
                    "created_at": s.created_at.isoformat(),
                    "started_at": s.started_at.isoformat() if s.started_at else None,
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                    "inventory_file": s.inventory_file,
                    "target_firmware_version": s.target_firmware_version,
                    "total_firewalls": s.total_firewalls,
                }
                for s in sessions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_session(req: SessionCreate, db: Session = Depends(get_db)) -> dict:
    """Create a new upgrade session"""
    try:
        # Parse inventory to get firewall list
        inventory_data = InventoryParser.parse_inventory(req.inventory_file)

        if "error" in inventory_data:
            raise HTTPException(status_code=404, detail=inventory_data["error"])

        # Create session
        session = UpgradeSession(
            target_firmware_version=req.target_firmware_version,
            execution_mode=req.execution_mode,
            total_firewalls=len(inventory_data["firewalls"]),
            inventory_file=req.inventory_file,
            extra_vars=req.extra_vars or {},
            notes=req.notes,
            status="pending"
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        # Create firewall status entries
        for fw in inventory_data["firewalls"]:
            fw_status = FirewallStatus(
                session_id=session.session_id,
                firewall_id=fw["firewall_id"],
                firewall_ip=fw["panos_ip"],
                firmware_version_target=fw.get("target_firmware_version", req.target_firmware_version),
                ha_enabled=fw.get("ha_enabled", False),
                ha_primary=fw.get("is_primary", False),
            )
            db.add(fw_status)

        db.commit()

        # Log event
        AuditLogger.log_event(
            db,
            session.session_id,
            "session_created",
            f"Upgrade session created with {len(inventory_data['firewalls'])} firewalls",
            severity="info"
        )

        return {
            "session_id": session.session_id,
            "status": session.status,
            "total_firewalls": session.total_firewalls,
            "inventory_file": session.inventory_file,
            "firewalls": inventory_data["firewalls"]
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
async def get_session(session_id: str, db: Session = Depends(get_db)) -> dict:
    """Get session details"""
    try:
        session = db.query(UpgradeSession).filter(UpgradeSession.session_id == session_id).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        firewalls = db.query(FirewallStatus).filter(FirewallStatus.session_id == session_id).all()

        return {
            "session_id": session.session_id,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "inventory_file": session.inventory_file,
            "target_firmware_version": session.target_firmware_version,
            "execution_mode": session.execution_mode,
            "total_firewalls": session.total_firewalls,
            "current_firewall_index": session.current_firewall_index,
            "firewalls": [
                {
                    "firewall_id": fw.firewall_id,
                    "status": fw.status,
                    "current_phase": fw.current_phase,
                    "progress_percent": fw.progress_percent,
                    "firewall_ip": fw.firewall_ip,
                    "firmware_version_current": fw.firmware_version_current,
                    "firmware_version_target": fw.firmware_version_target,
                }
                for fw in firewalls
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/start")
async def start_session(session_id: str, db: Session = Depends(get_db)) -> dict:
    """Start an upgrade session (trigger playbook)"""
    try:
        session = db.query(UpgradeSession).filter(UpgradeSession.session_id == session_id).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.status != "pending":
            raise HTTPException(status_code=400, detail=f"Cannot start session in {session.status} state")

        # Start playbook
        result = executor.start_upgrade(
            session_id=session_id,
            inventory_file=session.inventory_file,
            target_version=session.target_firmware_version,
            extra_vars=session.extra_vars
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        # Update session status
        session.status = "running"
        session.started_at = datetime.utcnow()
        db.commit()

        # Log event
        AuditLogger.log_event(
            db,
            session_id,
            "session_started",
            f"Upgrade session started (PID: {result.get('pid')})",
            severity="info"
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/pause")
async def pause_session(session_id: str, db: Session = Depends(get_db)) -> dict:
    """Pause an upgrade session"""
    try:
        session = db.query(UpgradeSession).filter(UpgradeSession.session_id == session_id).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        result = executor.pause_process(session_id)

        if result["status"] != "error":
            session.status = "paused"
            db.commit()

            AuditLogger.log_event(db, session_id, "session_paused", "Upgrade session paused")

        return result

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/resume")
async def resume_session(session_id: str, db: Session = Depends(get_db)) -> dict:
    """Resume a paused upgrade session"""
    try:
        session = db.query(UpgradeSession).filter(UpgradeSession.session_id == session_id).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        result = executor.resume_process(session_id)

        if result["status"] != "error":
            session.status = "running"
            db.commit()

            AuditLogger.log_event(db, session_id, "session_resumed", "Upgrade session resumed")

        return result

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/cancel")
async def cancel_session(session_id: str, db: Session = Depends(get_db)) -> dict:
    """Cancel an upgrade session"""
    try:
        session = db.query(UpgradeSession).filter(UpgradeSession.session_id == session_id).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        result = executor.cancel_process(session_id)

        if result["status"] != "error":
            session.status = "cancelled"
            session.completed_at = datetime.utcnow()
            db.commit()

            AuditLogger.log_event(db, session_id, "session_cancelled", "Upgrade session cancelled")

        return result

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/status")
async def get_session_status(session_id: str, db: Session = Depends(get_db)) -> dict:
    """Get real-time status of a session"""
    try:
        session = db.query(UpgradeSession).filter(UpgradeSession.session_id == session_id).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        process_status = executor.get_process_status(session_id)

        return {
            "session_id": session_id,
            "session_status": session.status,
            "process_status": process_status["status"],
            "current_firewall_index": session.current_firewall_index,
            "total_firewalls": session.total_firewalls,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
