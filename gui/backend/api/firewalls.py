"""
API endpoints for firewall-specific operations
"""

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import AuditLogEntry, FirewallStatus, UpgradeSession
from services.audit_logger import AuditLogger
from services.playbook_executor import PlaybookExecutor

router = APIRouter(prefix="/api/firewalls", tags=["firewalls"])
executor = PlaybookExecutor()


@router.get("/sessions/{session_id}")
async def list_session_firewalls(session_id: str, db: Session = Depends(get_db)) -> dict:
    """List all firewalls in a session"""
    try:
        firewalls = db.query(FirewallStatus).filter(
            FirewallStatus.session_id == session_id
        ).all()

        return {
            "session_id": session_id,
            "total": len(firewalls),
            "firewalls": [
                {
                    "firewall_id": fw.firewall_id,
                    "firewall_ip": fw.firewall_ip,
                    "status": fw.status,
                    "current_phase": fw.current_phase,
                    "progress_percent": fw.progress_percent,
                    "firmware_version_current": fw.firmware_version_current,
                    "firmware_version_target": fw.firmware_version_target,
                    "ha_enabled": fw.ha_enabled,
                    "ha_primary": fw.ha_primary,
                    "started_at": fw.started_at.isoformat() if fw.started_at else None,
                    "completed_at": fw.completed_at.isoformat() if fw.completed_at else None,
                }
                for fw in firewalls
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/{firewall_id}")
async def get_firewall_details(
    session_id: str,
    firewall_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """Get detailed status of a firewall in a session"""
    try:
        firewall = db.query(FirewallStatus).filter(
            FirewallStatus.session_id == session_id,
            FirewallStatus.firewall_id == firewall_id
        ).first()

        if not firewall:
            raise HTTPException(status_code=404, detail="Firewall not found in session")

        # Get recent logs for this firewall (from audit log)
        recent_events = db.query(AuditLogEntry).filter(
            AuditLogEntry.session_id == session_id,
            AuditLogEntry.firewall_id == firewall_id
        ).order_by(AuditLogEntry.timestamp.desc()).limit(50).all()

        return {
            "session_id": session_id,
            "firewall_id": firewall.firewall_id,
            "firewall_ip": firewall.firewall_ip,
            "status": firewall.status,
            "current_phase": firewall.current_phase,
            "progress_percent": firewall.progress_percent,
            "firmware_version_current": firewall.firmware_version_current,
            "firmware_version_target": firewall.firmware_version_target,
            "ha_enabled": firewall.ha_enabled,
            "ha_primary": firewall.ha_primary,
            "ha_peer_id": firewall.ha_peer_id,
            "backup_file": firewall.backup_file,
            "error_message": firewall.error_message,
            "started_at": firewall.started_at.isoformat() if firewall.started_at else None,
            "completed_at": firewall.completed_at.isoformat() if firewall.completed_at else None,
            "recent_events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "phase": event.phase,
                    "severity": event.severity,
                    "message": event.message,
                }
                for event in recent_events
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/{firewall_id}/rollback")
async def rollback_firewall(
    session_id: str,
    firewall_id: str,
    target_version: str = Body(..., embed=True),
    db: Session = Depends(get_db)
) -> dict:
    """Trigger rollback for a specific firewall"""
    try:
        firewall = db.query(FirewallStatus).filter(
            FirewallStatus.session_id == session_id,
            FirewallStatus.firewall_id == firewall_id
        ).first()

        if not firewall:
            raise HTTPException(status_code=404, detail="Firewall not found in session")

        session = db.query(UpgradeSession).filter(
            UpgradeSession.session_id == session_id
        ).first()

        # Create rollback session ID
        rollback_session_id = f"rollback_{session_id}_{firewall_id}"

        # Trigger rollback playbook
        result = executor.start_upgrade(
            session_id=rollback_session_id,
            playbook_file="palo_alto_firewall_rollback.yml",
            inventory_file=session.inventory_file,
            target_version=target_version,
            extra_vars={"target_firewalls": firewall_id}
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        # Log rollback event
        AuditLogger.log_event(
            db,
            session_id,
            "rollback_started",
            f"Rollback initiated for {firewall_id} to version {target_version}",
            firewall_id=firewall_id,
            severity="warning"
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/{firewall_id}/logs")
async def get_firewall_logs(
    session_id: str,
    firewall_id: str,
    lines: int = 100,
    db: Session = Depends(get_db)
) -> dict:
    """Get raw logs for a firewall from session"""
    try:
        session = db.query(UpgradeSession).filter(
            UpgradeSession.session_id == session_id
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Try to get the log file
        import os
        log_dir = os.getenv("LOG_DIR", "/data/logs")
        log_file = os.path.join(log_dir, f"{session_id}_ansible.log")

        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                content = ''.join(all_lines[-lines:])
        else:
            content = f"Log file not found: {log_file}"

        return {
            "session_id": session_id,
            "firewall_id": firewall_id,
            "log_content": content
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
