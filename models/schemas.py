"""
Data models and schemas for market data.
"""
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class RawMarketData:
    """
    Raw market data structure from exchanges.
    
    Attributes:
        timestamp: Unix timestamp or datetime of the data
        symbol: Trading pair (e.g., 'BTC/USD')
        price: Current/close price
        volume: Trading volume
        open_interest: Open interest (if applicable)
        funding_rate: Funding rate (for perpetuals)
        liquidations: Liquidation volume (if applicable)
        bid: Best bid price
        ask: Best ask price
        source: Exchange name (binance, hyperliquid, bitget)
    """
    timestamp: float
    symbol: str
    price: float
    volume: float
    open_interest: Optional[float] = None
    funding_rate: Optional[float] = None
    liquidations: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    source: Optional[str] = None


@dataclass
class NormalizedMarketData:
    """
    Normalized market data following unified schema.
    
    Attributes:
        timestamp: Unix timestamp
        symbol: Trading pair
        price: Normalized price
        volume: Normalized volume
        open_interest: Normalized open interest
        funding_rate: Normalized funding rate
        liquidations: Normalized liquidations
        source: Exchange name
        processed_at: When the record was processed
    """
    timestamp: float
    symbol: str
    price: float
    volume: float
    source: str
    open_interest: Optional[float] = None
    funding_rate: Optional[float] = None
    liquidations: Optional[float] = None
    processed_at: Optional[float] = None


@dataclass
class ProcessedMarketData:
    """
    Market data after feature engineering.
    
    Attributes:
        timestamp: Unix timestamp
        symbol: Trading pair
        price: Price
        volume: Volume
        rolling_avg_price: Rolling average price
        volume_aggregated: Aggregated volume
        source: Exchange name
        features_computed_at: When features were computed
    """
    timestamp: float
    symbol: str
    price: float
    volume: float
    source: str
    rolling_avg_price: Optional[float] = None
    volume_aggregated: Optional[float] = None
    open_interest: Optional[float] = None
    funding_rate: Optional[float] = None
    liquidations: Optional[float] = None
    features_computed_at: Optional[float] = None
