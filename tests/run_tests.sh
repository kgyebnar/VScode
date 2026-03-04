#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v ansible-playbook >/dev/null 2>&1; then
  echo "ansible-playbook is not installed. Install dependencies first:"
  echo "  pip install -r requirements-python.txt"
  exit 1
fi

echo "[1/3] Playbook syntax check"
ansible-playbook --syntax-check palo_alto_firewall_upgrade.yml -i inventory/palo_alto.yml

echo "[2/3] Static configuration validation"
ansible-playbook tests/test_config_validation.yml -i localhost, -c local

echo "[3/3] PAN firewall API smoke test"
if [[ -n "${PAN_TEST_HOST:-}" && -n "${PAN_TEST_USERNAME:-}" && -n "${PAN_TEST_PASSWORD:-}" ]]; then
  ansible-playbook tests/test_pan_api_connectivity.yml -i localhost, -c local
else
  echo "Skipped: set PAN_TEST_HOST, PAN_TEST_USERNAME and PAN_TEST_PASSWORD to run live PAN firewall test."
fi

echo "All available tests completed."
