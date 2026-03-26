"""
Audit logging service for tracking all upgrade events
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from models import AuditLogEntry
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AuditLogger:
    """Log audit events to database"""

    @staticmethod
    def log_event(db: Session,
                  session_id: str,
                  event_type: str,
                  message: str,
                  firewall_id: Optional[str] = None,
                  phase: Optional[str] = None,
                  severity: str = "info",
                  details: Optional[Dict[str, Any]] = None) -> AuditLogEntry:
        """
        Log an audit event

        Args:
            db: Database session
            session_id: Upgrade session ID
            event_type: Type of event (phase_started, backup_created, error, etc.)
            message: Human-readable message
            firewall_id: Optional firewall identifier
            phase: Optional current phase
            severity: Event severity (info, warning, error, critical)
            details: Optional additional details as dictionary

        Returns:
            AuditLogEntry object
        """
        try:
            entry = AuditLogEntry(
                timestamp=datetime.utcnow(),
                session_id=session_id,
                firewall_id=firewall_id,
                event_type=event_type,
                phase=phase,
                severity=severity,
                message=message,
                details=details or {}
            )

            db.add(entry)
            db.commit()
            db.refresh(entry)

            logger.info(f"Audit log: {event_type} - {message} (fw: {firewall_id}, session: {session_id})")
            return entry

        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_events(db: Session,
                   session_id: Optional[str] = None,
                   firewall_id: Optional[str] = None,
                   event_type: Optional[str] = None,
                   severity: Optional[str] = None,
                   limit: int = 1000) -> list:
        """
        Get audit log entries with optional filters

        Args:
            db: Database session
            session_id: Filter by session ID
            firewall_id: Filter by firewall ID
            event_type: Filter by event type
            severity: Filter by severity
            limit: Maximum number of results

        Returns:
            List of AuditLogEntry objects
        """
        try:
            query = db.query(AuditLogEntry)

            if session_id:
                query = query.filter(AuditLogEntry.session_id == session_id)
            if firewall_id:
                query = query.filter(AuditLogEntry.firewall_id == firewall_id)
            if event_type:
                query = query.filter(AuditLogEntry.event_type == event_type)
            if severity:
                query = query.filter(AuditLogEntry.severity == severity)

            return query.order_by(AuditLogEntry.timestamp.desc()).limit(limit).all()

        except Exception as e:
            logger.error(f"Error querying audit log: {e}")
            return []

    @staticmethod
    def get_session_summary(db: Session, session_id: str) -> Dict[str, Any]:
        """
        Get summary of events for a session

        Args:
            db: Database session
            session_id: Session ID

        Returns:
            Dictionary with event counts by type and severity
        """
        try:
            all_events = db.query(AuditLogEntry).filter(
                AuditLogEntry.session_id == session_id
            ).all()

            summary = {
                "total_events": len(all_events),
                "by_event_type": {},
                "by_severity": {
                    "info": 0,
                    "warning": 0,
                    "error": 0,
                    "critical": 0
                }
            }

            for event in all_events:
                # Count by type
                if event.event_type not in summary["by_event_type"]:
                    summary["by_event_type"][event.event_type] = 0
                summary["by_event_type"][event.event_type] += 1

                # Count by severity
                if event.severity in summary["by_severity"]:
                    summary["by_severity"][event.severity] += 1

            return summary

        except Exception as e:
            logger.error(f"Error getting session summary: {e}")
            return {}
