"""Draft Group service - atomic group operations."""
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict

from ..extensions import db
from ..models import DraftGroup, WeighInDraft, Stock, Surplus, User, Article, Batch
from ..error_handling import AppError, InsufficientStockError
from .approval_service import approve_draft, reject_draft
from . import batch_service


def _generate_group_name(source: str) -> str:
    """Generate auto-name for draft group.
    
    Format: {Source}_{Counter}-{YYYY-MM-DD}
    Example: AdminDraft_001-2026-02-07
    """
    today = datetime.now(timezone.utc).date()
    today_str = today.strftime('%Y-%m-%d')
    
    # Normalize source for name
    source_prefix = source.replace('ui_', '').replace('_', '').capitalize() + "Draft"
    
    # Count existing groups for this source today
    # We use a localized query. 
    # Note: This is not strictly race-condition proof without a separate counter table,
    # but for draft naming it's acceptable (duplicates allowed in name column if not unique constraint, 
    # but we desire uniqueness).
    # To be safer, we could append random suffix if collision, but let's stick to spec.
    
    start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
    
    count = db.session.query(DraftGroup).filter(
        DraftGroup.source == source,
        DraftGroup.created_at >= start_of_day
    ).count()
    
    counter = count + 1
    return f"{source_prefix}_{counter:03d}-{today_str}"


def create_group(
    location_id: int,
    user_id: int,
    lines: List[Dict],
    name: Optional[str] = None,
    source: str = 'ui_admin'
) -> DraftGroup:
    """Create a group with multiple lines atomically."""
    
    # Auto-name if no name provided
    if not name:
        name = _generate_group_name(source)
    
    group = DraftGroup(
        name=name,
        location_id=location_id,
        created_by_user_id=user_id,
        source=source,
        status=DraftGroup.STATUS_DRAFT
    )
    db.session.add(group)
    db.session.flush() # Get group ID
    
    for line_data in lines:
        # Resolve Article to check is_paint
        article = db.session.get(Article, line_data['article_id'])
        if not article:
             raise AppError('ARTICLE_NOT_FOUND', f"Article {line_data['article_id']} not found")
        
        # Handle Batch ID Logic
        batch_id = line_data.get('batch_id')
        
        if batch_id is None:
            if article.is_paint:
                 raise AppError('BATCH_REQUIRED', f"Batch ID is required for paint article {article.article_no}")
            
            # Consumable: Find or Create 'NA' system batch (using shared service)
            batch = batch_service.get_or_create_system_batch(article.id)
            batch_id = batch.id
        
        # Check for duplicate client_event_id (idempotency)
        existing = WeighInDraft.query.filter_by(
            client_event_id=line_data['client_event_id']
        ).first()
        if existing:
            raise AppError(
                'DUPLICATE_EVENT_ID',
                f"A draft with client_event_id '{line_data['client_event_id']}' already exists",
                {'client_event_id': line_data['client_event_id']}
            )
            
        # Round quantity
        qty = Decimal(str(line_data['quantity_kg'])).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
        
        draft = WeighInDraft(
            draft_group_id=group.id,
            location_id=location_id,
            article_id=line_data['article_id'],
            batch_id=batch_id,
            quantity_kg=qty,
            draft_type=line_data.get('draft_type', WeighInDraft.DRAFT_TYPE_WEIGH_IN),
            client_event_id=line_data['client_event_id'],
            note=line_data.get('note'),
            created_by_user_id=user_id,
            source=source
        )
        db.session.add(draft)
    
    db.session.commit()
    return group


def update_group_name(group_id: int, name: str, actor_user_id: int) -> DraftGroup:
    """Update draft group name."""
    group = db.session.query(DraftGroup).filter_by(id=group_id).first()
    
    if not group:
        raise AppError('GROUP_NOT_FOUND', f'Draft Group {group_id} not found')
        
    # Only allow renaming if DRAFT
    if group.status != DraftGroup.STATUS_DRAFT:
        raise AppError(
            'GROUP_NOT_DRAFT',
            f'Cannot rename group with status {group.status}',
            {'current_status': group.status}
        )
        
    group.name = name
    db.session.commit()
    return group


def approve_group(group_id: int, actor_user_id: int, note: Optional[str] = None) -> Dict:
    """Atomic group approval with pre-checks and row-level locking."""
    
    # 1. Lock group and validate
    group = db.session.query(DraftGroup).filter_by(
        id=group_id
    ).with_for_update().first()
    
    if not group:
        raise AppError('GROUP_NOT_FOUND', f'Draft Group {group_id} not found')
    
    if group.status != DraftGroup.STATUS_DRAFT:
        raise AppError(
            'GROUP_NOT_DRAFT',
            f'Cannot approve group with status {group.status}',
            {'current_status': group.status}
        )
    
    # 2. Get and lock all lines
    drafts = db.session.query(WeighInDraft).filter_by(
        draft_group_id=group_id
    ).with_for_update().all()
    
    if not drafts:
        raise AppError('GROUP_EMPTY', f'Group {group_id} has no lines')
    
    # 3. Pre-check: Sum requirements and lock inventory
    # Consistent locking order by (article_id, batch_id) to prevent deadlocks
    inventory_keys = sorted(list(set(
        (d.article_id, d.batch_id) for d in drafts
    )))
    
    # Requirements mapping: (article_id, batch_id) -> {'weigh_in': Decimal, 'shortage': Decimal}
    needs = {}
    for d in drafts:
        key = (d.article_id, d.batch_id)
        if key not in needs:
            needs[key] = {'WEIGH_IN': Decimal('0'), 'INVENTORY_SHORTAGE': Decimal('0')}
        needs[key][d.draft_type] += Decimal(str(d.quantity_kg))
        
    # Lock Stock and Surplus rows
    locked_stock = {}
    locked_surplus = {}
    
    for art_id, bat_id in inventory_keys:
        # Lock Stock
        stock = db.session.query(Stock).filter_by(
            location_id=group.location_id,
            article_id=art_id,
            batch_id=bat_id
        ).with_for_update().first()
        
        locked_stock[(art_id, bat_id)] = Decimal(str(stock.quantity_kg)) if stock else Decimal('0')
        
        # Lock Surplus
        surplus = db.session.query(Surplus).filter_by(
            location_id=group.location_id,
            article_id=art_id,
            batch_id=bat_id
        ).with_for_update().first()
        
        locked_surplus[(art_id, bat_id)] = Decimal(str(surplus.quantity_kg)) if surplus else Decimal('0')
        
    # 4. Availability Validation (Pre-check)
    for (art_id, bat_id), requirements in needs.items():
        stock_available = locked_stock[(art_id, bat_id)]
        surplus_available = locked_surplus[(art_id, bat_id)]
        
        # WEIGH_IN uses Surplus-First
        weigh_in_needed = requirements['WEIGH_IN']
        shortage_needed = requirements['INVENTORY_SHORTAGE']
        
        # Shortage MUST come from Stock first (as it never uses surplus)
        if stock_available < shortage_needed:
            raise InsufficientStockError(
                required=float(shortage_needed),
                available=float(stock_available),
                available_surplus=0,
                message=f"Insufficient stock for shortage line (Article {art_id}, Batch {bat_id})"
            )
            
        remaining_stock = stock_available - shortage_needed
        
        # Weigh In consumption
        use_surplus = min(surplus_available, weigh_in_needed)
        still_needed = weigh_in_needed - use_surplus
        
        if remaining_stock < still_needed:
            raise InsufficientStockError(
                required=float(weigh_in_needed),
                available=float(remaining_stock),
                available_surplus=float(surplus_available),
                message=f"Insufficient inventory for weigh-in line (Article {art_id}, Batch {bat_id})"
            )

    # 5. Execution: Success guaranteed by pre-check
    results = []
    for d in drafts:
        res = approve_draft(d.id, actor_user_id, note)
        results.append(res)
        
    group.status = DraftGroup.STATUS_APPROVED
    db.session.commit()
    
    return {
        'group_id': group.id,
        'new_status': group.status,
        'results': results
    }


def reject_group(group_id: int, actor_user_id: int, note: Optional[str] = None) -> Dict:
    """Atomic group rejection."""
    
    # 1. Lock group and validate
    group = db.session.query(DraftGroup).filter_by(
        id=group_id
    ).with_for_update().first()
    
    if not group:
        raise AppError('GROUP_NOT_FOUND', f'Draft Group {group_id} not found')
    
    if group.status != DraftGroup.STATUS_DRAFT:
        raise AppError(
            'GROUP_NOT_DRAFT',
            f'Cannot reject group with status {group.status}',
            {'current_status': group.status}
        )
        
    # 2. Get and lock all lines
    drafts = db.session.query(WeighInDraft).filter_by(
        draft_group_id=group_id
    ).with_for_update().all()
    
    results = []
    for d in drafts:
        res = reject_draft(d.id, actor_user_id, note)
        results.append(res)
        
    group.status = DraftGroup.STATUS_REJECTED
    db.session.commit()
    
    return {
        'group_id': group.id,
        'new_status': group.status,
        'results': results
    }
