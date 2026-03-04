# Palo Alto Networks Firewall Upgrade Automation

Comprehensive Ansible playbook for upgrading Palo Alto firewalls with support for individual firewalls, HA pairs, and Panorama-managed deployments.

## Features

- **Multi-deployment support**: Individual firewalls, HA pairs, and Panorama-managed firewalls
- **Mandatory backups**: Automatic configuration backup before any upgrade
- **Rolling upgrades**: Minimize service disruption for HA deployments
- **Comprehensive validation**: Pre-upgrade and post-upgrade health checks
- **Detailed logging**: Complete audit trail of all upgrade operations
- **Error handling**: Graceful error handling with optional rollback capability
- **Firmware management**: Download firmware directly from Palo Alto Networks portal

## Prerequisites

### Ansible Requirements
- Ansible 2.9 or later
- Python 3.6 or later
- Required collection: `paloaltonetworks.panos`

### Installation

```bash
# Install Palo Alto Networks Ansible collection
ansible-galaxy collection install paloaltonetworks.panos

# Or upgrade to latest version
ansible-galaxy collection install --force paloaltonetworks.panos
```

### Firewall Requirements
- Palo Alto firewall with API access enabled
- API credentials with admin privileges
- Or Panorama with management privileges (for Panorama-managed devices)
- Valid Palo Alto Networks support portal access (for firmware download)

## Directory Structure

```
.
├── palo_alto_firewall_upgrade.yml    # Main Ansible playbook
├── inventory/
│   └── palo_alto.yml                 # Firewall inventory and host definitions
├── group_vars/
│   └── palo_alto_firewalls.yml       # Default group variables
├── vars/
│   └── upgrade_config.yml            # Upgrade-specific configuration
├── templates/
│   └── upgrade_report.j2             # Upgrade report template
├── backups/                          # Configuration backups (created at runtime)
├── logs/                             # Upgrade logs (created at runtime)
└── README.md                         # This file
```

## Quick Start

### 1. Configure Inventory

Edit `inventory/palo_alto.yml` and add your firewalls:

```yaml
all:
  children:
    palo_alto_firewalls:
      hosts:
        fw-primary:
          panos_ip: 192.168.1.1
          panos_username: admin
          ha_enabled: true
          is_primary: true
          ha_peer_ip: 192.168.1.2
        fw-secondary:
          panos_ip: 192.168.1.2
          panos_username: admin
          ha_enabled: true
          is_primary: false
          ha_peer_ip: 192.168.1.1
```

### 2. Set Credentials

Choose one method:

**Option A: Environment Variables (Recommended)**
```bash
export PANOS_USERNAME=admin
export PANOS_PASSWORD=your_password
export PALO_ALTO_PORTAL_USERNAME=your_portal_email
export PALO_ALTO_PORTAL_PASSWORD=your_portal_password
```

**Option B: Ansible Vault (Recommended for production)**
```bash
ansible-vault encrypt inventory/palo_alto.yml
# Then enter your vault password
```

**Option C: Variable Files**
Edit `group_vars/palo_alto_firewalls.yml` and add credentials directly (NOT recommended for production).

### 3. Configure Upgrade Parameters

Edit `vars/upgrade_config.yml` to set:
- Target firmware version
- Backup retention period
- Pre/post-upgrade validation options
- HA failover strategy
- Error handling preferences

### 4. Run the Playbook

**Dry-run (check mode):**
```bash
ansible-playbook palo_alto_firewall_upgrade.yml -i inventory/palo_alto.yml --check
```

**Upgrade all firewalls:**
```bash
ansible-playbook palo_alto_firewall_upgrade.yml -i inventory/palo_alto.yml
```

**Upgrade specific firewall:**
```bash
ansible-playbook palo_alto_firewall_upgrade.yml -i inventory/palo_alto.yml -l fw-primary
```

**Verbose output for debugging:**
```bash
ansible-playbook palo_alto_firewall_upgrade.yml -i inventory/palo_alto.yml -vv
```

## Testing

Run automated checks:

```bash
./tests/run_tests.sh
```

Run live PAN firewall API smoke test (optional):

```bash
export PAN_TEST_HOST=10.0.1.10
export PAN_TEST_USERNAME=admin
export PAN_TEST_PASSWORD='your_password'
./tests/run_tests.sh
```

## Playbook Phases

### Phase 1: Pre-Upgrade Validation
- Test API connectivity
- Verify current firmware version
- Check system resources (memory, disk, CPU)
- Detect HA configuration and role (primary/secondary)
- Verify no pending operations

### Phase 2: Configuration Backup
- Export current firewall configuration
- Save backup with timestamp
- Create backup file copy for records
- Verify backup integrity

### Phase 3: Firmware Download & Staging
- Download target firmware version from Palo Alto portal
- Verify integrity and checksum
- Stage firmware on firewall

### Phase 4: Upgrade Execution (Rolling Strategy)
- **Non-HA firewalls**: Direct upgrade and reboot
- **HA secondary**: Upgrade secondary first, wait for sync
- **HA primary**: Suspend HA, upgrade, wait for recovery and sync

### Phase 5: Post-Upgrade Validation
- Verify firewall is online
- Confirm correct firmware version installed
- Check system resources and stability
- Verify HA synchronization
- Validate configuration loaded correctly

### Phase 6: Reporting
- Generate detailed upgrade report
- Save logs with timestamps
- Provide summary of upgrade status

## Configuration Options

### Key Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `target_firmware_version` | 11.1.0 | Target firmware version |
| `backup_dir` | ./backups | Where to save backups |
| `log_dir` | ./logs | Where to save logs |
| `upgrade_strategy` | rolling | rolling or immediate |
| `execution_mode` | sequential | sequential or parallel |
| `ha_failover_strategy` | graceful | graceful or immediate |
| `fail_on_single_host_failure` | false | Stop on first failure |
| `rollback_on_failure` | false | Attempt automatic rollback |

### HA Configuration

For HA pairs, ensure both firewalls are in inventory:

```yaml
fw-primary:
  ha_enabled: true
  is_primary: true
  ha_peer_ip: 192.168.1.2

fw-secondary:
  ha_enabled: true
  is_primary: false
  ha_peer_ip: 192.168.1.1
```

The playbook will:
1. Upgrade the secondary firewall first
2. Wait for HA sync
3. Suspend HA on the primary
4. Upgrade the primary
5. Wait for primary to boot and sync

## Troubleshooting

### Firewall Unreachable
- Verify API is enabled on firewall: Device > Setup > Management > API Settings
- Check network connectivity from Ansible controller to firewall
- Verify credentials and API port (default 443)

### Firmware Download Fails
- Verify Palo Alto Networks portal credentials are correct
- Confirm target version is available for your model
- Check internet connectivity from Ansible controller

### HA Sync Issues
- Wait longer for sync (increase `ha_sync_timeout` in variables)
- Check firewall logs for sync errors
- May need manual intervention to re-establish HA

### Playbook Fails Mid-Upgrade
- **Do not interrupt the playbook** - let it complete or timeout
- Check firewall logs for upgrade status
- Can safely re-run playbook - it will detect if upgrade already completed
- Manual rollback available using backup configuration file

## Backup and Recovery

All backups are saved to `./backups/` with format:
```
{hostname}-{old_version}-backup-{timestamp}.xml
```

### Manual Restore

1. Access firewall via GUI
2. Device > Setup > Management
3. Click "Restore" and upload backup XML file
4. Firewall will reboot with restored configuration

Or via CLI:
```
request system configuration import from-url {backup_file_url}
```

## Security Considerations

1. **Use Ansible Vault** for storing credentials
2. **Restrict inventory access** - contains sensitive firewall IPs
3. **Review backups location** - contains firewall configurations
4. **Audit logs** - keep upgrade logs for compliance
5. **Test in non-production** before deploying to production

## Advanced Features

### Skip Already-Upgraded Firewalls
The playbook automatically skips firewalls already at the target version.

### Parallel Execution
Set `execution_mode: parallel` in `vars/upgrade_config.yml` to upgrade multiple non-HA firewalls simultaneously.

### Custom Pre/Post Tasks
Extend the playbook with additional pre-upgrade or post-upgrade tasks as needed.

### Integration with Monitoring
Add hooks to notify monitoring systems before/after upgrades.

## Support and Issues

For issues:
1. Run with verbose output: `ansible-playbook ... -vv`
2. Check firewall API logs
3. Review backup and logs in `./backups/` and `./logs/`
4. Contact Palo Alto Networks support for device-specific issues

## Limitations

- Requires direct API access to firewalls
- Panorama integration is limited to metadata collection
- Firmware download requires internet connectivity from Ansible controller
- HA upgrade requires both peers to be operational

## Examples

### Upgrade Single Firewall
```bash
ansible-playbook palo_alto_firewall_upgrade.yml \
  -i inventory/palo_alto.yml \
  -l fw-branch-01 \
  -e target_firmware_version=11.0.0
```

### Upgrade with Custom Backup Location
```bash
ansible-playbook palo_alto_firewall_upgrade.yml \
  -i inventory/palo_alto.yml \
  -e backup_dir=/backups/palo_alto/2026-03-04
```

### Dry-run with Detailed Output
```bash
ansible-playbook palo_alto_firewall_upgrade.yml \
  -i inventory/palo_alto.yml \
  --check -vv
```

## License

Use as needed in your organization. Follow your internal policies and Palo Alto Networks terms of service.

## Change Log

### v1.0.0
- Initial release
- Support for individual firewalls, HA pairs, and Panorama-managed devices
- Comprehensive pre/post-upgrade validation
- Automatic backup and reporting
