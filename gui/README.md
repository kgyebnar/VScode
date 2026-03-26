# Palo Alto Firewall Upgrade GUI

Web-based interface for monitoring and controlling Palo Alto firewall upgrades in real-time with full audit trail.

## Overview

This GUI provides a single-page web application (SPA) that integrates with the existing Ansible playbook automation to:

- **Monitor** upgrade progress across multiple firewalls in real-time
- **Control** upgrade operations: start, resume, rollback
- **Track** complete audit trail of all events and actions
- **Rollback** individual firewalls to previous firmware versions
- **Export** audit logs for compliance and analysis

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Browser (Frontend)                    │
│            React 18+ SPA with WebSocket                     │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/WebSocket
┌─────────────────────▼───────────────────────────────────────┐
│                  Backend API (FastAPI)                       │
│  - Session management  - Playbook execution - WebSocket    │
└─────────────────────┬───────────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
      ▼               ▼               ▼
  SQLite3        File System      Ansible Playbooks
   (GUI DB)    (logs, backups)     (Execution)
```

## Quick Start

### OM2248 / Linux Container

Build one image that runs the backend and the web UI together:

```bash
cd /path/to/VScode
docker build -f gui/docker/Dockerfile -t palo-alto-upgrade-gui:latest .

docker run -d --name palo-alto-upgrade-gui \
  -p 8080:80 \
  -p 8000:8000 \
  -v /opt/palo-alto-upgrade-gui/data:/data \
  palo-alto-upgrade-gui:latest
```

Access:
- Web UI: `http://<om2248-ip>:8080`
- Backend API: `http://<om2248-ip>:8080/api`
- Swagger docs: `http://<om2248-ip>:8080/docs`

If you want a one-command VM/OM2248 deployment flow, use:

```bash
cd gui/docker
./deploy-om2248.sh
```

### Docker Compose (Local Development Only)

```bash
cd gui/docker
docker compose up -d
```

### Native Installation

**Backend:**
```bash
cd gui/backend
pip install -r requirements.txt
python app.py
```

**Frontend:**
```bash
cd gui/frontend
npm install
npm run dev
```

## Project Structure

```
gui/
├── backend/
│   ├── app.py                      # FastAPI application
│   ├── models.py                   # SQLAlchemy ORM models
│   ├── database.py                 # SQLite setup
│   ├── requirements.txt
│   ├── api/
│   │   ├── sessions.py             # Session endpoints
│   │   ├── firewalls.py            # Firewall endpoints
│   │   ├── audit.py                # Audit log endpoints
│   │   └── websocket.py            # WebSocket handler
│   ├── services/
│   │   ├── playbook_executor.py    # Execute Ansible
│   │   ├── audit_logger.py         # Audit logging
│   │   └── websocket_manager.py    # WebSocket broadcast
│   └── utils/
│       └── yaml_parser.py          # Parse inventory
├── frontend/
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── pages/                  # Dashboard, session, firewall, audit views
│   │   ├── services/               # API & WebSocket clients
│   │   ├── utils/                  # Shared formatting helpers
│   │   ├── main.jsx                # Vite entry point
│   │   ├── store.js                # Zustand state
│   │   ├── App.jsx                 # Root router
│   │   └── styles.css              # Global styling
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
└── docker/
    ├── Dockerfile                  # Single-container OM2248 build
    ├── docker-compose.yml          # Optional local dev stack
    ├── entrypoint.sh               # Starts backend + nginx
    └── nginx.om2248.conf           # Nginx reverse proxy config
```

## API Endpoints

### Sessions
```
GET    /api/sessions                    # List all sessions
POST   /api/sessions                    # Create session
GET    /api/sessions/{id}               # Get session details
GET    /api/sessions/{id}/status        # Real-time status
POST   /api/sessions/{id}/start         # Start upgrade
POST   /api/sessions/{id}/resume        # Resume upgrade
```

### Firewalls
```
GET    /api/firewalls/sessions/{id}                    # List firewalls
GET    /api/firewalls/sessions/{id}/{fw_id}            # Firewall details
POST   /api/firewalls/sessions/{id}/{fw_id}/rollback   # Rollback
GET    /api/firewalls/sessions/{id}/{fw_id}/logs       # Firewall logs
```

### Audit Log
```
GET    /api/audit/sessions/{id}           # Get audit log
GET    /api/audit/sessions/{id}/summary   # Event summary
GET    /api/audit/firewalls/{fw_id}       # Firewall events
GET    /api/audit/events/{event_type}     # Events by type
```

### WebSocket
```
WS     /ws/sessions/{session_id}         # Real-time updates
```

## Features

### Real-time Monitoring
- Live progress bars for each firewall
- Phase-by-phase tracking (validation → backup → download → install → post-validation)
- WebSocket-based updates (no polling)
- Automatic reconnection on connection loss

### Session Management
- Create new upgrade session from web UI
- Select inventory, target version, execution mode
- Review firewall list before starting
- View session history

### Upgrade Operations
- **Start**: Begin upgrade from pending state
- **Resume**: Continue from next firewall
- **Rollback**: Trigger an individual firewall rollback from its detail page

### Rollback Capability
- Rollback individual firewall to previously installed version
- Visible in firewall detail view
- Triggers separate rollback playbook

### Audit Trail
- Every action logged with timestamp
- Searchable by firewall, severity, event type
- Export to CSV/JSON
- Queryable API for programmatic access

## Environment Variables

### Backend
- `DB_PATH`: SQLite database path (default: `/data/gui.db`)
- `PLAYBOOK_DIR`: Directory containing Ansible playbooks (default: `/app`)
- `BACKUP_DIR`: Where to store firewall config backups (default: `/data/backups`)
- `LOG_DIR`: Where to store upgrade logs (default: `/data/logs`)
- `BACKEND_HOST`: API server host (default: `0.0.0.0`)
- `BACKEND_PORT`: API server port (default: `8000`)
- `DEBUG`: Enable debug mode (default: `false`)

### Frontend
- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000/api`)
- `VITE_WS_URL`: WebSocket URL (default: `ws://localhost:8000`)

## Usage Examples

### Create and Monitor Upgrade

1. **Navigate to Dashboard**: http://localhost:8080
2. **Click "New Session"**
3. **Select inventory file**: `inventory/palo_alto.yml`
4. **Enter target version**: `11.1.0`
5. **Choose execution mode**: `sequential` (one firewall at a time)
6. **Click "Start Upgrade"**
7. **Monitor in real-time**:
   - See progress bars for each firewall
   - Watch phase progression
   - Check audit log for events
   - No page refresh needed

### Resume a Session

1. Open a paused session
2. Click **"Resume upgrade"**
3. The playbook continues from the next pending firewall

### Rollback Single Firewall

1. In active session, click on a firewall
2. View detailed status and logs
3. Click **"Rollback"** button
4. Select firmware version to rollback to
5. Confirm
6. Rollback playbook executes

### Export Audit Log

1. Navigate to Audit Log tab
2. View all events with timestamps
3. Filter by severity, event type, or firewall
4. Export as CSV or JSON for compliance

## Database Schema

### UpgradeSession
```
session_id          PK  String
created_at              DateTime
started_at              DateTime (nullable)
completed_at            DateTime (nullable)
status                  String (pending, running, completed, failed, paused)
target_firmware_version String
execution_mode          String (sequential, parallel)
total_firewalls         Integer
current_firewall_index  Integer
inventory_file          String
extra_vars              JSON
created_by              String
notes                   String
```

### FirewallStatus
```
id                      PK  Integer
session_id              FK  String
firewall_id             String (hostname)
firewall_ip             String
status                  String
current_phase           String
progress_percent        Integer
firmware_version_current String
firmware_version_target String
ha_enabled              Boolean
ha_primary              Boolean
backup_file             String
error_message           String
started_at              DateTime
completed_at            DateTime
```

### AuditLogEntry
```
id                  PK  Integer
timestamp           DateTime (indexed)
session_id          FK  String (indexed)
firewall_id         String (indexed, nullable)
event_type          String (indexed)
severity            String (indexed)
phase               String
message             String
details             JSON
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG=false` in environment
- [ ] Configure CORS origins (restrict from `*`)
- [ ] Use strong database encryption
- [ ] Enable HTTPS/TLS
- [ ] Set up log rotation for audit logs
- [ ] Configure backup retention policy
- [ ] Test rollback procedures
- [ ] Set up monitoring/alerting
- [ ] Create backup of database(/data/gui.db)
- [ ] Document API credentials management

### Docker Deployment

```bash
# Build image
docker build -t palo-alto-upgrade-gui:latest -f docker/Dockerfile .

# Run with persistent storage
docker run -d \
  --name palo-alto-gui \
  -p 8080:80 \
  -v /path/to/data:/data \
  palo-alto-upgrade-gui:latest
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (optional).

##  Troubleshooting

### Backend won't start
```bash
# Check logs
docker logs palo-alto-gui

# Verify database
ls -la /data/gui.db

# Test API health
curl http://localhost:8000/health
```

### Frontend can't connect to backend
- Check VITE_API_URL environment variable
- Verify backend is running on correct port
- Check browser console for CORS errors
- Verify firewall ports are open

### WebSocket connection fails
- Check ws:// URL (should use ws not http)
- Verify proxy configuration in `gui/docker/nginx.om2248.conf`
- Check browser WebSocket support (DevTools → Network)

### Playbook execution fails
- Verify inventory file path is correct
- Check Ansible playbooks exist in /app
- Verify firewall credentials are valid
- Check network connectivity to firewalls

## Performance Tips

- Use sequential mode for production (safer, predictable)
- Run backend and frontend on same machine or close network
- Keep WebSocket connections alive (built-in keep-alive)
- Archive old sessions periodically
- Monitor database size (/data/gui.db)

## Security Notes

- No authentication required (suitable for internal-only deployment)
- All API endpoints are public
- Database is SQLite (single file, no server)
- Credentials stored in environment variables only
- Audit log captures all operations
- TLS/HTTPS should be used in production (nginx/load balancer)

## Future Enhancements

- [ ] Multi-user support with RBAC
- [ ] Email notifications on completion
- [ ] Scheduled upgrades
- [ ] Advanced filtering and search in audit logs
- [ ] Mobile UI
- [ ] Multi-language support
- [ ] Dark mode UI
- [ ] Metrics/chart dashboards
- [ ] Integration with Panorama
- [ ] Dry-run mode preview

## Support

For issues:
1. Check logs: `docker logs palo-alto-gui`
2. Review this README
3. Check backend/frontend source code comments
4. Reference Ansible playbook documentation

## License

Use as needed for your organization.

## Version

- GUI Version: 1.0.0
- Backend: FastAPI 0.104+
- Frontend: React 18+
- Supports Palo Alto Playbook: v1.0+
