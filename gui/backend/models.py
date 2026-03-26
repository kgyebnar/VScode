"""
Database models for Palo Alto Firewall Upgrade GUI
"""

from sqlalchemy import Column, String, DateTime, Integer, Boolean, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class UpgradeSession(Base):
    """Represents an upgrade session"""
    __tablename__ = "upgrade_sessions"

    session_id = Column(String(50), primary_key=True, default=lambda: f"upgrade_{datetime.now().strftime('%Y%m%dT%H%M%S')}")
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Status: pending, running, completed, failed, paused
    status = Column(String(20), default="pending")

    target_firmware_version = Column(String(50), nullable=False)
    execution_mode = Column(String(20), default="sequential")  # sequential or parallel

    total_firewalls = Column(Integer, default=0)
    current_firewall_index = Column(Integer, default=0)

    inventory_file = Column(String(255), nullable=False)
    playbook_file = Column(String(255), default="palo_alto_firewall_upgrade.yml")

    # Configuration
    extra_vars = Column(JSON, default={})  # Additional variables for playbook

    # Metadata
    created_by = Column(String(100), default="web_gui")
    notes = Column(String(1000), nullable=True)


class FirewallStatus(Base):
    """Tracks status of individual firewall during upgrade"""
    __tablename__ = "firewall_statuses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), ForeignKey("upgrade_sessions.session_id"), nullable=False)

    firewall_id = Column(String(100), nullable=False)  # hostname
    firewall_ip = Column(String(50), nullable=False)

    # Status: pending, in_progress, completed, failed, skipped, paused
    status = Column(String(20), default="pending")

    # Current phase: validation, backup, download, install, post_validation
    current_phase = Column(String(50), nullable=True)
    progress_percent = Column(Integer, default=0)

    firmware_version_current = Column(String(50), nullable=True)
    firmware_version_target = Column(String(50), nullable=False)

    # HA info
    ha_enabled = Column(Boolean, default=False)
    ha_primary = Column(Boolean, default=False)
    ha_peer_id = Column(String(100), nullable=True)

    # Key file references
    backup_file = Column(String(255), nullable=True)
    log_file = Column(String(255), nullable=True)

    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Error tracking
    error_message = Column(String(1000), nullable=True)
    error_type = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLogEntry(Base):
    """Audit trail for all upgrade events"""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    session_id = Column(String(50), ForeignKey("upgrade_sessions.session_id"), nullable=False, index=True)
    firewall_id = Column(String(100), nullable=True, index=True)

    # Event type: phase_started, phase_completed, error, warning, backup_created, etc.
    event_type = Column(String(50), nullable=False, index=True)
    phase = Column(String(50), nullable=True)

    # Severity: info, warning, error, critical
    severity = Column(String(20), default="info", index=True)

    message = Column(String(500), nullable=False)
    details = Column(JSON, default={})  # Additional context

    created_at = Column(DateTime, default=datetime.utcnow)
