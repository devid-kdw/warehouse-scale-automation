"""Inventory services - adjustment, consolidation, and inspection."""
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict
from sqlalchemy import func

from ..extensions import db
from ..models import Stock, Surplus, Transaction, Location, Article, Batch, User
from ..error_handling import AppError


def adjust_inventory(
    location_id: int,
    article_id: int,
    batch_id: int,
    target: str,
    mode: str,
    quantity: float, 
    uom: str,
    actor_user_id: int,
    note: Optional[str] = None
) -> dict:
    """Adjust inventory (stock or surplus) with atomic locking.
    
    Args:
        quantity: Unit-aware quantity (e.g. 10 L, 5 KG)
        uom: Unit of Measure (KG, L, etc.)
    """
    now = datetime.now(timezone.utc)
    
    if target not in ('stock', 'surplus'):
        raise AppError('VALIDATION_ERROR', "target must be 'stock' or 'surplus'")
    
    if mode not in ('set', 'delta'):
        raise AppError('VALIDATION_ERROR', "mode must be 'set' or 'delta'")
    
    qty = Decimal(str(quantity)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    uom = uom.strip().upper()
    
    if mode == 'set' and qty < Decimal('0'):
        raise AppError('VALIDATION_ERROR', 'quantity must be non-negative for set mode')
    
    user = db.session.get(User, actor_user_id)
    if not user:
         raise AppError('USER_NOT_FOUND', f'User {actor_user_id} not found')
    if user.role != 'ADMIN':
        raise AppError('FORBIDDEN', 'Only ADMIN users can perform inventory adjustments')
    
    article = db.session.get(Article, article_id)
    if not article:
        raise AppError('ARTICLE_NOT_FOUND', f'Article {article_id} not found')

    # Validate UOM matches Article UOM (Rule 10/11)
    if uom != article.uom:
         raise AppError('UOM_MISMATCH', f"Adjustment UOM '{uom}' does not match article UOM '{article.uom}'")
    
    if target == 'stock':
        row = db.session.query(Stock).filter_by(
            location_id=location_id, article_id=article_id, batch_id=batch_id
        ).with_for_update().first()
        if not row:
            # Create with 0 quantity
            row = Stock(
                location_id=location_id, 
                article_id=article_id, 
                batch_id=batch_id, 
                quantity=Decimal('0'),
                uom=uom
            )
            db.session.add(row)
    else:
        row = db.session.query(Surplus).filter_by(
            location_id=location_id, article_id=article_id, batch_id=batch_id
        ).with_for_update().first()
        if not row:
            row = Surplus(
                location_id=location_id, 
                article_id=article_id, 
                batch_id=batch_id, 
                quantity=Decimal('0'),
                uom=uom
            )
            db.session.add(row)
    
    previous_value = Decimal(str(row.quantity))
    
    if mode == 'set':
        new_value = qty
        real_delta = new_value - previous_value
    else: # delta
        new_value = previous_value + qty
        real_delta = qty
    
    if new_value < Decimal('0'):
        raise AppError('NEGATIVE_INVENTORY_NOT_ALLOWED', f'Adjustment would result in negative {target}')
    
    row.quantity = new_value
    row.uom = uom # Ensure UOM is set/updated
    
    if target == 'surplus':
        row.updated_at = now
        
    # Unit-Aware Transaction
    tx = Transaction(
        tx_type=Transaction.TX_INVENTORY_ADJUSTMENT,
        occurred_at=now,
        location_id=location_id,
        article_id=article_id,
        batch_id=batch_id,
        quantity=real_delta,
        uom=uom,
        user_id=actor_user_id,
        source='adjustment',
        meta={
            'target': target, 
            'mode': mode, 
            'previous_value': float(previous_value), 
            'new_value': float(new_value), 
            'uom': uom,
            'note': note
        }
    )

    db.session.add(tx)
    return {
        'target': target, 'mode': mode, 
        'previous_value': float(previous_value), 
        'new_value': float(new_value), 
        'delta': float(real_delta),
        'uom': uom,
        'location_id': location_id, 'article_id': article_id, 'batch_id': batch_id,
        'transaction': tx.to_dict()
    }


def get_consolidated_inventory(
    location_id: int,
    category: Optional[str] = None,
    article_no: Optional[str] = None,
    state_filter: str = 'active'
) -> List[Dict]:
    """Get aggregated article list with batch sums and state filters."""
    # Join Batch primarily to get Article+Batch granularity
    query = db.session.query(
        Batch,
        Article,
        func.coalesce(Stock.quantity, 0).label('stock_qty'),
        func.coalesce(Surplus.quantity, 0).label('surplus_qty')
    ).join(
        Article, Batch.article_id == Article.id
    ).outerjoin(
        Stock, (Stock.batch_id == Batch.id) & (Stock.location_id == location_id)
    ).outerjoin(
        Surplus, (Surplus.batch_id == Batch.id) & (Surplus.location_id == location_id)
    )
    
    if category:
        query = query.filter(Article.category == category)
    if article_no:
        query = query.filter(Article.article_no.ilike(f"%{article_no}%"))
        
    if state_filter == 'active':
        query = query.filter(Article.is_active == True)
    elif state_filter == 'inactive':
        query = query.filter(Article.is_active == False)
        
    results = query.order_by(Article.article_no, Batch.batch_code).all()
    
    items = []
    for batch, art, stock_qty, surplus_qty in results:
        # Unit values
        s_qty = float(stock_qty)
        sur_qty = float(surplus_qty)
        t_qty = s_qty + sur_qty
        
        items.append({
            'article_id': art.id,
            'article_no': art.article_no,
            'description': art.description,
            'category': art.category,
            'uom': art.uom,
            'batch_id': batch.id,
            'batch_code': batch.batch_code,
            'expiry_date': batch.expiry_date.isoformat() if batch.expiry_date else None,
            'stock': s_qty,
            'surplus': sur_qty,
            'total': t_qty,
            'is_active': art.is_active,
            'updated_at': batch.updated_at.isoformat() if hasattr(batch, 'updated_at') and batch.updated_at else None
        })
    return items


def get_article_details(article_id: int, location_id: int) -> Dict:
    """Get detailed Article info with batch breakdown and activity dates."""
    article = db.session.get(Article, article_id)
    if not article:
        raise AppError('ARTICLE_NOT_FOUND', f'Article {article_id} not found')
        
    batch_query = db.session.query(
        Batch,
        func.coalesce(Stock.quantity, 0).label('stock_qty'),
        func.coalesce(Surplus.quantity, 0).label('surplus_qty')
    ).outerjoin(
        Stock, (Stock.batch_id == Batch.id) & (Stock.location_id == location_id)
    ).outerjoin(
        Surplus, (Surplus.batch_id == Batch.id) & (Surplus.location_id == location_id)
    ).filter(
        Batch.article_id == article_id
    )
    
    batches = []
    for b, stock_qty, surplus_qty in batch_query.all():
        total_qty = float(stock_qty) + float(surplus_qty)
        if total_qty > 0 or b.is_active:
            batches.append({
                'batch_id': b.id,
                'batch_code': b.batch_code,
                'expiry_date': b.expiry_date.isoformat() if b.expiry_date else None,
                'stock': float(stock_qty),
                'surplus': float(surplus_qty),
                'total': total_qty
            })
            
    last_received = db.session.query(func.max(Transaction.occurred_at)).filter(
        Transaction.article_id == article_id, Transaction.location_id == location_id,
        Transaction.tx_type == Transaction.TX_STOCK_RECEIPT
    ).scalar()
    
    consumption_types = [Transaction.TX_STOCK_CONSUMED, Transaction.TX_SURPLUS_CONSUMED]
    last_issued = db.session.query(func.max(Transaction.occurred_at)).filter(
        Transaction.article_id == article_id, Transaction.location_id == location_id,
        Transaction.tx_type.in_(consumption_types)
    ).scalar()
    
    last_activity = db.session.query(func.max(Transaction.occurred_at)).filter(
        Transaction.article_id == article_id, Transaction.location_id == location_id
    ).scalar()
    
    return {
        'article': article.to_dict(),
        'batches': batches,
        'activity': {
            'last_received_at': last_received.isoformat() if last_received else None,
            'last_issued_at': last_issued.isoformat() if last_issued else None,
            'last_activity_at': last_activity.isoformat() if last_activity else None
        }
    }
