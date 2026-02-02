"""Approval service - atomic surplus-first approval logic."""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from ..extensions import db
from ..models import WeighInDraft, Stock, Surplus, Transaction, ApprovalAction, User
from ..error_handling import AppError, InsufficientStockError


def approve_draft(draft_id: int, actor_user_id: int, note: Optional[str] = None) -> dict:
    """Approve a weigh-in draft with atomic surplus-first consumption.
    
    This function implements the complete approval workflow:
    1. Validates draft exists and is in DRAFT status
    2. Validates actor user exists
    3. Locks inventory rows (surplus, stock) FOR UPDATE
    4. Applies surplus-first consumption logic
    5. Creates transaction records
    6. Updates draft status
    7. Creates approval action
    
    All operations are atomic - on any error, the entire transaction rolls back.
    
    Args:
        draft_id: ID of the draft to approve
        actor_user_id: ID of the user performing the approval
        note: Optional note for the approval action
        
    Returns:
        dict with approval result:
        {
            'draft_id': int,
            'new_status': 'APPROVED',
            'consumed_surplus_kg': float,
            'consumed_stock_kg': float,
            'transactions': list[dict]
        }
        
    Raises:
        AppError: If draft not found or not in DRAFT status
        AppError: If actor user not found  
        InsufficientStockError: If combined stock + surplus is insufficient
    """
    now = datetime.now(timezone.utc)
    
    # 1. Lock draft FOR UPDATE and validate
    draft = db.session.query(WeighInDraft).filter_by(
        id=draft_id
    ).with_for_update().first()
    
    if not draft:
        raise AppError('DRAFT_NOT_FOUND', f'Draft {draft_id} not found')
    
    if draft.status != WeighInDraft.STATUS_DRAFT:
        raise AppError(
            'DRAFT_NOT_DRAFT',
            f'Cannot approve draft with status {draft.status}',
            {'current_status': draft.status}
        )
    
    # 2. Validate actor user
    user = User.query.get(actor_user_id)
    if not user:
        raise AppError('USER_NOT_FOUND', f'User {actor_user_id} not found')
    
    # 3. Lock or create surplus row FOR UPDATE
    surplus = db.session.query(Surplus).filter_by(
        location_id=draft.location_id,
        article_id=draft.article_id,
        batch_id=draft.batch_id
    ).with_for_update().first()
    
    if not surplus:
        surplus = Surplus(
            location_id=draft.location_id,
            article_id=draft.article_id,
            batch_id=draft.batch_id,
            quantity_kg=Decimal('0')
        )
        db.session.add(surplus)
        db.session.flush()  # Get ID, maintain lock
    
    # 4. Lock or create stock row FOR UPDATE
    stock = db.session.query(Stock).filter_by(
        location_id=draft.location_id,
        article_id=draft.article_id,
        batch_id=draft.batch_id
    ).with_for_update().first()
    
    if not stock:
        stock = Stock(
            location_id=draft.location_id,
            article_id=draft.article_id,
            batch_id=draft.batch_id,
            quantity_kg=Decimal('0')
        )
        db.session.add(stock)
        db.session.flush()
    
    # 5. Calculate surplus-first consumption
    draft_qty = Decimal(str(draft.quantity_kg))
    surplus_qty = Decimal(str(surplus.quantity_kg))
    stock_qty = Decimal(str(stock.quantity_kg))
    
    # How much can we take from surplus?
    use_surplus = min(surplus_qty, draft_qty)
    remaining = draft_qty - use_surplus
    
    # 6. Validate stock is sufficient for remaining
    if stock_qty < remaining:
        raise InsufficientStockError(
            required=float(draft_qty),
            available=float(stock_qty),
            available_surplus=float(surplus_qty)
        )
    
    # 7. Apply inventory updates
    surplus.quantity_kg = surplus_qty - use_surplus
    surplus.updated_at = now
    
    stock.quantity_kg = stock_qty - remaining
    # stock.last_updated auto-updates via onupdate
    
    # 8. Create transaction records
    transactions_created = []
    
    # Always create WEIGH_IN transaction
    tx_weigh_in = Transaction(
        tx_type=Transaction.TX_WEIGH_IN,
        occurred_at=now,
        location_id=draft.location_id,
        article_id=draft.article_id,
        batch_id=draft.batch_id,
        quantity_kg=draft_qty,
        user_id=actor_user_id,
        source=draft.source,
        client_event_id=draft.client_event_id,
        meta={'draft_id': draft_id}
    )
    db.session.add(tx_weigh_in)
    transactions_created.append(tx_weigh_in)
    
    # Create SURPLUS_CONSUMED if surplus was used
    if use_surplus > 0:
        tx_surplus = Transaction(
            tx_type=Transaction.TX_SURPLUS_CONSUMED,
            occurred_at=now,
            location_id=draft.location_id,
            article_id=draft.article_id,
            batch_id=draft.batch_id,
            quantity_kg=-use_surplus,  # Negative for consumption
            user_id=actor_user_id,
            source='approval',
            client_event_id=draft.client_event_id,
            meta={'draft_id': draft_id}
        )
        db.session.add(tx_surplus)
        transactions_created.append(tx_surplus)
    
    # Create STOCK_CONSUMED if stock was used
    if remaining > 0:
        tx_stock = Transaction(
            tx_type=Transaction.TX_STOCK_CONSUMED,
            occurred_at=now,
            location_id=draft.location_id,
            article_id=draft.article_id,
            batch_id=draft.batch_id,
            quantity_kg=-remaining,  # Negative for consumption
            user_id=actor_user_id,
            source='approval',
            client_event_id=draft.client_event_id,
            meta={'draft_id': draft_id}
        )
        db.session.add(tx_stock)
        transactions_created.append(tx_stock)
    
    # 9. Update draft status
    old_status = draft.status
    draft.status = WeighInDraft.STATUS_APPROVED
    
    # 10. Create approval action
    approval_action = ApprovalAction(
        draft_id=draft_id,
        action='APPROVE',
        actor_user_id=actor_user_id,
        old_value={'status': old_status},
        new_value={
            'status': WeighInDraft.STATUS_APPROVED,
            'consumed_surplus_kg': float(use_surplus),
            'consumed_stock_kg': float(remaining)
        },
        note=note
    )
    db.session.add(approval_action)
    
    # Flush to get IDs before returning
    db.session.flush()
    
    return {
        'draft_id': draft_id,
        'new_status': WeighInDraft.STATUS_APPROVED,
        'consumed_surplus_kg': float(use_surplus),
        'consumed_stock_kg': float(remaining),
        'remaining_surplus_kg': float(surplus.quantity_kg),
        'remaining_stock_kg': float(stock.quantity_kg),
        'transactions': [tx.to_dict() for tx in transactions_created],
        'approval_action': approval_action.to_dict()
    }


def reject_draft(draft_id: int, actor_user_id: int, note: Optional[str] = None) -> dict:
    """Reject a weigh-in draft.
    
    No inventory changes occur on rejection.
    
    Args:
        draft_id: ID of the draft to reject
        actor_user_id: ID of the user performing the rejection
        note: Optional note for the rejection
        
    Returns:
        dict with rejection result
        
    Raises:
        AppError: If draft not found or not in DRAFT status
        AppError: If actor user not found
    """
    # Lock draft FOR UPDATE
    draft = db.session.query(WeighInDraft).filter_by(
        id=draft_id
    ).with_for_update().first()
    
    if not draft:
        raise AppError('DRAFT_NOT_FOUND', f'Draft {draft_id} not found')
    
    if draft.status != WeighInDraft.STATUS_DRAFT:
        raise AppError(
            'DRAFT_NOT_DRAFT',
            f'Cannot reject draft with status {draft.status}',
            {'current_status': draft.status}
        )
    
    # Validate actor user
    user = User.query.get(actor_user_id)
    if not user:
        raise AppError('USER_NOT_FOUND', f'User {actor_user_id} not found')
    
    # Update draft status
    old_status = draft.status
    draft.status = WeighInDraft.STATUS_REJECTED
    
    # Create approval action
    approval_action = ApprovalAction(
        draft_id=draft_id,
        action='REJECT',
        actor_user_id=actor_user_id,
        old_value={'status': old_status},
        new_value={'status': WeighInDraft.STATUS_REJECTED},
        note=note
    )
    db.session.add(approval_action)
    db.session.flush()
    
    return {
        'draft_id': draft_id,
        'new_status': WeighInDraft.STATUS_REJECTED,
        'approval_action': approval_action.to_dict()
    }
