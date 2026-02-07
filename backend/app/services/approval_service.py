"""Approval service - atomic surplus-first approval logic."""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from ..extensions import db
from ..models import WeighInDraft, Stock, Surplus, Transaction, ApprovalAction, User
from ..error_handling import AppError, InsufficientStockError


def approve_draft(draft_id: int, actor_user_id: int, note: Optional[str] = None) -> dict:
    """Approve a draft.
    
    Delegates to specific handler based on draft_type:
    - WEIGH_IN: surplus-first consumption (existing logic)
    - INVENTORY_SHORTAGE: stock-only consumption (new logic)
    
    WARNING: THIS FUNCTION DOES NOT COMMIT. Caller is responsible for 
    calling db.session.commit() to finalize the transaction.
    """
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
        
    # Delegate based on type
    if draft.draft_type == WeighInDraft.DRAFT_TYPE_INVENTORY_SHORTAGE:
        return _approve_shortage_draft(draft, actor_user_id, note)
    else:
        # Default to WEIGH_IN logic
        return _approve_weigh_in_draft(draft, actor_user_id, note)


def _approve_weigh_in_draft(draft, actor_user_id, note=None):
    """Surplus-first consumption logic for WEIGH_IN drafts."""
    now = datetime.now(timezone.utc)
    
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
        meta={'draft_id': draft.id}
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
            quantity_kg=-use_surplus,
            user_id=actor_user_id,
            source='approval',
            client_event_id=draft.client_event_id,
            meta={'draft_id': draft.id}
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
            quantity_kg=-remaining,
            user_id=actor_user_id,
            source='approval',
            client_event_id=draft.client_event_id,
            meta={'draft_id': draft.id}
        )
        db.session.add(tx_stock)
        transactions_created.append(tx_stock)
    
    # 9. Update draft status
    old_status = draft.status
    draft.status = WeighInDraft.STATUS_APPROVED
    
    # 10. Create approval action
    approval_action = ApprovalAction(
        draft_id=draft.id,
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
    
    db.session.flush()
    
    return {
        'draft_id': draft.id,
        'new_status': WeighInDraft.STATUS_APPROVED,
        'consumed_surplus_kg': float(use_surplus),
        'consumed_stock_kg': float(remaining),
        'remaining_surplus_kg': float(surplus.quantity_kg),
        'remaining_stock_kg': float(stock.quantity_kg),
        'transactions': [tx.to_dict() for tx in transactions_created],
        'approval_action': approval_action.to_dict()
    }


def _approve_shortage_draft(draft, actor_user_id, note=None):
    """Stock-only consumption logic for INVENTORY_SHORTAGE drafts.
    
    Never touches surplus.
    If stock is insufficient -> INSUFFICIENT_STOCK error.
    """
    now = datetime.now(timezone.utc)
    
    # Lock stock row
    stock = db.session.query(Stock).filter_by(
        location_id=draft.location_id,
        article_id=draft.article_id,
        batch_id=draft.batch_id
    ).with_for_update().first()
    
    stock_qty = Decimal('0')
    if stock:
        stock_qty = Decimal(str(stock.quantity_kg))
    
    draft_qty = Decimal(str(draft.quantity_kg))
    
    # Validate stock sufficiency
    if stock_qty < draft_qty:
        raise InsufficientStockError(
            required=float(draft_qty),
            available=float(stock_qty),
            available_surplus=0  # Shortage approval doesn't use surplus
        )
    
    # Reduce stock
    stock.quantity_kg = stock_qty - draft_qty
    
    # Create INVENTORY_ADJUSTMENT transaction (negative)
    tx = Transaction(
        tx_type=Transaction.TX_INVENTORY_ADJUSTMENT,
        occurred_at=now,
        location_id=draft.location_id,
        article_id=draft.article_id,
        batch_id=draft.batch_id,
        quantity_kg=-draft_qty,
        user_id=actor_user_id,
        source='shortage_approval',
        client_event_id=draft.client_event_id,
        meta={
            'draft_id': draft.id,
            'reason': 'inventory_shortage_approved'
        }
    )
    db.session.add(tx)
    
    # Update draft status
    old_status = draft.status
    draft.status = WeighInDraft.STATUS_APPROVED
    
    # Create approval action
    approval_action = ApprovalAction(
        draft_id=draft.id,
        action='APPROVE',
        actor_user_id=actor_user_id,
        old_value={'status': old_status},
        new_value={
            'status': WeighInDraft.STATUS_APPROVED,
            'consumed_stock_kg': float(draft_qty),
            'consumed_surplus_kg': 0.0
        },
        note=note
    )
    db.session.add(approval_action)
    
    db.session.flush()
    
    return {
        'draft_id': draft.id,
        'new_status': WeighInDraft.STATUS_APPROVED,
        'consumed_surplus_kg': 0.0,
        'consumed_stock_kg': float(draft_qty),
        'remaining_stock_kg': float(stock.quantity_kg),
        'transactions': [tx.to_dict()],
        'approval_action': approval_action.to_dict()
    }


def reject_draft(draft_id: int, actor_user_id: int, note: Optional[str] = None) -> dict:
    """Reject a weigh-in draft.
    
    No inventory changes occur on rejection.
    
    WARNING: THIS FUNCTION DOES NOT COMMIT. Caller is responsible for 
    calling db.session.commit() to finalize the transaction.
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
