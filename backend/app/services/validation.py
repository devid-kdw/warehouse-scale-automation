"""Validation service - batch codes, quantities, etc."""
import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from flask import current_app

from ..error_handling import AppError


# Batch code regex: 4-5 digits (Mankiewicz) or 9-12 digits (Akzo)
# Valid: 0044, 10455, 292456953, 2924662112, 292466211255
# Invalid: 123, 123456, abc123, 12-34
BATCH_CODE_REGEX = re.compile(r'^\d{4,5}$|^\d{9,12}$')


def validate_batch_code(batch_code: str) -> bool:
    """Validate batch code format.
    
    Valid formats:
    - 4-5 digits (Mankiewicz): 0044, 1045, 10455
    - 9-12 digits (Akzo): 292456953, 2924662112, 292466211255
    
    Invalid examples:
    - 123 (too short)
    - 123456 (in the gap: 6-8 digits)
    - abc123 (non-numeric)
    - 12-34 (contains non-digit)
    
    Args:
        batch_code: The batch code to validate
        
    Returns:
        True if valid
        
    Raises:
        AppError: If invalid format
    """
    if not batch_code:
        raise AppError(
            'INVALID_BATCH_FORMAT',
            'Batch code is required'
        )
    
    if not BATCH_CODE_REGEX.match(batch_code):
        raise AppError(
            'INVALID_BATCH_FORMAT',
            f'Invalid batch code format: {batch_code}. '
            'Must be 4-5 digits (Mankiewicz) or 9-12 digits (Akzo).',
            {'pattern': r'^\d{4,5}$|^\d{9,12}$', 'value': batch_code}
        )
    
    return True


def validate_quantity(quantity: float, field_name: str = 'quantity_kg') -> Decimal:
    """Validate and round quantity to 2 decimal places.
    
    Args:
        quantity: The quantity value
        field_name: Field name for error messages
        
    Returns:
        Rounded Decimal value
        
    Raises:
        AppError: If quantity out of range
    """
    min_qty = current_app.config.get('QUANTITY_MIN', 0.01)
    max_qty = current_app.config.get('QUANTITY_MAX', 9999.99)
    
    if quantity is None:
        raise AppError(
            'VALIDATION_ERROR',
            f'{field_name} is required'
        )
    
    # Round to 2 decimal places using HALF_UP
    rounded = Decimal(str(quantity)).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP
    )
    
    if rounded < Decimal(str(min_qty)):
        raise AppError(
            'VALIDATION_ERROR',
            f'{field_name} must be at least {min_qty}',
            {'min': min_qty, 'value': float(rounded)}
        )
    
    if rounded > Decimal(str(max_qty)):
        raise AppError(
            'VALIDATION_ERROR',
            f'{field_name} must not exceed {max_qty}',
            {'max': max_qty, 'value': float(rounded)}
        )
    
    return rounded


def validate_quantity_adjustment(quantity: float, allow_negative: bool = False) -> Decimal:
    """Validate quantity for inventory adjustments.
    
    Args:
        quantity: The quantity value (can be negative for delta mode)
        allow_negative: Whether to allow negative values
        
    Returns:
        Rounded Decimal value
        
    Raises:
        AppError: If validation fails
    """
    if quantity is None:
        raise AppError(
            'VALIDATION_ERROR',
            'quantity_kg is required'
        )
    
    # Round to 2 decimal places
    rounded = Decimal(str(quantity)).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP
    )
    
    if not allow_negative and rounded < Decimal('0'):
        raise AppError(
            'VALIDATION_ERROR',
            'quantity_kg must be non-negative for set mode',
            {'value': float(rounded)}
        )
    
    return rounded


def validate_client_event_id(client_event_id: Optional[str]) -> str:
    """Validate client_event_id is provided and non-empty.
    
    Args:
        client_event_id: The client event ID
        
    Returns:
        The validated client_event_id
        
    Raises:
        AppError: If missing or empty
    """
    if not client_event_id or not client_event_id.strip():
        raise AppError(
            'VALIDATION_ERROR',
            'client_event_id is required'
        )
    
    return client_event_id.strip()
