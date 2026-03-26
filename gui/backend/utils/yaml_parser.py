"""
Utility functions for parsing inventory YAML files
"""

import yaml
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class InventoryParser:
    """Parse Palo Alto inventory YAML files"""

    @staticmethod
    def parse_inventory(inventory_file: str) -> Dict[str, Any]:
        """
        Parse inventory YAML file and extract firewall list

        Args:
            inventory_file: Path to inventory YAML file

        Returns:
            Dictionary with firewalls, groups, and metadata
        """
        try:
            with open(inventory_file, 'r') as f:
                inventory_data = yaml.safe_load(f)

            if not inventory_data:
                logger.warning(f"Inventory file {inventory_file} is empty")
                return {"firewalls": [], "error": "Empty inventory file"}

            firewalls = []
            groups = inventory_data.get('all', {}).get('children', {}).get('palo_alto_firewalls', {})
            hosts = groups.get('hosts', {})

            for hostname, host_vars in hosts.items():
                firewall = {
                    "firewall_id": hostname,
                    "panos_ip": host_vars.get('panos_ip', hostname),
                    "ha_enabled": host_vars.get('ha_enabled', False),
                    "is_primary": host_vars.get('is_primary', False),
                    "ha_peer_ip": host_vars.get('ha_peer_ip', ''),
                    "target_firmware_version": host_vars.get('target_firmware_version', 'unknown'),
                    "panorama_managed": host_vars.get('panorama_managed', False),
                }
                firewalls.append(firewall)

            return {
                "firewalls": firewalls,
                "total": len(firewalls),
                "file_path": inventory_file
            }

        except FileNotFoundError:
            logger.error(f"Inventory file not found: {inventory_file}")
            return {"firewalls": [], "error": f"File not found: {inventory_file}"}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file: {e}")
            return {"firewalls": [], "error": f"YAML parse error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error parsing inventory: {e}")
            return {"firewalls": [], "error": f"Parse error: {str(e)}"}

    @staticmethod
    def get_available_inventory_files(playbook_dir: str = "/workspace") -> List[str]:
        """
        Get list of available inventory files

        Args:
            playbook_dir: Root directory to search for inventories

        Returns:
            List of inventory file paths
        """
        inventory_files = []
        try:
            inventory_dir = Path(playbook_dir) / "inventory"
            if inventory_dir.exists():
                inventory_files = [
                    str(f) for f in inventory_dir.glob("*.yml")
                    if f.is_file()
                ]
        except Exception as e:
            logger.error(f"Error finding inventory files: {e}")

        return inventory_files

    @staticmethod
    def get_available_firmware_versions() -> List[str]:
        """
        Get list of available firmware versions for Palo Alto devices
        (This would typically be fetched from Palo Alto support portal or config)

        Returns:
            List of firmware versions
        """
        # Placeholder - in production this would be fetched from a configuration
        # or the Palo Alto support portal
        return [
            "11.1.0",
            "11.0.4",
            "11.0.3",
            "10.2.8",
            "10.2.4",
        ]
