"""
Palo Alto Firewall Upgrade Automation - Web GUI Backend
FastAPI application with WebSocket support for real-time updates
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db, get_db, engine
from models import Base
from api import sessions, firewalls, audit, websocket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    logger.info("Starting Palo Alto Upgrade GUI Backend")
    init_db()
    yield
    logger.info("Shutting down Palo Alto Upgrade GUI Backend")


# Create FastAPI app
app = FastAPI(
    title="Palo Alto Firewall Upgrade GUI API",
    description="API for monitoring and controlling Palo Alto firewall upgrades",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(sessions.router)
app.include_router(firewalls.router)
app.include_router(audit.router)
app.include_router(websocket.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "component": "backend"
    }


@app.get("/api/config")
async def get_config():
    """Get configuration info"""
    return {
        "db_path": os.getenv("DB_PATH", "/data/gui.db"),
        "playbook_dir": os.getenv("PLAYBOOK_DIR", "/workspace"),
        "backup_dir": os.getenv("BACKUP_DIR", "/data/backups"),
        "log_dir": os.getenv("LOG_DIR", "/data/logs"),
    }


@app.get("/api/inventory-files")
async def get_inventory_files():
    """Get list of available inventory files"""
    from utils.yaml_parser import InventoryParser
    files = InventoryParser.get_available_inventory_files()
    return {
        "inventory_files": files,
        "total": len(files)
    }


@app.get("/api/firmware-versions")
async def get_firmware_versions():
    """Get list of available firmware versions"""
    from utils.yaml_parser import InventoryParser
    versions = InventoryParser.get_available_firmware_versions()
    return {
        "firmware_versions": versions,
        "total": len(versions)
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")

    logger.info(f"Starting FastAPI server on {host}:{port}")
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )
