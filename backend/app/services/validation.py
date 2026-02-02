"""Validation service - batch codes, quantities, etc."""
import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from flask import current_app

from ..error_handling import AppError


# Batch code regex: 4 digits (Mankiewicz) or 9-10 digits (Akzo)
BATCH_CODE_REGEX = re.compile(r'^\d{4}$|^\d{9,10}$')


def validate_batch_code(batch_code: str) -> bool:
    """Validate batch code format.
    
    Valid formats:
    - 4 digits (Mankiewicz): 0044, 1045, 0667
    - 9-10 digits (Akzo): 292456953, 2924662112
    
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
            'Must be 4 digits (Mankiewicz) or 9-10 digits (Akzo).',
            {'pattern': r'^\d{4}$|^\d{9,10}$', 'value': batch_code}
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
