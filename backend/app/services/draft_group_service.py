"""Draft Group service - atomic group operations."""
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict

from ..extensions import db
from ..models import DraftGroup, WeighInDraft, Stock, Surplus, User, Article, Batch
from ..error_handling import AppError, InsufficientStockError
from .approval_service import approve_draft, reject_draft
from . import batch_service


from sqlalchemy.exc import IntegrityError
import time
import random

def _generate_receipt_number() -> str:
    """Generate sequential receipt number (0001, 0002...).

    Uses Python-side parsing instead of DB-specific string operations
    so it works on both PostgreSQL and SQLite.
    """
    rows = db.session.query(DraftGroup.receipt_number).all()

    max_val = 0
    for (rn,) in rows:
        if rn and rn.isdigit():
            max_val = max(max_val, int(rn))

    return f"{max_val + 1:04d}"


def _generate_group_name(source: str) -> str:
    """Generate auto-name based on source and daily counter."""
    from datetime import date as _date
    today_str = _date.today().strftime('%Y-%m-%d')
    
    prefix = 'AdminDraft' if source == 'ui_admin' else 'OperatorDraft'
    
    # Count existing groups today
    today_count = db.session.query(db.func.count(DraftGroup.id)).filter(
        db.func.date(DraftGroup.created_at) == _date.today()
    ).scalar() or 0
    
    counter = today_count + 1
    return f"{prefix}_{counter:03d}-{today_str}"


def create_group(
    location_id: int,
    user_id: int,
    lines: List[Dict],
    description: Optional[str] = None,
    name: Optional[str] = None, # Legacy alias
    source: str = 'ui_admin'
) -> DraftGroup:
    """Create a group with multiple lines atomically."""
    
    # Map description from legacy name if missing
    final_desc = description or name
    
    # Auto-name if no name/description provided
    if not final_desc:
        final_desc = _generate_group_name(source)
    
    max_retries = 10
    group = None
    
    for attempt in range(max_retries):
        try:
            # Always generate a new receipt number
            receipt_no = _generate_receipt_number()
            
            group = DraftGroup(
                receipt_number=receipt_no,
                description=final_desc,
                name=final_desc,
                location_id=location_id,
                created_by_user_id=user_id,
                source=source,
                status=DraftGroup.STATUS_DRAFT
            )
            db.session.add(group)
            db.session.flush() # Check for unique violation
            break
        except IntegrityError:
            db.session.rollback()
            if attempt == max_retries - 1:
                raise
            # Small random sleep to reduce collision probability on next try
            time.sleep(random.uniform(0.01, 0.05))
            continue
        except Exception:
            db.session.rollback()
            raise
    
    for line_data in lines:
        # Resolve Article to check batch-tracking requirement
        article = db.session.get(Article, line_data['article_id'])
        if not article:
             raise AppError('ARTICLE_NOT_FOUND', f"Article {line_data['article_id']} not found")
        
        # Handle Batch ID Logic (v3: uses has_batch, not is_paint)
        batch_id = line_data.get('batch_id')
        
        if batch_id is None:
            if article.has_batch:
                 raise AppError('BATCH_REQUIRED', f"Batch ID is required for batch-tracked article {article.article_no}")
            
            # Non-batch-tracked: Find or Create 'NA' system batch (using shared service)
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
        
        # Resolve UOM
        uom = line_data.get('uom')
        if not uom:
            uom = article.uom
        
        # Determine quantity field
        # Legacy callers might still send quantity_kg, check for quantity first
        raw_qty = line_data.get('quantity', line_data.get('quantity_kg'))
        if raw_qty is None:
             raise AppError('VALIDATION_ERROR', 'quantity is required')
            
        # Round quantity
        qty = Decimal(str(raw_qty)).quantize(
            Decimal('0.001') if uom in ['L', 'KG'] else Decimal('1.000'), # Higher precision for mass/vol
            rounding=ROUND_HALF_UP
        )
        
        draft = WeighInDraft(
            draft_group_id=group.id,
            location_id=location_id,
            article_id=line_data['article_id'],
            batch_id=batch_id,
            quantity=qty,
            uom=uom,
            draft_type=line_data.get('draft_type', WeighInDraft.DRAFT_TYPE_WEIGH_IN),
            client_event_id=line_data['client_event_id'],
            note=line_data.get('note'),
            created_by_user_id=user_id,
            source=source
        )
        db.session.add(draft)
    
    db.session.commit()
    return group


def update_group_details(group_id: int, name: Optional[str], description: Optional[str], actor_user_id: int) -> DraftGroup:
    """Update draft group name and description."""
    group = db.session.query(DraftGroup).filter_by(id=group_id).first()
    
    if not group:
        raise AppError('GROUP_NOT_FOUND', f'Draft Group {group_id} not found')
        
    # Only allow editing if DRAFT
    if group.status != DraftGroup.STATUS_DRAFT:
        raise AppError(
            'GROUP_NOT_DRAFT',
            f'Cannot edit group with status {group.status}',
            {'current_status': group.status}
        )
        
    if name is not None:
        group.name = name
    if description is not None:
        group.description = description
        
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
        # Sum unit quantities 
        needs[key][d.draft_type] += Decimal(str(d.quantity))
        
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
        
        locked_stock[(art_id, bat_id)] = Decimal(str(stock.quantity)) if stock else Decimal('0')
        
        # Lock Surplus
        surplus = db.session.query(Surplus).filter_by(
            location_id=group.location_id,
            article_id=art_id,
            batch_id=bat_id
        ).with_for_update().first()
        
        locked_surplus[(art_id, bat_id)] = Decimal(str(surplus.quantity)) if surplus else Decimal('0')
        
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
