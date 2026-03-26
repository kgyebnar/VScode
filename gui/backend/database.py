"""
Database initialization and session management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SQLSession
from sqlalchemy.pool import StaticPool
from models import Base
import logging

logger = logging.getLogger(__name__)

# Database path
DB_PATH = os.getenv("DB_PATH", "/data/gui.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else ".", exist_ok=True)

# Create engine with SQLite connection
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true"
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    logger.info(f"Initializing database at {DB_PATH}")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def get_db():
    """Get database session for dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Get async database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
