# Quick Start Guide: Palo Alto Firewall Upgrade

Get your Palo Alto firewall upgrade automation running in 5 minutes.

## Step 1: Install Dependencies

```bash
# Install Ansible and collections
pip install ansible>=2.9
ansible-galaxy install -r requirements.yml

# Install Python dependencies
pip install -r requirements-python.txt
```

## Step 2: Configure Your Inventory

Edit `inventory/palo_alto.yml` and add your firewalls:

```yaml
all:
  children:
    palo_alto_firewalls:
      hosts:
        fw-01:
          panos_ip: 192.168.1.1
          panos_username: admin
```

## Step 3: Set Credentials

**Option A: Environment Variables (Recommended)**
```bash
export PANOS_USERNAME=admin
export PANOS_PASSWORD=your_password
export PALO_ALTO_PORTAL_USERNAME=your_email@company.com
export PALO_ALTO_PORTAL_PASSWORD=your_portal_password
```

**Option B: Ansible Vault**
```bash
cp credentials_vault_template.yml group_vars/palo_alto_firewalls_vault.yml
# Edit with your credentials, then:
ansible-vault encrypt group_vars/palo_alto_firewalls_vault.yml
```

## Step 4: Verify Connectivity

```bash
# Test API access to your firewall (dry-run)
ansible-playbook palo_alto_firewall_upgrade.yml -i inventory/palo_alto.yml --check
```

## Step 5: Run the Upgrade

```bash
# Display what will happen without making changes
ansible-playbook palo_alto_firewall_upgrade.yml -i inventory/palo_alto.yml --check -vv

# Actually perform the upgrade
ansible-playbook palo_alto_firewall_upgrade.yml -i inventory/palo_alto.yml
```

Rollback to a version that is already on the firewall:

```bash
ansible-playbook palo_alto_firewall_rollback.yml -i inventory/palo_alto.yml
```

## Step 6: Run on Opengear OM2248 (Container)

Build and test inside Docker (works without Docker Compose):

```bash
sudo docker build -t palo-alto-upgrade:latest .
sudo docker run --rm \
  -v "$PWD":/workspace \
  -w /workspace \
  palo-alto-upgrade:latest ./tests/run_tests.sh
```

Run playbook in container:

```bash
export PANOS_USERNAME=admin
export PANOS_PASSWORD='your_password'
sudo docker run --rm \
  -v "$PWD":/workspace \
  -w /workspace \
  -e PANOS_USERNAME \
  -e PANOS_PASSWORD \
  palo-alto-upgrade:latest \
  ansible-playbook palo_alto_firewall_upgrade.yml -i inventory/palo_alto.yml --check
```

If `docker compose` plugin is available, this is also valid:

```bash
docker compose build
docker compose run --rm palo-alto-upgrade
```

For persistent artifacts in container mode, use:
- `/data/backups` for backups
- `/data/logs` for logs

## Troubleshooting

### "No such file or directory: group_vars/palo_alto_firewalls.yml"
Make sure you're running the playbook from the correct directory where all files are located.

### "Failed to reach firewall API"
Check:
1. Firewall IP address is correct in inventory
2. API is enabled on firewall: Device > Setup > Management > API Settings
3. Network connectivity from your Ansible controller
4. Credentials are correct

### "Cannot download firmware"
- Verify Palo Alto Networks portal credentials
- Ensure target firmware version exists for your firewall model
- Check internet connectivity from Ansible controller

### "YAML syntax error"
- Ensure you're using proper indentation (2 spaces, no tabs)
- Run `ansible-playbook --syntax-check palo_alto_firewall_upgrade.yml`

## File Descriptions

| File | Purpose |
|------|---------|
| `palo_alto_firewall_upgrade.yml` | Main playbook with all upgrade logic |
| `inventory/palo_alto.yml` | Your firewall definitions |
| `group_vars/palo_alto_firewalls.yml` | Default configuration variables |
| `vars/upgrade_config.yml` | Upgrade-specific settings |
| `ansible.cfg` | Ansible configuration defaults |
| `requirements.yml` | Ansible collection dependencies |
| `requirements-python.txt` | Python package dependencies |

## Common Commands

```bash
# Upgrade all firewalls
ansible-playbook palo_alto_firewall_upgrade.yml -i inventory/palo_alto.yml

# Upgrade single firewall
ansible-playbook palo_alto_firewall_upgrade.yml -i inventory/palo_alto.yml -l fw-01

# Use different firmware version
ansible-playbook palo_alto_firewall_upgrade.yml -i inventory/palo_alto.yml -e target_firmware_version=11.0.0

# Dry-run with verbose output
ansible-playbook palo_alto_firewall_upgrade.yml -i inventory/palo_alto.yml --check -vvv

# Show HA status only (no upgrade)
ansible-playbook palo_alto_firewall_upgrade.yml -i inventory/palo_alto.yml --tags ha_check
```

## Network Requirements

```
Ansible Controller → Port 443 (HTTPS) → Palo Alto Firewall (API)
Palo Alto Firewall → Port 443 (HTTPS) → Palo Alto Networks Portal (firmware download)
```

## What Happens During Upgrade

1. ✓ Validates firewall is accessible
2. ✓ Creates configuration backup
3. ✓ Downloads firmware from Palo Alto portal
4. ✓ Installs firmware (no interruption on HA secondary)
5. ✓ Reboots firewall
6. ✓ Verifies upgrade success
7. ✓ Generates upgrade report

**Backup files**: `./backups/`
**Upgrade logs**: `./logs/`

## Next Steps

- Review [README.md](README.md) for complete documentation
- Read [inventory/palo_alto.yml](inventory/palo_alto.yml) for inventory examples
- Check [vars/upgrade_config.yml](vars/upgrade_config.yml) for configuration options
- Test on non-critical firewall first
- Set up monitoring/alerting before production runs

## Support

For detailed information, see [README.md](README.md)

For issues:
1. Run with `-vv` for verbose output
2. Check `./logs/` for detailed upgrade logs
3. Review `./backups/` for configuration backups
4. Contact your Palo Alto Networks support representative
