# Market Data Infrastructure Engine

A production-style Python data engineering project for ingesting, normalizing, and storing financial market data from multiple exchanges.

## Overview

This project implements a modular, scalable market data pipeline that:
- Ingests data from **Binance**, **Hyperliquid**, and **Bitget**
- Normalizes data into a unified schema
- Performs feature engineering (rolling averages, volume aggregation)
- Stores data in SQLite (easily extendable to PostgreSQL)
- Provides structured logging and error handling

## Project Structure

```
market-data-infrastructure-engine/
├── ingestion/
│   ├── binance.py          # Binance API simulation
│   ├── hyperliquid.py      # Hyperliquid API simulation
│   ├── bitget.py           # Bitget API simulation
│
├── models/
│   └── schemas.py          # Data models (Raw, Normalized, Processed)
│
├── database/
│   ├── connection.py       # SQLAlchemy setup and session management
│   └── create_tables.py    # Table schemas (MarketData, ProcessedData)
│
├── processing/
│   ├── normalize.py        # Data normalization logic
│   ├── feature_engineering.py  # Feature computation
│
├── utils/
│   ├── logger.py           # Structured logging
│   ├── config.py           # Configuration management
│
├── main.py                 # Pipeline entrypoint
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Data Types Supported

- **OHLCV** (Open, High, Low, Close, Volume)
- **Open Interest**
- **Funding Rates** (perpetuals)
- **Liquidations**
- **Order Book** (bid/ask snapshots)

## Unified Data Schema

All exchange data is normalized to this structure:

```python
{
    timestamp: float,           # Unix timestamp
    symbol: str,               # Trading pair (e.g., 'BTC/USD')
    price: float,              # Current price
    volume: float,             # Trading volume
    open_interest: float,      # Optional: open interest
    funding_rate: float,       # Optional: funding rate
    liquidations: float,       # Optional: liquidation volume
    source: str                # Exchange name
}
```

## Features

### Ingestion Layer
- Exchange-specific modules for Binance, Hyperliquid, Bitget
- Simulated API responses (easily replaceable with real APIs)
- Automatic timestamp addition
- Error handling per exchange

### Normalization Layer
- Converts exchange-specific formats to unified schema
- Validates critical fields (price, volume, timestamp)
- Removes invalid records
- Handles missing optional fields

### Processing Layer
- **Rolling Averages**: Computes moving averages per symbol
- **Volume Aggregation**: Groups volume by time buckets
- **Missing Value Handling**: Fills or skips incomplete data

### Database Layer
- SQLAlchemy ORM with SQLite backend
- Automatic table creation
- Optimized indexes for query performance
- Two main tables:
  - `market_data`: Normalized records
  - `processed_data`: Feature-engineered records

### Logging
- Structured logging with timestamps
- Log levels: DEBUG, INFO, WARNING, ERROR
- Per-module logger instances
- Clear pipeline execution tracking

## Installation

### Prerequisites
- Python 3.8+

### Setup

```bash
# Clone the repository
git clone https://github.com/Davideddcoder/market-data-infrastructure-engine.git
cd market-data-infrastructure-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Configuration is managed via environment variables (see `utils/config.py`):

```bash
# Database
DATABASE_URL=sqlite:///market_data.db
DATABASE_ECHO=False

# Pipeline
INGESTION_BATCH_SIZE=1000
PROCESSING_WINDOW=5

# Logging
LOG_LEVEL=INFO
```

Or use defaults in `utils/config.py`.

## Usage

### Run the Complete Pipeline

```bash
python main.py
```

This will:
1. Initialize the database
2. Ingest data from all three exchanges
3. Normalize the data
4. Validate records
5. Engineer features
6. Store results in the database
7. Print execution summary

### Example Output

```
================================================================================
MARKET DATA INFRASTRUCTURE PIPELINE
================================================================================

[STEP 1] Initializing database...
✓ Database tables created successfully

[STEP 2] Ingesting data from exchanges...
✓ Fetched 5 OHLCV records from Binance for BTC/USD
✓ Fetched 5 funding rate records from Binance for BTC/USD
...
✓ Total raw records ingested: 189

[STEP 3] Normalizing data...
✓ Normalization complete: 189 successful, 0 errors

[STEP 4] Validating data...
✓ Validation complete: 189 valid, 0 invalid

[STEP 5] Engineering features...
✓ Feature engineering complete: 189 processed records

[STEP 6] Storing normalized data...
✓ Stored 189 normalized records in database

[STEP 7] Storing processed data...
✓ Stored 189 processed records in database

================================================================================
PIPELINE SUMMARY
================================================================================

✓ Execution Time: 0.45s

Ingestion:
  - Binance: 65 records
  - Hyperliquid: 62 records
  - Bitget: 62 records
  - Total: 189 records

Processing:
  - Normalized: 189 records
  - Validated: 189 records
  - Processed: 189 records

Storage:
  - Normalized stored: 189 records
  - Processed stored: 189 records

Symbols: BTC/USD, ETH/USD, SOL/USD
Timestamp: 2025-01-15T10:30:45.123456

================================================================================
✓ PIPELINE COMPLETED SUCCESSFULLY
================================================================================
```

## Extending the Pipeline

### Add a New Exchange

1. Create `ingestion/newexchange.py`:
```python
from models.schemas import RawMarketData

def fetch_ohlcv(symbol: str, limit: int = 10):
    # Implement API calls
    pass

def ingest_newexchange(symbols: list):
    # Orchestrate data fetching
    pass
```

2. Import in `main.py` and add to pipeline:
```python
from ingestion.newexchange import ingest_newexchange
# ...
newexchange_data = ingest_newexchange(symbols)
```

### Customize Features

Edit `processing/feature_engineering.py`:
- Add new rolling statistics
- Implement additional aggregations
- Create custom indicators

### Use PostgreSQL

Update `DATABASE_URL` in `.env`:
```bash
DATABASE_URL=postgresql://user:password@localhost/market_data
```

SQLAlchemy handles the rest automatically.

## Code Quality

- **Type Hints**: Used where helpful for clarity
- **Docstrings**: Every function includes docstrings
- **Error Handling**: Try-catch blocks with logging
- **Logging**: Structured logs at every step
- **No Overengineering**: Clean, readable code

## Performance Considerations

- **Batch Processing**: Records processed in batches
- **Indexed Queries**: Database indexes on common queries
- **Time-based Aggregation**: Efficient volume bucketing
- **Lazy Evaluation**: Features computed on-demand

## Database Schema

### market_data table
```sql
CREATE TABLE market_data (
    id INTEGER PRIMARY KEY,
    timestamp FLOAT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    price FLOAT NOT NULL,
    volume FLOAT NOT NULL,
    open_interest FLOAT,
    funding_rate FLOAT,
    liquidations FLOAT,
    source VARCHAR(50) NOT NULL,
    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_timestamp (symbol, timestamp),
    INDEX idx_source_timestamp (source, timestamp)
);
```

### processed_data table
```sql
CREATE TABLE processed_data (
    id INTEGER PRIMARY KEY,
    timestamp FLOAT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    price FLOAT NOT NULL,
    volume FLOAT NOT NULL,
    rolling_avg_price FLOAT,
    volume_aggregated FLOAT,
    open_interest FLOAT,
    funding_rate FLOAT,
    liquidations FLOAT,
    source VARCHAR(50) NOT NULL,
    features_computed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_timestamp_processed (symbol, timestamp)
);
```

## License

MIT

## Author

Your Name

---

**Last Updated**: 2025-01-15
