# Palo Alto Networks Ansible Module Reference

This document explains the key Ansible modules used in the firewall upgrade playbook.

## Main Module: paloaltonetworks.panos.panos_software

Used for downloading and installing firmware on Palo Alto firewalls.

### Module Parameters

```yaml
paloaltonetworks.panos.panos_software:
  ip_address: "192.168.1.1"           # Firewall IP or hostname
  username: "admin"                    # API username
  password: "your_password"            # API password
  version: "11.1.0"                    # Firmware version to download/install
  download: yes                        # Download firmware if available
  install: yes                         # Install downloaded firmware
  restart: yes                         # Reboot after installation
```

### Usage Examples

```yaml
# Download firmware without installing
- name: Download firmware
  paloaltonetworks.panos.panos_software:
    ip_address: "{{ panos_ip }}"
    username: "{{ panos_username }}"
    password: "{{ panos_password }}"
    version: "{{ target_firmware_version }}"
    download: yes
    install: no

# Install and reboot (after download)
- name: Install firmware and reboot
  paloaltonetworks.panos.panos_software:
    ip_address: "{{ panos_ip }}"
    username: "{{ panos_username }}"
    password: "{{ panos_password }}"
    version: "{{ target_firmware_version }}"
    download: no
    install: yes
    restart: yes
```

### Return Values

```yaml
# When successful
msg: "firmware(s) installed and firewall rebooting"
changed: true

# When already at target version
msg: "System is already on firmware version 11.1.0"
changed: false

# When download fails
fail_on: "Failed to download firmware"
changed: false
```

### Important Notes

1. **Automatic reboot**: When `restart: yes`, the firewall will reboot automatically
2. **HA handling**: Module doesn't handle HA failover - must be done separately
3. **Download time**: Depends on firmware file size and internet connection
4. **Reboot time**: Usually 5-10 minutes on modern firewalls

## Supporting Module: paloaltonetworks.panos.panos_op

Used for running operational commands on firewalls.

### Common Commands Used

```yaml
# Get system information
- paloaltonetworks.panos.panos_op:
    cmd: "request system info"

# Get HA status
- paloaltonetworks.panos.panos_op:
    cmd: "request high-availability info"

# Get hardware info
- paloaltonetworks.panos.panos_op:
    cmd: "request system hardware info"

# Get available firmware versions
- paloaltonetworks.panos.panos_op:
    cmd: "request system software info"

# Get resource usage
- paloaltonetworks.panos.panos_op:
    cmd: "request system resource info"

# Suspend HA
- paloaltonetworks.panos.panos_op:
    cmd: "request high-availability suspend"

# Export configuration
- paloaltonetworks.panos.panos_op:
    cmd: "request export configuration to file"
```

### Return Value

```yaml
# Returns XML response from firewall
stdout_xml: "<response status='success'><result>...</result></response>"

# Parsed output available via XML parsing
```

## HA-Specific Operations

### Pre-Upgrade HA Checks

```yaml
# Check if HA is enabled
- name: Check HA status
  paloaltonetworks.panos.panos_op:
    ip_address: "{{ panos_ip }}"
    username: "{{ panos_username }}"
    password: "{{ panos_password }}"
    cmd: "request high-availability info"
  register: ha_info

# Parse HA status
- xml:
    xmlstring: "{{ ha_info.stdout_xml }}"
    xpath: /response/result/enabled
    content: text
  register: ha_enabled
```

### HA Suspend/Resume

```yaml
# Suspend HA (before upgrading primary)
- name: Suspend HA
  paloaltonetworks.panos.panos_op:
    ip_address: "{{ panos_ip }}"
    username: "{{ panos_username }}"
    password: "{{ panos_password }}"
    cmd: "request high-availability suspend"
```

## Configuration Backup

### Export Configuration

```yaml
# Export configuration to file
- name: Export configuration
  paloaltonetworks.panos.panos_op:
    ip_address: "{{ panos_ip }}"
    username: "{{ panos_username }}"
    password: "{{ panos_password }}"
    cmd: "request export configuration to file"
  register: backup_result
```

## Troubleshooting with Modules

### Enable Debug Output

```bash
# Run with module debug:
ansible-playbook playbook.yml -vvv
```

### Common Errors

```
ERROR! Unexpected failure during module execution.
→ Firewall API not responding
  Solution: Verify API access, check firewall connectivity

ERROR! msg": "Failed to download firmware image
→ Firmware version not available
  Solution: Check version number, verify support portal access

ERROR! \"Timed out waiting for device\"
→ Firewall taking longer to reboot
  Solution: Increase wait timeouts, check firewall logs
```

## Module Versions

To check which version of the paloaltonetworks.panos collection you have:

```bash
ansible-galaxy collection list | grep paloaltonetworks
```

To upgrade to latest version:

```bash
ansible-galaxy collection install --force paloaltonetworks.panos
```

## Authentication

All modules support three authentication methods:

1. **Direct credentials** (username/password parameters)
2. **Environment variables**:
   ```bash
   export PANOS_USERNAME=admin
   export PANOS_PASSWORD=password
   ```
3. **API key** (alternative to password):
   ```yaml
   api_key: "{{ panos_api_key }}"  # Instead of username/password
   ```

## Rate Limiting

The Palo Alto API has rate limits:
- Default: ~100 requests per minute
- Use `delay` and `retries` in playbook tasks

```yaml
- name: Task that might hit rate limit
  paloaltonetworks.panos.panos_op:
    ...
  retries: 5
  delay: 10  # Wait 10 seconds between retries
```

## API Documentation

For complete module documentation:

```bash
# List all panos modules
ansible-doc -l | grep panos_

# Get detailed info on specific module
ansible-doc paloaltonetworks.panos.panos_software
ansible-doc paloaltonetworks.panos.panos_op
```

Or visit: https://ansible-paloaltonetworks.readthedocs.io/

## Real-World Examples

### Simple upgrade sequence
```yaml
- name: Upgrade single firewall
  hosts: localhost
  tasks:
    - name: Download firmware
      paloaltonetworks.panos.panos_software:
        ip_address: 192.168.1.1
        username: admin
        password: password
        version: 11.1.0
        download: yes
        install: no

    - name: Wait for download
      wait_for:
        timeout: 300

    - name: Install and reboot
      paloaltonetworks.panos.panos_software:
        ip_address: 192.168.1.1
        username: admin
        password: password
        version: 11.1.0
        download: no
        install: yes
        restart: yes

    - name: Wait for reboot
      wait_for:
        host: 192.168.1.1
        port: 443
        delay: 30
        timeout: 600
```

### HA upgrade sequence
```yaml
- name: Upgrade HA pair
  hosts: localhost
  tasks:
    # Upgrade secondary first
    - name: Upgrade secondary
      paloaltonetworks.panos.panos_software:
        ip_address: 192.168.1.2
        username: admin
        password: password
        version: 11.1.0
        download: yes
        install: yes
        restart: yes

    - name: Wait for secondary
      wait_for:
        host: 192.168.1.2
        port: 443
        delay: 30
        timeout: 600

    # Suspend HA, upgrade primary
    - name: Suspend HA
      paloaltonetworks.panos.panos_op:
        ip_address: 192.168.1.1
        username: admin
        password: password
        cmd: "request high-availability suspend"

    - name: Upgrade primary
      paloaltonetworks.panos.panos_software:
        ip_address: 192.168.1.1
        username: admin
        password: password
        version: 11.1.0
        download: yes
        install: yes
        restart: yes

    - name: Wait for primary
      wait_for:
        host: 192.168.1.1
        port: 443
        delay: 30
        timeout: 600
```

## Limitations

1. **No automatic HA handling**: Module doesn't manage HA failover
2. **Single device per task**: Run separate tasks for each firewall
3. **No rollback automation**: Must use backup files manually
4. **No progress tracking**: Firmware download times not reported
5. **API-dependent**: Requires functioning firewall API

## Security Considerations

1. **Never hardcode credentials** in playbooks
2. **Use Ansible Vault** for sensitive variables
3. **Restrict file permissions** on inventory files
4. **Use API keys** instead of passwords when possible
5. **Enable API logging** on firewalls for audit trails
