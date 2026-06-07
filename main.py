"""
Main entrypoint for the market data infrastructure pipeline.

Orchestrates: ingestion → normalization → processing → storage.
"""
import time
from typing import List
from datetime import datetime

from ingestion.binance import ingest_binance
from ingestion.hyperliquid import ingest_hyperliquid
from ingestion.bitget import ingest_bitget

from processing.normalize import normalize_batch, validate_normalized_data
from processing.feature_engineering import engineer_features

from database.create_tables import create_all_tables
from database.connection import get_session
from database.create_tables import MarketData, ProcessedData

from models.schemas import RawMarketData, NormalizedMarketData, ProcessedMarketData
from utils.logger import get_logger
from utils.config import DEFAULT_SYMBOLS

logger = get_logger(__name__)


def store_normalized_data(data: List[NormalizedMarketData]) -> int:
    """
    Store normalized data in the database.
    
    Args:
        data: List of NormalizedMarketData objects
    
    Returns:
        Number of records stored
    """
    session = get_session()
    try:
        stored_count = 0
        
        for record in data:
            db_record = MarketData(
                timestamp=record.timestamp,
                symbol=record.symbol,
                price=record.price,
                volume=record.volume,
                open_interest=record.open_interest,
                funding_rate=record.funding_rate,
                liquidations=record.liquidations,
                source=record.source,
                processed_at=record.processed_at
            )
            session.add(db_record)
            stored_count += 1
        
        session.commit()
        logger.info(f"✓ Stored {stored_count} normalized records in database")
        return stored_count
    
    except Exception as e:
        session.rollback()
        logger.error(f"✗ Failed to store normalized data: {str(e)}")
        return 0
    
    finally:
        session.close()


def store_processed_data(data: List[ProcessedMarketData]) -> int:
    """
    Store processed/feature-engineered data in the database.
    
    Args:
        data: List of ProcessedMarketData objects
    
    Returns:
        Number of records stored
    """
    session = get_session()
    try:
        stored_count = 0
        
        for record in data:
            db_record = ProcessedData(
                timestamp=record.timestamp,
                symbol=record.symbol,
                price=record.price,
                volume=record.volume,
                rolling_avg_price=record.rolling_avg_price,
                volume_aggregated=record.volume_aggregated,
                open_interest=record.open_interest,
                funding_rate=record.funding_rate,
                liquidations=record.liquidations,
                source=record.source,
                features_computed_at=record.features_computed_at
            )
            session.add(db_record)
            stored_count += 1
        
        session.commit()
        logger.info(f"✓ Stored {stored_count} processed records in database")
        return stored_count
    
    except Exception as e:
        session.rollback()
        logger.error(f"✗ Failed to store processed data: {str(e)}")
        return 0
    
    finally:
        session.close()


def run_pipeline(symbols: List[str] = None) -> None:
    """
    Run the complete market data pipeline.
    
    Steps:
        1. Initialize database
        2. Ingest data from all exchanges
        3. Normalize data
        4. Validate data
        5. Engineer features
        6. Store normalized data
        7. Store processed data
        8. Print summary
    
    Args:
        symbols: List of trading pairs (default: DEFAULT_SYMBOLS)
    """
    if symbols is None:
        symbols = DEFAULT_SYMBOLS
    
    start_time = time.time()
    logger.info("=" * 80)
    logger.info("MARKET DATA INFRASTRUCTURE PIPELINE")
    logger.info("=" * 80)
    
    try:
        # Step 1: Initialize database
        logger.info("\n[STEP 1] Initializing database...")
        create_all_tables()
        
        # Step 2: Ingest data
        logger.info("\n[STEP 2] Ingesting data from exchanges...")
        
        binance_data = ingest_binance(symbols)
        hyperliquid_data = ingest_hyperliquid(symbols)
        bitget_data = ingest_bitget(symbols)
        
        raw_data = binance_data + hyperliquid_data + bitget_data
        logger.info(f"✓ Total raw records ingested: {len(raw_data)}")
        
        # Step 3: Normalize data
        logger.info("\n[STEP 3] Normalizing data...")
        normalized_data = normalize_batch(raw_data)
        
        # Step 4: Validate data
        logger.info("\n[STEP 4] Validating data...")
        validated_data = validate_normalized_data(normalized_data)
        
        # Step 5: Engineer features
        logger.info("\n[STEP 5] Engineering features...")
        processed_data = engineer_features(validated_data, rolling_window=5)
        
        # Step 6: Store normalized data
        logger.info("\n[STEP 6] Storing normalized data...")
        normalized_stored = store_normalized_data(validated_data)
        
        # Step 7: Store processed data
        logger.info("\n[STEP 7] Storing processed data...")
        processed_stored = store_processed_data(processed_data)
        
        # Step 8: Print summary
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE SUMMARY")
        logger.info("=" * 80)
        
        elapsed = time.time() - start_time
        
        summary = f"""
        ✓ Execution Time: {elapsed:.2f}s
        
        Ingestion:
          - Binance: {len(binance_data)} records
          - Hyperliquid: {len(hyperliquid_data)} records
          - Bitget: {len(bitget_data)} records
          - Total: {len(raw_data)} records
        
        Processing:
          - Normalized: {len(normalized_data)} records
          - Validated: {len(validated_data)} records
          - Processed: {len(processed_data)} records
        
        Storage:
          - Normalized stored: {normalized_stored} records
          - Processed stored: {processed_stored} records
        
        Symbols: {', '.join(symbols)}
        Timestamp: {datetime.utcnow().isoformat()}
        """
        
        logger.info(summary)
        logger.info("=" * 80)
        logger.info("✓ PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
    
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"✗ PIPELINE FAILED after {elapsed:.2f}s")
        logger.error(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    run_pipeline(symbols=DEFAULT_SYMBOLS)
