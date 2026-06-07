````markdown name=README.md
# Market Data Infrastructure Engine

A modular Python application that demonstrates a complete data pipeline for ingesting, normalizing, and storing market data from multiple simulated exchange sources.

---

## Overview

This project implements an ETL (Extract-Transform-Load) pipeline that:

1. **Ingests** data from three simulated cryptocurrency exchanges
2. **Normalizes** data from different sources into a consistent schema
3. **Processes** data by computing derived metrics
4. **Stores** results in a relational database

The pipeline is designed with layered architecture, allowing each stage to be modified independently.

---

## Features

- **Multi-source ingestion**: Simulated data feeds from Binance, Hyperliquid, and Bitget
- **Data types**: OHLCV, funding rates, liquidations, order book snapshots, open interest
- **Unified schema**: Converts exchange-specific formats to a standardized structure
- **Data validation**: Filters records with missing or invalid critical fields
- **Feature computation**: Rolling averages and volume aggregation per symbol
- **Database persistence**: SQLAlchemy ORM with SQLite backend
- **Structured logging**: Per-module logging with timestamps
- **Configuration management**: Environment variable support for deployment flexibility

---

## Architecture

### Ingestion Layer

Located in `ingestion/`:

- **binance.py**: Simulates OHLCV candles, perpetual funding rates, and liquidation data
- **hyperliquid.py**: Simulates spot market candles, order book snapshots, and liquidations
- **bitget.py**: Simulates perpetual candles, funding rates, and ticker data

Each module contains functions that generate random market data with realistic variance around base prices. Data is returned as `RawMarketData` objects with fields: timestamp, symbol, price, volume, and optional fields (open_interest, funding_rate, liquidations, bid, ask).

### Normalization Layer

Located in `processing/normalize.py`:

- **normalize_batch()**: Converts `RawMarketData` objects to `NormalizedMarketData` objects
- **validate_normalized_data()**: Filters records where price ≤ 0, volume < 0, or timestamp ≤ 0

All normalized records contain: timestamp, symbol, price, volume, source exchange, and optional fields standardized to float values or None.

### Processing Layer

Located in `processing/feature_engineering.py`:

- **handle_missing_values()**: Fills None values in optional fields with 0.0
- **compute_rolling_average()**: Calculates moving average price per symbol using a configurable window (default: 5 records)
- **aggregate_volume()**: Groups volume by time buckets per symbol (default: 300-second buckets)
- **engineer_features()**: Orchestrates all transformations and returns `ProcessedMarketData` objects

Processed records include original fields plus: rolling_avg_price, volume_aggregated, and features_computed_at timestamp.

### Database Layer

Located in `database/`:

- **connection.py**: SQLAlchemy engine initialization and session management
- **create_tables.py**: ORM model definitions (MarketData, ProcessedData) with compound indexes

Two tables are created:
- `market_data`: Stores normalized records (120+ rows per execution)
- `processed_data`: Stores feature-engineered records (120+ rows per execution)

Indexes on (symbol, timestamp) for both tables optimize common query patterns.

### Logging Layer

Located in `utils/logger.py`:

- Configurable per-module logger instances
- Structured format: [TIMESTAMP] [LEVEL] [MODULE] Message
- Log levels: DEBUG, INFO, WARNING, ERROR

### Configuration Layer

Located in `utils/config.py`:

- DATABASE_URL: Controls database backend (default: SQLite)
- INGESTION_BATCH_SIZE: Batch size configuration (unused in current implementation)
- PROCESSING_WINDOW: Rolling window size
- DEFAULT_SYMBOLS: Default trading pairs to ingest
- LOG_LEVEL: Logging verbosity

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.8+ | Implementation language |
| ORM | SQLAlchemy 2.0.23 | Database abstraction |
| Database | SQLite | Data persistence |
| Data Models | Dataclasses | Type-safe data structures |
| Logging | Python logging | Event tracking |
| Configuration | Environment variables | Runtime configuration |

---

## Project Structure

```
market-data-infrastructure-engine/
│
├── ingestion/
│   ├── __init__.py
│   ├── binance.py           # Binance data simulation
│   ├── hyperliquid.py       # Hyperliquid data simulation
│   └── bitget.py            # Bitget data simulation
│
├── models/
│   ├── __init__.py
│   └── schemas.py           # Data models: RawMarketData, 
│                             # NormalizedMarketData, ProcessedMarketData
│
├── database/
│   ├── __init__.py
│   ├── connection.py        # SQLAlchemy engine, session management
│   └── create_tables.py     # ORM models, table creation
│
├── processing/
│   ├── __init__.py
│   ├── normalize.py         # Data normalization and validation
│   └── feature_engineering.py  # Feature computation and transformation
│
├── utils/
│   ├── __init__.py
│   ├── logger.py            # Logging configuration
│   └── config.py            # Environment-based configuration
│
├── main.py                  # Pipeline orchestration
├── requirements.txt         # Python dependencies
├── .gitignore               # Git exclusions
└── README.md                # This file
```

### Module Responsibilities

| Module | Lines | Responsibility |
|--------|-------|-----------------|
| ingestion/binance.py | ~150 | Simulate OHLCV, funding rates, liquidations |
| ingestion/hyperliquid.py | ~150 | Simulate OHLCV, order book, liquidations |
| ingestion/bitget.py | ~150 | Simulate OHLCV, funding rates, tickers |
| processing/normalize.py | ~100 | Convert to unified schema, validate |
| processing/feature_engineering.py | ~180 | Compute rolling averages, aggregate volume |
| database/connection.py | ~50 | SQLAlchemy setup |
| database/create_tables.py | ~100 | ORM models and indexes |
| models/schemas.py | ~90 | Data class definitions |
| utils/logger.py | ~40 | Logging configuration |
| utils/config.py | ~25 | Configuration variables |
| main.py | ~180 | Pipeline orchestration |

---

## How to Run

### Prerequisites

- Python 3.8 or higher

### Installation

```bash
# Clone repository
git clone https://github.com/Davideddcoder/market-data-infrastructure-engine.git
cd market-data-infrastructure-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Execution

```bash
python main.py
```

---

## Expected Behavior

When executed, the pipeline performs the following operations:

### Step 1: Database Initialization
- Creates SQLite database file (market_data.db)
- Creates market_data and processed_data tables with indexes

### Step 2: Data Ingestion
- Calls ingest_binance(['BTC/USD', 'ETH/USD', 'SOL/USD'])
- Calls ingest_hyperliquid(['BTC/USD', 'ETH/USD', 'SOL/USD'])
- Calls ingest_bitget(['BTC/USD', 'ETH/USD', 'SOL/USD'])
- Generates approximately 120-140 raw records total

Raw data includes:
- Timestamps within the last hour
- Prices around base values: BTC/USD ~45000, ETH/USD ~2500, SOL/USD ~150
- Random price variance: ±400-500 per record
- Volume: 100,000-2,000,000 per record
- Optional fields: funding rates (±0.001), open interest (30M-300M), liquidations (100K-800K)

### Step 3: Normalization
- Converts each RawMarketData record to NormalizedMarketData
- Adds processed_at timestamp
- All records converted successfully (0 errors expected)

### Step 4: Validation
- Filters records by critical field constraints
- Removes records where price ≤ 0, volume < 0, or timestamp ≤ 0
- All records pass validation (0 invalid expected)

### Step 5: Feature Engineering
- Groups records by symbol
- Computes rolling average price (5-record window)
- Aggregates volume into 300-second time buckets
- Creates ProcessedMarketData objects
- Returns same number of records as input

### Step 6: Storage
- Inserts normalized records into market_data table
- Inserts processed records into processed_data table
- Commits transaction

### Output Example

```
================================================================================
MARKET DATA INFRASTRUCTURE PIPELINE
================================================================================

[STEP 1] Initializing database...
✓ Database tables created successfully

[STEP 2] Ingesting data from exchanges...
[2025-01-15 10:30:45] [INFO] [ingestion.binance] Starting Binance ingestion for 3 symbols
[2025-01-15 10:30:45] [INFO] [ingestion.binance] ✓ Fetched 5 OHLCV records from Binance for BTC/USD
[2025-01-15 10:30:45] [INFO] [ingestion.binance] ✓ Fetched 5 funding rate records from Binance for BTC/USD
[2025-01-15 10:30:45] [INFO] [ingestion.binance] ✓ Fetched 3 liquidation records from Binance for BTC/USD
[2025-01-15 10:30:45] [INFO] [ingestion.binance] ✓ Binance ingestion complete: 39 records

[2025-01-15 10:30:45] [INFO] [ingestion.hyperliquid] Starting Hyperliquid ingestion for 3 symbols
[2025-01-15 10:30:45] [INFO] [ingestion.hyperliquid] ✓ Hyperliquid ingestion complete: 36 records

[2025-01-15 10:30:45] [INFO] [ingestion.bitget] Starting Bitget ingestion for 3 symbols
[2025-01-15 10:30:45] [INFO] [ingestion.bitget] ✓ Bitget ingestion complete: 45 records

✓ Total raw records ingested: 120

[STEP 3] Normalizing data...
[2025-01-15 10:30:45] [INFO] [processing.normalize] ✓ Normalization complete: 120 successful, 0 errors

[STEP 4] Validating data...
[2025-01-15 10:30:45] [INFO] [processing.normalize] ✓ Validation complete: 120 valid, 0 invalid

[STEP 5] Engineering features...
[2025-01-15 10:30:45] [INFO] [processing.feature_engineering] ✓ Feature engineering complete: 120 processed records

[STEP 6] Storing normalized data...
[2025-01-15 10:30:45] [INFO] [main] ✓ Stored 120 normalized records in database

[STEP 7] Storing processed data...
[2025-01-15 10:30:45] [INFO] [main] ✓ Stored 120 processed records in database

================================================================================
PIPELINE SUMMARY
================================================================================

✓ Execution Time: 0.34s

Ingestion:
  - Binance: 39 records
  - Hyperliquid: 36 records
  - Bitget: 45 records
  - Total: 120 records

Processing:
  - Normalized: 120 records
  - Validated: 120 records
  - Processed: 120 records

Storage:
  - Normalized stored: 120 records
  - Processed stored: 120 records

Symbols: BTC/USD, ETH/USD, SOL/USD
Timestamp: 2025-01-15T10:30:45.123456

================================================================================
✓ PIPELINE COMPLETED SUCCESSFULLY
================================================================================
```

### Inspection

After execution, data can be inspected:

```bash
# View database schema
sqlite3 market_data.db ".schema"

# Query normalized data
sqlite3 market_data.db "SELECT symbol, COUNT(*) FROM market_data GROUP BY symbol;"

# Query processed data
sqlite3 market_data.db "SELECT symbol, rolling_avg_price FROM processed_data LIMIT 5;"
```

---

## Database Schema

### market_data Table

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
    processed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_timestamp (symbol, timestamp),
    INDEX idx_source_timestamp (source, timestamp)
);
```

Stores normalized records from all exchanges. Compound index on (symbol, timestamp) supports queries filtering by symbol and time range.

### processed_data Table

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
    features_computed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_timestamp_processed (symbol, timestamp)
);
```

Stores feature-engineered records. rolling_avg_price contains the 5-record moving average. volume_aggregated contains the sum of volumes within 300-second time buckets.

---

## Configuration

Configuration values are defined in `utils/config.py` and can be overridden with environment variables:

```bash
# Database backend
DATABASE_URL=sqlite:///market_data.db

# ORM echo (prints SQL statements)
DATABASE_ECHO=False

# Pipeline parameters
INGESTION_BATCH_SIZE=1000
PROCESSING_WINDOW=5

# Logging
LOG_LEVEL=INFO
```

To switch database backends (e.g., PostgreSQL), update DATABASE_URL:

```bash
export DATABASE_URL=postgresql://user:password@localhost/market_data
pip install psycopg2-binary
python main.py
```

No code changes are required; SQLAlchemy handles dialect differences automatically.

---

## Data Models

Three data classes are defined in `models/schemas.py`:

### RawMarketData
Input data from exchanges. Optional fields may be None.

```python
@dataclass
class RawMarketData:
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
```

### NormalizedMarketData
Standardized schema after conversion. All fields are float or None (no mixed types).

```python
@dataclass
class NormalizedMarketData:
    timestamp: float
    symbol: str
    price: float
    volume: float
    source: str
    open_interest: Optional[float] = None
    funding_rate: Optional[float] = None
    liquidations: Optional[float] = None
    processed_at: Optional[float] = None
```

### ProcessedMarketData
Output after feature computation. Includes derived fields.

```python
@dataclass
class ProcessedMarketData:
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
```

---

## Skills Demonstrated

### Data Ingestion
- Multiple data source simulation
- Random data generation with realistic constraints
- Per-source error handling

### API Integration Concepts
- Exchange-agnostic ingestion functions
- Consistent API surface across different data types
- Extension pattern for new sources

### Data Normalization
- Schema conversion between formats
- Field type standardization
- Null value handling

### Data Validation
- Constraint checking (price > 0, volume >= 0)
- Missing field detection
- Data quality reporting

### Database Design
- Relational table schema
- Index strategy for query patterns
- ORM usage for abstraction

### Data Processing
- Rolling window computations
- Time-based aggregation
- Batch processing patterns

### Software Organization
- Layered architecture (ingestion, processing, storage)
- Module separation by concern
- Configuration management
- Logging and observability
- Type annotations

---

## License

MIT

---

**Created**: January 2025
````
