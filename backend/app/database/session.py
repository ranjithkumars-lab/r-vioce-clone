from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config_registry import ConfigRegistry
from app.core.logging import logger
from app.database.base import Base
import app.models  # Ensure models register with Base.metadata


settings = ConfigRegistry.get_settings()

# Connect args for SQLite to allow multi-threaded access safely
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database tables for single voice_studio.db."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database initialized cleanly at: {settings.DATABASE_URL}")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """Dependency provider yielding SQLAlchemy Session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
