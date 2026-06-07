"""
Configuration management for the market data pipeline.
"""
import os
from typing import Literal

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///market_data.db')
DATABASE_ECHO = os.getenv('DATABASE_ECHO', 'False').lower() == 'true'

# Pipeline Configuration
INGESTION_BATCH_SIZE = int(os.getenv('INGESTION_BATCH_SIZE', '1000'))
PROCESSING_WINDOW = int(os.getenv('PROCESSING_WINDOW', '5'))  # Rolling window in minutes

# Exchanges
EXCHANGES = ['binance', 'hyperliquid', 'bitget']
DEFAULT_SYMBOLS = ['BTC/USD', 'ETH/USD', 'SOL/USD']

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
