"""Inventory adjustment service - set or delta adjust stock/surplus."""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from ..extensions import db
from ..models import Stock, Surplus, Transaction, Location, Article, Batch, User
from ..error_handling import AppError


def adjust_inventory(
    location_id: int,
    article_id: int,
    batch_id: int,
    target: str,
    mode: str,
    quantity_kg: float,
    actor_user_id: int,
    note: Optional[str] = None
) -> dict:
    """Adjust inventory (stock or surplus) with atomic locking.
    
    Args:
        location_id: Location ID
        article_id: Article ID
        batch_id: Batch ID
        target: 'stock' or 'surplus'
        mode: 'set' (absolute) or 'delta' (relative change)
        quantity_kg: Amount to set or adjust by
        actor_user_id: User performing the adjustment
        note: Optional note for audit
        
    Returns:
        dict with adjustment result
        
    Raises:
        AppError: For validation errors, missing entities
    """
    now = datetime.now(timezone.utc)
    
    # Validate target
    if target not in ('stock', 'surplus'):
        raise AppError(
            'VALIDATION_ERROR',
            "target must be 'stock' or 'surplus'",
            {'value': target}
        )
    
    # Validate mode
    if mode not in ('set', 'delta'):
        raise AppError(
            'VALIDATION_ERROR',
            "mode must be 'set' or 'delta'",
            {'value': mode}
        )
    
    # Validate quantity precision
    qty = Decimal(str(quantity_kg)).quantize(Decimal('0.01'))
    
    # For set mode, quantity must be >= 0
    if mode == 'set' and qty < Decimal('0'):
        raise AppError(
            'VALIDATION_ERROR',
            'quantity_kg must be non-negative for set mode',
            {'value': float(qty)}
        )
    
    # Validate actor user exists and is admin
    user = db.session.get(User, actor_user_id)
    if not user:
        raise AppError('USER_NOT_FOUND', f'User {actor_user_id} not found')
    
    if user.role != 'ADMIN':
        raise AppError(
            'VALIDATION_ERROR',
            'Only ADMIN users can perform inventory adjustments',
            {'user_role': user.role}
        )
    
    # Validate location exists
    location = db.session.get(Location, location_id)
    if not location:
        raise AppError('LOCATION_NOT_FOUND', f'Location {location_id} not found')
    
    # Validate article exists
    article = db.session.get(Article, article_id)
    if not article:
        raise AppError('ARTICLE_NOT_FOUND', f'Article {article_id} not found')
    
    # Validate batch exists
    batch = db.session.get(Batch, batch_id)
    if not batch:
        raise AppError('BATCH_NOT_FOUND', f'Batch {batch_id} not found')
    
    # Get or create target row with lock
    if target == 'stock':
        row = db.session.query(Stock).filter_by(
            location_id=location_id,
            article_id=article_id,
            batch_id=batch_id
        ).with_for_update().first()
        
        if not row:
            row = Stock(
                location_id=location_id,
                article_id=article_id,
                batch_id=batch_id,
                quantity_kg=Decimal('0')
            )
            db.session.add(row)
            db.session.flush()
    else:  # surplus
        row = db.session.query(Surplus).filter_by(
            location_id=location_id,
            article_id=article_id,
            batch_id=batch_id
        ).with_for_update().first()
        
        if not row:
            row = Surplus(
                location_id=location_id,
                article_id=article_id,
                batch_id=batch_id,
                quantity_kg=Decimal('0')
            )
            db.session.add(row)
            db.session.flush()
    
    previous_value = Decimal(str(row.quantity_kg))
    
    # Calculate new value
    if mode == 'set':
        new_value = qty
    else:  # delta
        new_value = previous_value + qty
    
    # Check for negative result
    if new_value < Decimal('0'):
        raise AppError(
            'NEGATIVE_INVENTORY_NOT_ALLOWED',
            f'Adjustment would result in negative {target}: {float(new_value)}kg',
            {
                'target': target,
                'previous_value': float(previous_value),
                'delta': float(qty),
                'would_be': float(new_value)
            }
        )
    
    # Apply the adjustment
    row.quantity_kg = new_value
    if target == 'surplus':
        row.updated_at = now
    # stock.last_updated auto-updates via onupdate
    
    # Calculate delta for transaction (new - old)
    delta_for_tx = new_value - previous_value
    
    # Create transaction record
    tx = Transaction(
        tx_type=Transaction.TX_INVENTORY_ADJUSTMENT,
        occurred_at=now,
        location_id=location_id,
        article_id=article_id,
        batch_id=batch_id,
        quantity_kg=delta_for_tx,
        user_id=actor_user_id,
        source='adjustment',
        meta={
            'target': target,
            'mode': mode,
            'previous_value': float(previous_value),
            'new_value': float(new_value),
            'note': note
        }
    )
    db.session.add(tx)
    db.session.flush()
    
    return {
        'target': target,
        'mode': mode,
        'previous_value': float(previous_value),
        'new_value': float(new_value),
        'delta': float(delta_for_tx),
        'location_id': location_id,
        'article_id': article_id,
        'batch_id': batch_id,
        'transaction': tx.to_dict()
    }
