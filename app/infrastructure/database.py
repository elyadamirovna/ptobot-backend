"""SQLAlchemy engine, session factory, and base declarative class."""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

logger = logging.getLogger(__name__)
_settings = get_settings()
logger.info("Settings.database_url = %s", _settings.database_url)
logger.info("ENV DATABASE_URL      = %s", os.getenv("DATABASE_URL"))
engine = create_engine(_settings.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for FastAPI dependencies."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
