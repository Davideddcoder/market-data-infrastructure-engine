"""
Database table schema and creation.
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from database.connection import engine
from utils.logger import get_logger

logger = get_logger(__name__)

Base = declarative_base()


class MarketData(Base):
    """
    Market data table schema.
    
    Stores normalized market data from all exchanges.
    """
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    open_interest = Column(Float, nullable=True)
    funding_rate = Column(Float, nullable=True)
    liquidations = Column(Float, nullable=True)
    source = Column(String(50), nullable=False, index=True)
    processed_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_source_timestamp', 'source', 'timestamp'),
    )
    
    def __repr__(self) -> str:
        return (
            f"<MarketData(id={self.id}, timestamp={self.timestamp}, "
            f"symbol={self.symbol}, price={self.price}, source={self.source})>"
        )


class ProcessedData(Base):
    """
    Processed market data table schema.
    
    Stores feature-engineered market data.
    """
    __tablename__ = 'processed_data'
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    rolling_avg_price = Column(Float, nullable=True)
    volume_aggregated = Column(Float, nullable=True)
    open_interest = Column(Float, nullable=True)
    funding_rate = Column(Float, nullable=True)
    liquidations = Column(Float, nullable=True)
    source = Column(String(50), nullable=False, index=True)
    features_computed_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_symbol_timestamp_processed', 'symbol', 'timestamp'),
    )
    
    def __repr__(self) -> str:
        return (
            f"<ProcessedData(id={self.id}, timestamp={self.timestamp}, "
            f"symbol={self.symbol}, price={self.price})>"
        )


def create_all_tables() -> None:
    """
    Create all database tables.
    
    Idempotent: safe to call multiple times.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created successfully")
    except Exception as e:
        logger.error(f"✗ Failed to create database tables: {str(e)}")
        raise
