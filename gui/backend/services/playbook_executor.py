"""
Service for executing Ansible playbooks and managing processes
"""

import subprocess
import logging
import asyncio
import os
import signal
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class PlaybookExecutor:
    """Execute Ansible playbooks and manage their lifecycle"""

    def __init__(self,
                 playbook_dir: str = "/workspace",
                 backup_dir: str = "/data/backups",
                 log_dir: str = "/data/logs"):
        self.playbook_dir = playbook_dir
        self.backup_dir = backup_dir
        self.log_dir = log_dir
        self.processes: Dict[str, subprocess.Popen] = {}

        # Create directories
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

    def start_upgrade(self,
                      session_id: str,
                      playbook_file: str = "palo_alto_firewall_upgrade.yml",
                      inventory_file: str = "inventory/palo_alto.yml",
                      target_version: Optional[str] = None,
                      extra_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Start an Ansible playbook execution

        Args:
            session_id: Unique session identifier
            playbook_file: Name of playbook file to execute
            inventory_file: Inventory file to use
            target_version: Target firmware version
            extra_vars: Additional variables to pass to playbook

        Returns:
            Dictionary with process info and status
        """
        try:
            # Build command
            cmd = ["ansible-playbook"]

            # Add playbook file
            playbook_path = os.path.join(self.playbook_dir, playbook_file)
            if not os.path.exists(playbook_path):
                logger.error(f"Playbook not found: {playbook_path}")
                return {
                    "status": "error",
                    "message": f"Playbook not found: {playbook_path}",
                    "session_id": session_id
                }

            cmd.append(playbook_path)

            # Add inventory
            inventory_path = inventory_file if os.path.isabs(inventory_file) else os.path.join(self.playbook_dir, inventory_file)
            if not os.path.exists(inventory_path):
                logger.error(f"Inventory not found: {inventory_path}")
                return {
                    "status": "error",
                    "message": f"Inventory not found: {inventory_path}",
                    "session_id": session_id
                }

            cmd.extend(["-i", inventory_path])

            # Add extra variables
            if target_version:
                cmd.extend(["-e", f"target_firmware_version={target_version}"])

            if extra_vars:
                for key, value in extra_vars.items():
                    cmd.extend(["-e", f"{key}={value}"])

            # Add verbose mode
            cmd.append("-v")

            # Log file for this session
            log_file = os.path.join(self.log_dir, f"{session_id}_ansible.log")

            logger.info(f"Starting playbook: {' '.join(cmd)}")
            logger.info(f"Log file: {log_file}")

            # Start process
            with open(log_file, 'w') as log_f:
                process = subprocess.Popen(
                    cmd,
                    stdout=log_f,
                    stderr=subprocess.STDOUT,
                    cwd=self.playbook_dir,
                    text=True
                )

            self.processes[session_id] = process

            return {
                "status": "started",
                "session_id": session_id,
                "pid": process.pid,
                "log_file": log_file
            }

        except Exception as e:
            logger.error(f"Error starting playbook: {e}")
            return {
                "status": "error",
                "message": str(e),
                "session_id": session_id
            }

    def get_process_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a running process"""
        if session_id not in self.processes:
            return {"status": "not_found", "session_id": session_id}

        process = self.processes[session_id]
        poll_result = process.poll()

        if poll_result is None:
            return {
                "status": "running",
                "session_id": session_id,
                "pid": process.pid
            }
        else:
            # Process finished
            del self.processes[session_id]
            return {
                "status": "completed",
                "session_id": session_id,
                "exit_code": poll_result
            }

    def pause_process(self, session_id: str) -> Dict[str, Any]:
        """Pause a running process (SIGSTOP)"""
        if session_id not in self.processes:
            return {"status": "not_found", "session_id": session_id}

        try:
            process = self.processes[session_id]
            process.send_signal(signal.SIGSTOP)
            logger.info(f"Paused process {session_id}")
            return {"status": "paused", "session_id": session_id}
        except Exception as e:
            logger.error(f"Error pausing process: {e}")
            return {"status": "error", "message": str(e), "session_id": session_id}

    def resume_process(self, session_id: str) -> Dict[str, Any]:
        """Resume a paused process (SIGCONT)"""
        if session_id not in self.processes:
            return {"status": "not_found", "session_id": session_id}

        try:
            process = self.processes[session_id]
            process.send_signal(signal.SIGCONT)
            logger.info(f"Resumed process {session_id}")
            return {"status": "resumed", "session_id": session_id}
        except Exception as e:
            logger.error(f"Error resuming process: {e}")
            return {"status": "error", "message": str(e), "session_id": session_id}

    def cancel_process(self, session_id: str) -> Dict[str, Any]:
        """Cancel a running process (SIGTERM)"""
        if session_id not in self.processes:
            return {"status": "not_found", "session_id": session_id}

        try:
            process = self.processes[session_id]
            process.send_signal(signal.SIGTERM)
            logger.info(f"Terminated process {session_id}")
            return {"status": "terminated", "session_id": session_id}
        except Exception as e:
            logger.error(f"Error terminating process: {e}")
            return {"status": "error", "message": str(e), "session_id": session_id}

    def get_log_content(self, log_file: str, lines: int = 100) -> str:
        """Get last N lines from log file"""
        try:
            if not os.path.exists(log_file):
                return f"Log file not found: {log_file}"

            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                # Return last N lines
                return ''.join(all_lines[-lines:])
        except Exception as e:
            logger.error(f"Error reading log: {e}")
            return f"Error reading log: {str(e)}"
