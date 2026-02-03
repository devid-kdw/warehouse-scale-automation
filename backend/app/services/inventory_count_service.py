"""Inventory count service - admin inventory count with surplus/shortage logic."""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
import uuid

from ..extensions import db
from ..models import Stock, Surplus, Transaction, WeighInDraft, Location, Article, Batch, User
from ..error_handling import AppError


def perform_inventory_count(
    location_id: int,
    article_id: int,
    batch_id: int,
    counted_total_qty: float,
    actor_user_id: int,
    note: Optional[str] = None,
    client_event_id: Optional[str] = None
) -> dict:
    """Perform inventory count with business logic.
    
    Business rules:
    - CASE A (OVER): counted > current → add delta to surplus
    - CASE B (EQUAL): counted == current → no changes
    - CASE C (UNDER): counted < current → reset surplus to 0, create shortage draft
    
    Args:
        location_id: Location ID
        article_id: Article ID
        batch_id: Batch ID
        counted_total_qty: Total quantity counted by admin
        actor_user_id: Admin user performing the count
        note: Optional note
        client_event_id: Optional client event ID for idempotency
        
    Returns:
        dict with count result
        
    Raises:
        AppError: For validation errors
    """
    now = datetime.now(timezone.utc)
    counted_qty = Decimal(str(counted_total_qty)).quantize(Decimal('0.01'))
    
    # Validate actor is admin
    user = db.session.get(User, actor_user_id)
    if not user:
        raise AppError('USER_NOT_FOUND', f'User {actor_user_id} not found')
    if user.role != 'ADMIN':
        raise AppError('FORBIDDEN', 'Only ADMIN can perform inventory count')
    
    # Validate entities exist
    location = db.session.get(Location, location_id)
    if not location:
        raise AppError('LOCATION_NOT_FOUND', f'Location {location_id} not found')
    
    article = db.session.get(Article, article_id)
    if not article:
        raise AppError('ARTICLE_NOT_FOUND', f'Article {article_id} not found')
    
    batch = db.session.get(Batch, batch_id)
    if not batch:
        raise AppError('BATCH_NOT_FOUND', f'Batch {batch_id} not found')
    
    # Lock and get/create stock row
    stock = db.session.query(Stock).filter_by(
        location_id=location_id,
        article_id=article_id,
        batch_id=batch_id
    ).with_for_update().first()
    
    if not stock:
        stock = Stock(
            location_id=location_id,
            article_id=article_id,
            batch_id=batch_id,
            quantity_kg=Decimal('0')
        )
        db.session.add(stock)
        db.session.flush()
    
    # Lock and get/create surplus row
    surplus = db.session.query(Surplus).filter_by(
        location_id=location_id,
        article_id=article_id,
        batch_id=batch_id
    ).with_for_update().first()
    
    if not surplus:
        surplus = Surplus(
            location_id=location_id,
            article_id=article_id,
            batch_id=batch_id,
            quantity_kg=Decimal('0')
        )
        db.session.add(surplus)
        db.session.flush()
    
    # Calculate current state
    current_stock = Decimal(str(stock.quantity_kg))
    current_surplus = Decimal(str(surplus.quantity_kg))
    current_total = current_stock + current_surplus
    
    transactions_created = []
    result = {
        'previous_stock': float(current_stock),
        'previous_surplus': float(current_surplus),
        'previous_total': float(current_total),
        'counted_total': float(counted_qty),
        'delta': float(counted_qty - current_total),
        'surplus_added': None,
        'surplus_reset': None,
        'shortage_draft_id': None,
        'transactions': []
    }
    
    # Generate client_event_id if not provided
    if not client_event_id:
        client_event_id = f'inventory-count-{uuid.uuid4()}'
    
    # === CASE A: OVER (counted > current) ===
    if counted_qty > current_total:
        delta = counted_qty - current_total
        
        # Add to surplus
        surplus.quantity_kg = current_surplus + delta
        surplus.updated_at = now
        
        # Create transaction
        tx = Transaction(
            tx_type=Transaction.TX_INVENTORY_ADJUSTMENT,
            occurred_at=now,
            location_id=location_id,
            article_id=article_id,
            batch_id=batch_id,
            quantity_kg=delta,
            user_id=actor_user_id,
            source='inventory_count',
            client_event_id=client_event_id,
            meta={
                'reason': 'inventory_count_over',
                'counted_total': float(counted_qty),
                'previous_total': float(current_total),
                'surplus_added': float(delta),
                'note': note
            }
        )
        db.session.add(tx)
        transactions_created.append(tx)
        
        result['result'] = 'over'
        result['surplus_added'] = float(delta)
    
    # === CASE B: EQUAL (counted == current) ===
    elif counted_qty == current_total:
        result['result'] = 'no_change'
    
    # === CASE C: UNDER (counted < current) ===
    else:
        # Step 1: Reset surplus to 0 if positive
        if current_surplus > Decimal('0'):
            tx_surplus_reset = Transaction(
                tx_type=Transaction.TX_INVENTORY_ADJUSTMENT,
                occurred_at=now,
                location_id=location_id,
                article_id=article_id,
                batch_id=batch_id,
                quantity_kg=-current_surplus,
                user_id=actor_user_id,
                source='inventory_count',
                client_event_id=f'{client_event_id}-surplus-reset',
                meta={
                    'reason': 'inventory_count_surplus_reset',
                    'surplus_before': float(current_surplus),
                    'note': note
                }
            )
            db.session.add(tx_surplus_reset)
            transactions_created.append(tx_surplus_reset)
            
            surplus.quantity_kg = Decimal('0')
            surplus.updated_at = now
            
            result['surplus_reset'] = float(current_surplus)
        
        # Step 2: Calculate shortage (deficit)
        shortage = current_total - counted_qty
        
        # Step 3: Create shortage draft (NOT automatically applied to stock)
        shortage_draft = WeighInDraft(
            location_id=location_id,
            article_id=article_id,
            batch_id=batch_id,
            quantity_kg=shortage,
            status=WeighInDraft.STATUS_DRAFT,
            draft_type=WeighInDraft.DRAFT_TYPE_INVENTORY_SHORTAGE,
            created_by_user_id=actor_user_id,
            source='inventory_count',
            client_event_id=f'{client_event_id}-shortage',
            note=f'Inventory count shortage: counted {float(counted_qty)}, expected {float(current_total)}. {note or ""}'.strip()
        )
        db.session.add(shortage_draft)
        db.session.flush()
        
        result['result'] = 'under'
        result['shortage_draft_id'] = shortage_draft.id
    
    db.session.flush()
    result['transactions'] = [tx.to_dict() for tx in transactions_created]
    
    return result
