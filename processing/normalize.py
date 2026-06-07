"""
Normalization layer for market data.

Converts raw data from different exchanges into a unified schema.
"""
from typing import List
from datetime import datetime

from models.schemas import RawMarketData, NormalizedMarketData
from utils.logger import get_logger

logger = get_logger(__name__)


def normalize_record(raw: RawMarketData) -> NormalizedMarketData:
    """
    Normalize a single raw market data record.
    
    Args:
        raw: RawMarketData object
    
    Returns:
        NormalizedMarketData object with unified schema
    """
    normalized = NormalizedMarketData(
        timestamp=raw.timestamp,
        symbol=raw.symbol,
        price=float(raw.price),
        volume=float(raw.volume),
        source=raw.source,
        open_interest=float(raw.open_interest) if raw.open_interest else None,
        funding_rate=float(raw.funding_rate) if raw.funding_rate else None,
        liquidations=float(raw.liquidations) if raw.liquidations else None,
        processed_at=datetime.utcnow().timestamp()
    )
    return normalized


def normalize_batch(raw_data: List[RawMarketData]) -> List[NormalizedMarketData]:
    """
    Normalize a batch of raw market data records.
    
    Args:
        raw_data: List of RawMarketData objects
    
    Returns:
        List of NormalizedMarketData objects
    """
    logger.debug(f"Normalizing {len(raw_data)} records")
    
    normalized_data = []
    errors = 0
    
    for record in raw_data:
        try:
            normalized = normalize_record(record)
            normalized_data.append(normalized)
        except Exception as e:
            logger.warning(f"Failed to normalize record {record}: {str(e)}")
            errors += 1
    
    success_count = len(normalized_data)
    logger.info(
        f"✓ Normalization complete: {success_count} successful, {errors} errors"
    )
    
    return normalized_data


def validate_normalized_data(data: List[NormalizedMarketData]) -> List[NormalizedMarketData]:
    """
    Validate and clean normalized data.
    
    Removes records with missing critical fields (price, volume).
    
    Args:
        data: List of NormalizedMarketData objects
    
    Returns:
        Validated list of NormalizedMarketData objects
    """
    logger.debug(f"Validating {len(data)} normalized records")
    
    valid_data = []
    invalid_count = 0
    
    for record in data:
        # Check for critical fields
        if record.price is None or record.price <= 0:
            invalid_count += 1
            continue
        
        if record.volume is None or record.volume < 0:
            invalid_count += 1
            continue
        
        if record.timestamp is None or record.timestamp <= 0:
            invalid_count += 1
            continue
        
        valid_data.append(record)
    
    logger.info(
        f"✓ Validation complete: {len(valid_data)} valid, {invalid_count} invalid"
    )
    
    return valid_data
