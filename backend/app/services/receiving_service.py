"""Receiving service - atomic stock receipt workflow."""
import re
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from ..extensions import db
from ..models import Stock, Transaction, Location, Article, Batch, User
from ..error_handling import AppError


# Batch code regex: 4-5 digits (Mankiewicz) or 9-12 digits (Akzo)
BATCH_CODE_PATTERN = r'^\d{4,5}$|^\d{9,12}$'


def receive_stock(
    article_id: int,
    batch_code: str,
    quantity_kg: Decimal,
    expiry_date: date,
    actor_user_id: int,
    location_id: int = 1,
    received_date: Optional[date] = None,
    note: Optional[str] = None
) -> dict:
    """Receive stock into inventory.
    
    Creates or validates batch, increases stock, creates STOCK_RECEIPT transaction.
    
    Args:
        article_id: Article ID
        batch_code: Batch code (4-5 or 9-12 digits)
        quantity_kg: Quantity to receive (Decimal, must be > 0)
        expiry_date: Required expiry date
        actor_user_id: User ID from JWT token
        location_id: Location ID (default=1, only 1 allowed in v1)
        received_date: Date of receipt (defaults to today)
        note: Optional note
        
    Returns:
        dict with receipt result
        
    Raises:
        AppError: For validation errors
    """
    now = datetime.now(timezone.utc)
    today = date.today()
    
    # Default received_date to today
    if received_date is None:
        received_date = today
    
    # Validate quantity is Decimal and positive
    if not isinstance(quantity_kg, Decimal):
        quantity_kg = Decimal(str(quantity_kg))
    
    quantity_kg = quantity_kg.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    if quantity_kg <= Decimal('0'):
        raise AppError(
            'VALIDATION_ERROR',
            'quantity_kg must be positive',
            {'value': str(quantity_kg)}
        )
    
    # Validate batch code format
    if not re.match(BATCH_CODE_PATTERN, batch_code):
        raise AppError(
            'VALIDATION_ERROR',
            'Invalid batch code format. Must be 4-5 digits (Mankiewicz) or 9-12 digits (Akzo).',
            {'batch_code': batch_code}
        )
    
    # Validate actor user exists and is admin
    user = db.session.get(User, actor_user_id)
    if not user:
        raise AppError('USER_NOT_FOUND', f'User {actor_user_id} not found')
    
    if user.role != 'ADMIN':
        raise AppError(
            'FORBIDDEN',
            'Only ADMIN users can receive stock',
            {'user_role': user.role}
        )
    
    # Validate location exists
    location = db.session.get(Location, location_id)
    if not location:
        raise AppError('LOCATION_NOT_FOUND', f'Location {location_id} not found')
    
    # v1: Only location_id=1 allowed
    if location_id != 1:
        raise AppError(
            'LOCATION_NOT_ALLOWED',
            'Only location ID 1 is allowed in v1',
            {'location_id': location_id}
        )
    
    # Validate article exists
    article = db.session.get(Article, article_id)
    if not article:
        raise AppError('ARTICLE_NOT_FOUND', f'Article {article_id} not found')
    
    # ===== BATCH HANDLING (with lock if exists) =====
    batch_created = False
    
    # Try to find existing batch
    batch = db.session.query(Batch).filter_by(
        article_id=article_id,
        batch_code=batch_code
    ).with_for_update().first()
    
    if batch:
        # Batch exists - check expiry
        if batch.expiry_date is None:
            # Backfill: NULL -> set expiry
            batch.expiry_date = expiry_date
        elif batch.expiry_date != expiry_date:
            # Mismatch -> 409 CONFLICT
            raise AppError(
                'BATCH_EXPIRY_MISMATCH',
                f'Batch {batch_code} already has expiry date {batch.expiry_date}, '
                f'but received {expiry_date}',
                {
                    'batch_code': batch_code,
                    'existing_expiry': batch.expiry_date.isoformat(),
                    'provided_expiry': expiry_date.isoformat()
                }
            )
        # else: same expiry, OK
    else:
        # Create new batch
        batch = Batch(
            article_id=article_id,
            batch_code=batch_code,
            received_date=received_date,
            expiry_date=expiry_date,
            note=note,
            is_active=True
        )
        db.session.add(batch)
        db.session.flush()  # Get ID
        batch_created = True
    
    # ===== STOCK HANDLING (get or create with lock) =====
    stock = db.session.query(Stock).filter_by(
        location_id=location_id,
        article_id=article_id,
        batch_id=batch.id
    ).with_for_update().first()
    
    if not stock:
        stock = Stock(
            location_id=location_id,
            article_id=article_id,
            batch_id=batch.id,
            quantity_kg=Decimal('0')
        )
        db.session.add(stock)
        db.session.flush()
    
    previous_stock = Decimal(str(stock.quantity_kg))
    new_stock = previous_stock + quantity_kg
    stock.quantity_kg = new_stock
    
    # ===== CREATE TRANSACTION =====
    tx = Transaction(
        tx_type=Transaction.TX_STOCK_RECEIPT,
        occurred_at=now,
        location_id=location_id,
        article_id=article_id,
        batch_id=batch.id,
        quantity_kg=quantity_kg,
        user_id=actor_user_id,
        source='receiving',
        meta={
            'note': note,
            'received_date': received_date.isoformat(),
            'batch_created': batch_created
        }
    )
    db.session.add(tx)
    db.session.flush()
    
    return {
        'batch_id': batch.id,
        'batch_created': batch_created,
        'previous_stock': previous_stock,
        'new_stock': new_stock,
        'quantity_received': quantity_kg,
        'transaction': tx.to_dict()
    }
