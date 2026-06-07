"""
Bitget market data ingestion module.

Simulates API calls to Bitget and returns OHLCV and funding rates.
"""
import random
import time
from typing import List

from models.schemas import RawMarketData
from utils.logger import get_logger

logger = get_logger(__name__)


def fetch_ohlcv(symbol: str, limit: int = 10) -> List[RawMarketData]:
    """
    Simulate fetching OHLCV data from Bitget.
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USD')
        limit: Number of candles to fetch
    
    Returns:
        List of RawMarketData objects
    """
    logger.debug(f"Fetching OHLCV data from Bitget for {symbol}")
    
    data = []
    base_price = {'BTC/USD': 45000, 'ETH/USD': 2500, 'SOL/USD': 150}.get(symbol, 100)
    
    for i in range(limit):
        timestamp = time.time() - (limit - i) * 60
        price = base_price + random.uniform(-400, 400)
        volume = random.uniform(150000, 900000)
        
        record = RawMarketData(
            timestamp=timestamp,
            symbol=symbol,
            price=price,
            volume=volume,
            open_interest=random.uniform(30000000, 160000000),
            funding_rate=random.uniform(-0.0008, 0.0008),
            source='bitget'
        )
        data.append(record)
    
    logger.info(f"✓ Fetched {len(data)} OHLCV records from Bitget for {symbol}")
    return data


def fetch_funding_rates(symbol: str) -> List[RawMarketData]:
    """
    Simulate fetching funding rates from Bitget perpetuals.
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USD')
    
    Returns:
        List of RawMarketData objects with funding rate data
    """
    logger.debug(f"Fetching funding rates from Bitget for {symbol}")
    
    data = []
    base_price = {'BTC/USD': 45000, 'ETH/USD': 2500, 'SOL/USD': 150}.get(symbol, 100)
    
    for i in range(6):
        timestamp = time.time() - (6 - i) * 3600  # Hourly data
        
        record = RawMarketData(
            timestamp=timestamp,
            symbol=symbol,
            price=base_price + random.uniform(-250, 250),
            volume=random.uniform(400000, 1800000),
            open_interest=random.uniform(80000000, 280000000),
            funding_rate=random.uniform(-0.0006, 0.0006),
            source='bitget'
        )
        data.append(record)
    
    logger.info(f"✓ Fetched {len(data)} funding rate records from Bitget for {symbol}")
    return data


def fetch_tickers(symbol: str) -> List[RawMarketData]:
    """
    Simulate fetching ticker data from Bitget.
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USD')
    
    Returns:
        List of RawMarketData objects with ticker data
    """
    logger.debug(f"Fetching tickers from Bitget for {symbol}")
    
    data = []
    base_price = {'BTC/USD': 45000, 'ETH/USD': 2500, 'SOL/USD': 150}.get(symbol, 100)
    
    for i in range(4):
        timestamp = time.time() - (4 - i) * 900  # 15-minute intervals
        
        record = RawMarketData(
            timestamp=timestamp,
            symbol=symbol,
            price=base_price + random.uniform(-350, 350),
            volume=random.uniform(250000, 1100000),
            bid=base_price - random.uniform(10, 25),
            ask=base_price + random.uniform(10, 25),
            source='bitget'
        )
        data.append(record)
    
    logger.info(f"✓ Fetched {len(data)} ticker records from Bitget for {symbol}")
    return data


def ingest_bitget(symbols: List[str]) -> List[RawMarketData]:
    """
    Main ingestion function for Bitget data.
    
    Args:
        symbols: List of trading pairs to ingest
    
    Returns:
        Combined list of RawMarketData objects
    """
    logger.info(f"Starting Bitget ingestion for {len(symbols)} symbols")
    
    all_data = []
    
    for symbol in symbols:
        try:
            all_data.extend(fetch_ohlcv(symbol, limit=5))
            all_data.extend(fetch_funding_rates(symbol))
            all_data.extend(fetch_tickers(symbol))
        except Exception as e:
            logger.error(f"Error ingesting Bitget data for {symbol}: {str(e)}")
    
    logger.info(f"✓ Bitget ingestion complete: {len(all_data)} records")
    return all_data
