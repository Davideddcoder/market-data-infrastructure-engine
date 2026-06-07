"""
Feature engineering layer for processed market data.

Computes rolling averages, aggregations, and handles missing values.
"""
from typing import List, Dict
from datetime import datetime
from collections import defaultdict

from models.schemas import NormalizedMarketData, ProcessedMarketData
from utils.logger import get_logger

logger = get_logger(__name__)


def handle_missing_values(data: List[NormalizedMarketData]) -> List[NormalizedMarketData]:
    """
    Handle missing values in normalized data.
    
    For optional fields, keep None. For critical fields, already validated.
    
    Args:
        data: List of NormalizedMarketData objects
    
    Returns:
        Cleaned list with missing values handled
    """
    logger.debug(f"Handling missing values for {len(data)} records")
    
    cleaned = []
    for record in data:
        # Fill missing optional fields with None or 0 depending on field
        if record.open_interest is None:
            record.open_interest = 0.0
        if record.funding_rate is None:
            record.funding_rate = 0.0
        if record.liquidations is None:
            record.liquidations = 0.0
        
        cleaned.append(record)
    
    logger.info(f"✓ Missing values handled for {len(cleaned)} records")
    return cleaned


def compute_rolling_average(
    data: List[NormalizedMarketData],
    window: int = 5
) -> Dict[str, List[float]]:
    """
    Compute rolling average price per symbol.
    
    Args:
        data: List of NormalizedMarketData objects
        window: Window size for rolling average
    
    Returns:
        Dictionary mapping symbol to list of rolling averages
    """
    logger.debug(f"Computing rolling averages with window={window}")
    
    # Group by symbol
    by_symbol: Dict[str, List[NormalizedMarketData]] = defaultdict(list)
    for record in data:
        by_symbol[record.symbol].append(record)
    
    # Sort by timestamp within each symbol
    for symbol in by_symbol:
        by_symbol[symbol].sort(key=lambda x: x.timestamp)
    
    rolling_avgs = {}
    
    for symbol, records in by_symbol.items():
        avgs = []
        for i in range(len(records)):
            # Calculate average of last 'window' records
            start_idx = max(0, i - window + 1)
            window_data = records[start_idx:i+1]
            avg_price = sum(r.price for r in window_data) / len(window_data)
            avgs.append(avg_price)
        
        rolling_avgs[symbol] = avgs
        logger.debug(f"✓ Computed {len(avgs)} rolling averages for {symbol}")
    
    return rolling_avgs


def aggregate_volume(
    data: List[NormalizedMarketData],
    time_bucket: int = 300  # 5 minutes in seconds
) -> Dict[str, List[float]]:
    """
    Aggregate volume by time buckets per symbol.
    
    Args:
        data: List of NormalizedMarketData objects
        time_bucket: Time bucket size in seconds
    
    Returns:
        Dictionary mapping symbol to list of aggregated volumes
    """
    logger.debug(f"Aggregating volume with bucket={time_bucket}s")
    
    # Group by symbol and time bucket
    buckets: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
    
    for record in data:
        bucket_key = int(record.timestamp / time_bucket)
        buckets[record.symbol][bucket_key] += record.volume
    
    aggregated = {}
    
    for symbol, bucket_data in buckets.items():
        sorted_buckets = sorted(bucket_data.items())
        volumes = [vol for _, vol in sorted_buckets]
        aggregated[symbol] = volumes
        logger.debug(f"✓ Aggregated {len(volumes)} volume buckets for {symbol}")
    
    return aggregated


def engineer_features(
    data: List[NormalizedMarketData],
    rolling_window: int = 5
) -> List[ProcessedMarketData]:
    """
    Main feature engineering function.
    
    Applies transformations: rolling averages, volume aggregation, etc.
    
    Args:
        data: List of NormalizedMarketData objects
        rolling_window: Window size for rolling statistics
    
    Returns:
        List of ProcessedMarketData objects
    """
    logger.info(f"Starting feature engineering for {len(data)} records")
    
    # Handle missing values
    cleaned_data = handle_missing_values(data)
    
    # Compute rolling averages
    rolling_avgs = compute_rolling_average(cleaned_data, window=rolling_window)
    
    # Aggregate volumes
    aggregated_vols = aggregate_volume(cleaned_data)
    
    # Create processed records
    processed = []
    by_symbol = defaultdict(list)
    
    for record in cleaned_data:
        by_symbol[record.symbol].append(record)
    
    for symbol, records in by_symbol.items():
        records.sort(key=lambda x: x.timestamp)
        avgs = rolling_avgs.get(symbol, [])
        vols = aggregated_vols.get(symbol, [])
        
        for i, record in enumerate(records):
            rolling_avg = avgs[i] if i < len(avgs) else record.price
            aggregated_vol = vols[i] if i < len(vols) else record.volume
            
            processed_record = ProcessedMarketData(
                timestamp=record.timestamp,
                symbol=record.symbol,
                price=record.price,
                volume=record.volume,
                source=record.source,
                rolling_avg_price=rolling_avg,
                volume_aggregated=aggregated_vol,
                open_interest=record.open_interest,
                funding_rate=record.funding_rate,
                liquidations=record.liquidations,
                features_computed_at=datetime.utcnow().timestamp()
            )
            processed.append(processed_record)
    
    logger.info(f"✓ Feature engineering complete: {len(processed)} processed records")
    return processed
