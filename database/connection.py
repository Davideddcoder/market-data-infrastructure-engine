"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

from utils.config import DATABASE_URL, DATABASE_ECHO
from utils.logger import get_logger

logger = get_logger(__name__)


# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=DATABASE_ECHO,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Session:
    """
    Get a database session.
    
    Returns:
        SQLAlchemy Session instance
    """
    return SessionLocal()


def get_session_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Yields:
        Session instance
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        session.close()
