"""
Hyperliquid market data ingestion module.

Simulates API calls to Hyperliquid and returns OHLCV, order book, and liquidations.
"""
import random
import time
from typing import List

from models.schemas import RawMarketData
from utils.logger import get_logger

logger = get_logger(__name__)


def fetch_ohlcv(symbol: str, limit: int = 10) -> List[RawMarketData]:
    """
    Simulate fetching OHLCV data from Hyperliquid.
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USD')
        limit: Number of candles to fetch
    
    Returns:
        List of RawMarketData objects
    """
    logger.debug(f"Fetching OHLCV data from Hyperliquid for {symbol}")
    
    data = []
    base_price = {'BTC/USD': 45000, 'ETH/USD': 2500, 'SOL/USD': 150}.get(symbol, 100)
    
    for i in range(limit):
        timestamp = time.time() - (limit - i) * 60
        price = base_price + random.uniform(-300, 300)
        volume = random.uniform(200000, 1500000)
        
        record = RawMarketData(
            timestamp=timestamp,
            symbol=symbol,
            price=price,
            volume=volume,
            open_interest=random.uniform(40000000, 180000000),
            source='hyperliquid'
        )
        data.append(record)
    
    logger.info(f"✓ Fetched {len(data)} OHLCV records from Hyperliquid for {symbol}")
    return data


def fetch_order_book(symbol: str) -> List[RawMarketData]:
    """
    Simulate fetching order book snapshot from Hyperliquid.
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USD')
    
    Returns:
        List of RawMarketData objects with bid/ask data
    """
    logger.debug(f"Fetching order book from Hyperliquid for {symbol}")
    
    data = []
    base_price = {'BTC/USD': 45000, 'ETH/USD': 2500, 'SOL/USD': 150}.get(symbol, 100)
    
    for i in range(3):
        timestamp = time.time() - (3 - i) * 60
        mid_price = base_price + random.uniform(-100, 100)
        
        record = RawMarketData(
            timestamp=timestamp,
            symbol=symbol,
            price=mid_price,
            volume=random.uniform(300000, 1200000),
            bid=mid_price - random.uniform(5, 20),
            ask=mid_price + random.uniform(5, 20),
            source='hyperliquid'
        )
        data.append(record)
    
    logger.info(f"✓ Fetched {len(data)} order book records from Hyperliquid for {symbol}")
    return data


def fetch_liquidations(symbol: str) -> List[RawMarketData]:
    """
    Simulate fetching liquidation data from Hyperliquid.
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USD')
    
    Returns:
        List of RawMarketData objects with liquidation data
    """
    logger.debug(f"Fetching liquidations from Hyperliquid for {symbol}")
    
    data = []
    
    for i in range(4):
        timestamp = time.time() - (4 - i) * 300  # 5-minute intervals
        
        record = RawMarketData(
            timestamp=timestamp,
            symbol=symbol,
            price=random.uniform(42000, 48000),
            volume=random.uniform(5000, 30000),
            liquidations=random.uniform(200000, 800000),
            source='hyperliquid'
        )
        data.append(record)
    
    logger.info(f"✓ Fetched {len(data)} liquidation records from Hyperliquid for {symbol}")
    return data


def ingest_hyperliquid(symbols: List[str]) -> List[RawMarketData]:
    """
    Main ingestion function for Hyperliquid data.
    
    Args:
        symbols: List of trading pairs to ingest
    
    Returns:
        Combined list of RawMarketData objects
    """
    logger.info(f"Starting Hyperliquid ingestion for {len(symbols)} symbols")
    
    all_data = []
    
    for symbol in symbols:
        try:
            all_data.extend(fetch_ohlcv(symbol, limit=5))
            all_data.extend(fetch_order_book(symbol))
            all_data.extend(fetch_liquidations(symbol))
        except Exception as e:
            logger.error(f"Error ingesting Hyperliquid data for {symbol}: {str(e)}")
    
    logger.info(f"✓ Hyperliquid ingestion complete: {len(all_data)} records")
    return all_data
