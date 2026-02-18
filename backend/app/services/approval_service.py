from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from ..extensions import db
from ..models import WeighInDraft, Stock, Surplus, Transaction, ApprovalAction, User, Article, Batch
from ..error_handling import AppError, InsufficientStockError


BERLIN_TZ = ZoneInfo('Europe/Berlin')


def get_operational_day(dt: datetime) -> str:
    """Convert UTC datetime to Europe/Berlin operational day string (YYYY-MM-DD)."""
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    berlin_dt = dt.astimezone(BERLIN_TZ)
    return berlin_dt.strftime('%Y-%m-%d')


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
            quantity=Decimal('0'),
            uom=draft.article.uom
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
            quantity=Decimal('0'),
            uom=draft.article.uom
        )
        db.session.add(stock)
        db.session.flush()
    
    # 5. Calculate surplus-first consumption (UNIT-AWARE)
    draft_qty = Decimal(str(draft.quantity))
    surplus_qty = Decimal(str(surplus.quantity))
    stock_qty = Decimal(str(stock.quantity))
    
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
    surplus.quantity = surplus_qty - use_surplus
    surplus.updated_at = now
    
    stock.quantity = stock_qty - remaining
    
    # 8. Create transaction records
    transactions_created = []
    
    # Unit-Aware Transaction Resolution
    resolved_uom = draft.uom
    
    # Always create WEIGH_IN transaction
    # WEIGH_IN is consumption -> Negative sign (Rule 1)

    tx_weigh_in = Transaction(
        tx_type=Transaction.TX_WEIGH_IN,
        occurred_at=now,
        location_id=draft.location_id,
        article_id=draft.article_id,
        batch_id=draft.batch_id,
        quantity=-draft_qty, # Unit-aware
        uom=resolved_uom,
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
            quantity=-use_surplus,
            uom=resolved_uom,
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
            quantity=-remaining,
            uom=resolved_uom,
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
            'consumed_surplus': float(use_surplus),
            'consumed_stock': float(remaining)
        },
        note=note
    )
    db.session.add(approval_action)
    
    db.session.flush()
    
    return {
        'draft_id': draft.id,
        'new_status': WeighInDraft.STATUS_APPROVED,
        'consumed_surplus': float(use_surplus),
        'consumed_stock': float(remaining),
        'remaining_surplus': float(surplus.quantity),
        'remaining_stock': float(stock.quantity),
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
        stock_qty = Decimal(str(stock.quantity))
    
    draft_qty = Decimal(str(draft.quantity))
    
    # Validate stock sufficiency
    if stock_qty < draft_qty:
        raise InsufficientStockError(
            required=float(draft_qty),
            available=float(stock_qty),
            available_surplus=0  # Shortage approval doesn't use surplus
        )
    
    # Reduce stock
    stock.quantity = stock_qty - draft_qty
    
    # Resolve UOM
    resolved_uom = draft.uom

    # Create INVENTORY_ADJUSTMENT transaction (negative)
    tx = Transaction(
        tx_type=Transaction.TX_INVENTORY_ADJUSTMENT,
        occurred_at=now,
        location_id=draft.location_id,
        article_id=draft.article_id,
        batch_id=draft.batch_id,
        quantity=-draft_qty,
        uom=resolved_uom,
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
            'consumed_stock': float(draft_qty),
            'consumed_surplus': 0.0
        },
        note=note
    )
    db.session.add(approval_action)
    
    db.session.flush()
    
    return {
        'draft_id': draft.id,
        'new_status': WeighInDraft.STATUS_APPROVED,
        'consumed_surplus': 0.0,
        'consumed_stock': float(draft_qty),
        'remaining_stock': float(stock.quantity),
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


def get_daily_approvals_list() -> List[Dict]:
    """Get list of operational days with pending DRAFT drafts."""
    drafts = WeighInDraft.query.filter_by(status=WeighInDraft.STATUS_DRAFT).all()
    
    # Group by operational day and location
    days = {}
    for d in drafts:
        day_str = get_operational_day(d.created_at)
        key = (day_str, d.location_id)
        if key not in days:
            days[key] = {
                'date': day_str,
                'location_id': d.location_id,
                'total_lines': 0,
                'total_qty': Decimal('0')
            }
        days[key]['total_lines'] += 1
        days[key]['total_qty'] += Decimal(str(d.quantity or 0))
        
    return sorted(
        [
            {
                'date': v['date'],
                'location_id': v['location_id'],
                'total_lines': v['total_lines'],
                'total_qty': float(v['total_qty'])
            }
            # Unpack key for sorting
            for k, v in days.items()
        ],
        key=lambda x: (x['date'], x['location_id']),
        reverse=True
    )


def get_daily_approvals_detail(date_str: str, location_id: int) -> List[Dict]:
    """Get aggregated detail for a specific operational day and location."""
    drafts = WeighInDraft.query.filter_by(
        status=WeighInDraft.STATUS_DRAFT,
        location_id=location_id
    ).all()
    
    day_drafts = [d for d in drafts if get_operational_day(d.created_at) == date_str]
    
    # Aggregate by article + batch
    groups = {}
    for d in day_drafts:
        key = (d.article_id, d.batch_id)
        article = db.session.get(Article, d.article_id) # Article needed for UOM/Density
        
        if key not in groups:
            groups[key] = {
                'article_id': d.article_id,
                'article_no': article.article_no if article else 'UNKNOWN',
                'article_name': article.description if article else 'UNKNOWN',
                'batch_id': d.batch_id,
                'batch_code': d.batch.batch_code if d.batch else 'NO_BATCH',
                'location_id': location_id,
                'total_qty': Decimal('0'),
                'uom': None,
                'draft_ids': []
            }
        
        # Unit Fallback Rule: use draft.uom or article.uom
        resolved_uom = getattr(d, 'uom', None)
        if not resolved_uom:
            resolved_uom = article.uom if article else 'KG'
            
        # UOM Consistency Validation guard
        if groups[key]['uom'] and groups[key]['uom'] != resolved_uom:
            raise AppError(
                'MIXED_UOM_IN_AGGREGATION',
                f"Mixed UOMs ({groups[key]['uom']} and {resolved_uom}) detected for Article {groups[key]['article_no']}",
                {'article_id': d.article_id, 'batch_id': d.batch_id}
            )
        
        groups[key]['uom'] = resolved_uom
        
        draft_qty = Decimal(str(d.quantity or 0))
        groups[key]['total_qty'] += draft_qty
        groups[key]['draft_ids'].append(d.id)
        
    return sorted(
        [
            {
                'article_id': v['article_id'],
                'article_no': v['article_no'],
                'article_name': v['article_name'],
                'batch_id': v['batch_id'],
                'batch_code': v['batch_code'],
                'location_id': v['location_id'],
                'total_qty': float(v['total_qty']),
                'uom': v['uom'],
                'draft_ids': v['draft_ids']
            }
            for v in groups.values()
        ],
        key=lambda x: x['article_no']
    )


def update_aggregate_quantity(
    date_str: str,
    location_id: int,
    article_id: int,
    batch_id: int,
    new_total_qty: Decimal,
    actor_user_id: int
) -> Dict:
    """Implement First-Draft Delta Adjustment rule (Unit-Aware)."""
    drafts = db.session.query(WeighInDraft).filter_by(
        status=WeighInDraft.STATUS_DRAFT,
        location_id=location_id,
        article_id=article_id,
        batch_id=batch_id
    ).order_by(WeighInDraft.id).with_for_update().all()
    
    day_drafts = [d for d in drafts if get_operational_day(d.created_at) == date_str]
    if not day_drafts:
        raise AppError('NO_DRAFTS_FOUND', 'No pending drafts found for the specified group')
    
    article = db.session.get(Article, article_id)
    if not article:
        raise AppError('ARTICLE_NOT_FOUND', f'Article {article_id} not found')

    # Calculate Sum in units (authoritative)
    current_sum = sum(Decimal(str(d.quantity or 0)) for d in day_drafts)
    delta = new_total_qty - current_sum
    
    if delta == 0:
        return {'status': 'no_change', 'total_qty': float(current_sum)}
        
    target_draft = day_drafts[0]
    old_qty = Decimal(str(target_draft.quantity or 0))
    new_qty = old_qty + delta
    
    if new_qty <= 0:
        raise AppError(
            'INVALID_ADJUSTMENT',
            f"Adjustment would result in non-positive quantity ({new_qty}) for draft {target_draft.id}",
            {'target_draft_id': target_draft.id, 'resulting_qty': float(new_qty)}
        )
        
    # Synchronous Update (quantity only)
    target_draft.quantity = new_qty
    
    # removed quantity_kg logic as column is dropped

    action = ApprovalAction(
        draft_id=target_draft.id,
        action='EDIT',
        actor_user_id=actor_user_id,
        old_value={'quantity': float(old_qty)},
        new_value={'quantity': float(new_qty), 'delta': float(delta)},
        note=f'Aggregate edit for {date_str}'
    )
    db.session.add(action)
    db.session.flush()
    
    return {
        'status': 'updated',
        'target_draft_id': target_draft.id,
        'delta': float(delta),
        'new_total_qty': float(new_total_qty)
    }


def approve_day(date_str: str, location_id: int, actor_user_id: int) -> Dict:
    """Atomic mass approval for a specific day and location.
    
    Uses Deterministic Lock Order (article_id, batch_id) to prevent deadlocks.
    """
    # 1. Find all drafts for the day
    drafts = WeighInDraft.query.filter_by(
        status=WeighInDraft.STATUS_DRAFT,
        location_id=location_id
    ).all()
    
    day_drafts = [d for d in drafts if get_operational_day(d.created_at) == date_str]
    if not day_drafts:
        return {'status': 'nothing_to_approve', 'count': 0}
        
    # 2. Group by Article+Batch for locking order
    # We need a stable order to prevent deadlocks between parallel day approvals
    # ARTICLE_ID ASC, BATCH_ID ASC
    sorted_drafts = sorted(day_drafts, key=lambda x: (x.article_id, x.batch_id, x.id))
    
    results = []
    for d in sorted_drafts:
        # approve_draft handles internal locking FOR UPDATE
        res = approve_draft(d.id, actor_user_id, note=f'Mass approval for {date_str}')
        results.append(res)
        
    return {
        'status': 'success',
        'count': len(results),
        'date': date_str,
        'location_id': location_id
    }


def reject_day(date_str: str, location_id: int, actor_user_id: int) -> Dict:
    """Atomic mass rejection for a specific day and location."""
    drafts = WeighInDraft.query.filter_by(
        status=WeighInDraft.STATUS_DRAFT,
        location_id=location_id
    ).all()
    
    day_drafts = [d for d in drafts if get_operational_day(d.created_at) == date_str]
    if not day_drafts:
        return {'status': 'nothing_to_reject', 'count': 0}
        
    sorted_drafts = sorted(day_drafts, key=lambda x: x.id)
    
    count = 0
    for d in sorted_drafts:
        reject_draft(d.id, actor_user_id, note=f'Mass rejection for {date_str}')
        count += 1
        
    return {
        'status': 'success',
        'count': count,
        'date': date_str,
        'location_id': location_id
    }
