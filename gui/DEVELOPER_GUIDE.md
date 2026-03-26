# Web GUI - Developer Quick Reference

## Project Root
📍 `/Users/kgyebnar/VScode/gui/`

## Quick Commands

### Start Full Stack
```bash
cd docker
docker compose up -d
# Access: http://localhost:8080
```

### Deploy to VM or OM2248
```bash
cd docker
./deploy-om2248.sh
```

### Start Backend Only
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Start Frontend Only
```bash
cd frontend
npm install
npm run dev
```

### Test API
```bash
# Health check
curl http://localhost:8000/health

# List sessions
curl http://localhost:8000/api/sessions

# Upload inventory
curl -F "file=@inventory/palo_alto.yml" http://localhost:8000/api/inventory-files/upload

# Swagger docs
open http://localhost:8000/docs
```

### Browser Smoke Checklist
See [`BROWSER_SMOKE.md`](./BROWSER_SMOKE.md) for the browser verification steps after deployment.

## Key Files Reference

### Backend Entry Points
| File | Purpose |
|------|---------|
| `backend/app.py` | FastAPI application + routes |
| `backend/models.py` | SQLAlchemy database models |
| `backend/database.py` | SQLite connection setup |

### Backend Services
| File | Purpose |
|------|---------|
| `backend/services/playbook_executor.py` | Execute Ansible playbooks |
| `backend/services/audit_logger.py` | Log all events |
| `backend/services/websocket_manager.py` | Broadcast updates |

### Frontend Entry Points
| File | Purpose |
|------|---------|
| `frontend/src/App.jsx` | Root router |
| `frontend/src/main.jsx` | Vite bootstrap |
| `frontend/src/store.js` | Zustand state management |
| `frontend/src/services/api.js` | API client |
| `frontend/src/pages/Dashboard.jsx` | Home page |
| `frontend/src/pages/NewSession.jsx` | Session creation |
| `frontend/src/pages/SessionDetail.jsx` | Session lifecycle and audit summary |
| `frontend/src/pages/FirewallDetail.jsx` | Firewall detail and rollback |
| `frontend/src/pages/AuditPage.jsx` | Session audit trail |

### Configuration
| File | Purpose |
|------|---------|
| `frontend/vite.config.js` | Build config |
| `docker/docker-compose.yml` | Single-container local dev |
| `docker/Dockerfile` | Single-container OM2248 image |

## Database

**Location**: `/data/gui.db` (auto-created in Docker)

**Tables**:
- `upgrade_sessions` - Session metadata
- `firewall_statuses` - Per-firewall progress
- `audit_log` - All events

**Connect locally**:
```bash
sqlite3 /path/to/gui.db
# Then SQL queries: SELECT * FROM upgrade_sessions;
```

## API Documentation

**Swagger UI**: http://localhost:8000/docs
**ReDoc**: http://localhost:8000/redoc

## Environment Variables

### Backend (in `docker-compose.yml`)
```yaml
DB_PATH=/data/gui.db
PLAYBOOK_DIR=/app
BACKEND_PORT=8000
DEBUG=false
```

### Frontend (in `docker-compose.yml`)
```yaml
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
```

## Common Tasks

### Add New API Endpoint
1. Edit `backend/api/*.py`
2. Add FastAPI route with @router.get/post
3. Restart backend

### Add New React Component
1. Create file in `frontend/src/components/`
2. Export component
3. Import in pages

### Modify Database Schema
1. Edit `backend/models.py`
2. Delete old `/data/gui.db`
3. Restart - new schema auto-created

### Change UI Styling
1. Edit `frontend/src/*.jsx` components
2. Use Tailwind classes
3. Frontend hot-reload should update

## Maintenance

### View Logs
```bash
# Docker logs
docker compose logs -f gui

# Local Backend
# Check console output

# Frontend
# Browser DevTools Console
```

### Database Backup
```bash
cp /data/gui.db /data/gui.db.backup
```

### Clean Data
```bash
# Remove all sessions
rm /data/gui.db

# Restart
docker compose restart gui
```

## File Sizes

| Component | Type | Size |
|-----------|------|------|
| Backend code | Python | ~10KB |
| Frontend code | JavaScript | ~8KB |
| Database | SQLite | Auto-grows |
| Docker image | Container | ~500MB |

## Performance Tips

1. Use sequential mode for upgrades
2. Monitor `/data/gui.db` size
3. Archive old sessions periodically
4. Use docker volumes for persistence
5. Deploy backend and frontend close (same network)

## Common Issues

| Issue | Solution |
|-------|----------|
| API won't start | Check port 8000 not in use |
| Frontend blank | Check browser console for errors |
| WebSocket fails | Verify backend is running |
| Database locked | Delete `/data/gui.db`, restart |
| Permission denied | Use `sudo docker` if needed |

## Testing

### Backend Tests (TODO)
```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/
```

### Frontend Tests (TODO)
```bash
cd frontend
npm run test
```

## Deployment Checklist

- [ ] Set `DEBUG=false`
- [ ] Change default ports if needed
- [ ] Configure volume paths
- [ ] Set up HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Test rollback procedure
- [ ] Set up monitoring
- [ ] Document access credentials
- [ ] Backup database regularly
- [ ] Set up log rotation

## Useful Aliases (add to ~/.bashrc or ~/.zshrc)

```bash
alias gui-start='cd /Users/kgyebnar/VScode/gui/docker && docker compose up -d'
alias gui-stop='cd /Users/kgyebnar/VScode/gui/docker && docker compose down'
alias gui-logs='cd /Users/kgyebnar/VScode/gui/docker && docker compose logs -f'
alias gui-api='open http://localhost:8000/docs'
alias gui-web='open http://localhost:8080'
```

## Architecture Diagram

```
Browser (8080)
    ↓
Nginx (reverse proxy)
    ↓
Frontend SPA (React)
    ↓ HTTP
API Server (8000)
    ↓ JSON
FastAPI Server
    ↓
SQLite DB
    ↓
Ansible Playbooks
    ↓
Firewalls
```

## Contact/Support

1. Check IMPLEMENTATION_STATUS.md for progress
2. Review README.md for detailed docs
3. Inspect code comments for implementation details
4. Check git history for recent changes

---
**Last Updated**: Phase 2 Complete
**Next Phase**: Phase 3 - Frontend Integration
