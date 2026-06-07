"""
Binance market data ingestion module.

Simulates API calls to Binance and returns OHLCV, funding rates, and liquidations.
"""
import random
import time
from typing import List
from datetime import datetime

from models.schemas import RawMarketData
from utils.logger import get_logger

logger = get_logger(__name__)


def fetch_ohlcv(symbol: str, limit: int = 10) -> List[RawMarketData]:
    """
    Simulate fetching OHLCV data from Binance.
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USD')
        limit: Number of candles to fetch
    
    Returns:
        List of RawMarketData objects
    """
    logger.debug(f"Fetching OHLCV data from Binance for {symbol}")
    
    data = []
    base_price = {'BTC/USD': 45000, 'ETH/USD': 2500, 'SOL/USD': 150}.get(symbol, 100)
    
    for i in range(limit):
        timestamp = time.time() - (limit - i) * 60
        price = base_price + random.uniform(-500, 500)
        volume = random.uniform(100000, 1000000)
        
        record = RawMarketData(
            timestamp=timestamp,
            symbol=symbol,
            price=price,
            volume=volume,
            open_interest=random.uniform(50000000, 200000000),
            funding_rate=random.uniform(-0.001, 0.001),
            source='binance'
        )
        data.append(record)
    
    logger.info(f"✓ Fetched {len(data)} OHLCV records from Binance for {symbol}")
    return data


def fetch_funding_rates(symbol: str) -> List[RawMarketData]:
    """
    Simulate fetching funding rates from Binance perpetuals.
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USD')
    
    Returns:
        List of RawMarketData objects with funding rate data
    """
    logger.debug(f"Fetching funding rates from Binance for {symbol}")
    
    data = []
    base_price = {'BTC/USD': 45000, 'ETH/USD': 2500, 'SOL/USD': 150}.get(symbol, 100)
    
    for i in range(5):
        timestamp = time.time() - (5 - i) * 3600  # Hourly data
        
        record = RawMarketData(
            timestamp=timestamp,
            symbol=symbol,
            price=base_price + random.uniform(-200, 200),
            volume=random.uniform(500000, 2000000),
            open_interest=random.uniform(100000000, 300000000),
            funding_rate=random.uniform(-0.0005, 0.0005),
            source='binance'
        )
        data.append(record)
    
    logger.info(f"✓ Fetched {len(data)} funding rate records from Binance for {symbol}")
    return data


def fetch_liquidations(symbol: str) -> List[RawMarketData]:
    """
    Simulate fetching liquidation data from Binance.
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USD')
    
    Returns:
        List of RawMarketData objects with liquidation data
    """
    logger.debug(f"Fetching liquidations from Binance for {symbol}")
    
    data = []
    
    for i in range(3):
        timestamp = time.time() - (3 - i) * 600  # 10-minute intervals
        
        record = RawMarketData(
            timestamp=timestamp,
            symbol=symbol,
            price=random.uniform(40000, 50000),
            volume=random.uniform(10000, 50000),
            liquidations=random.uniform(100000, 500000),
            source='binance'
        )
        data.append(record)
    
    logger.info(f"✓ Fetched {len(data)} liquidation records from Binance for {symbol}")
    return data


def ingest_binance(symbols: List[str]) -> List[RawMarketData]:
    """
    Main ingestion function for Binance data.
    
    Args:
        symbols: List of trading pairs to ingest
    
    Returns:
        Combined list of RawMarketData objects
    """
    logger.info(f"Starting Binance ingestion for {len(symbols)} symbols")
    
    all_data = []
    
    for symbol in symbols:
        try:
            all_data.extend(fetch_ohlcv(symbol, limit=5))
            all_data.extend(fetch_funding_rates(symbol))
            all_data.extend(fetch_liquidations(symbol))
        except Exception as e:
            logger.error(f"Error ingesting Binance data for {symbol}: {str(e)}")
    
    logger.info(f"✓ Binance ingestion complete: {len(all_data)} records")
    return all_data
