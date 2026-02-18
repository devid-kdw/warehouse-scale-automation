"""Receiving service - atomic stock receipt workflow (v3 unit-aware)."""
import re
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from ..extensions import db
from ..models import Stock, Transaction, Location, Article, Batch, User
from ..models.order import OrderLine
from ..error_handling import AppError


# Batch code regex: 4-5 digits (Mankiewicz) or 9-12 digits (Akzo)
BATCH_CODE_PATTERN = r'^\d{4,5}$|^\d{9,12}$'


def receive_stock(
    article_id: int,
    batch_code: str,
    expiry_date: date,
    actor_user_id: int,
    delivery_note_number: str,
    quantity: Decimal,
    uom: str,
    # --- optional linkage ---
    order_number: Optional[str] = None,
    order_line_id: Optional[int] = None,
    # --- other ---
    location_id: int = 13,
    received_date: Optional[date] = None,
    note: Optional[str] = None,
    client_event_id: Optional[str] = None
) -> dict:
    """Receive stock into inventory (v3 unit-aware).

    Args:
        article_id: Article ID
        batch_code: Batch code (4-5 or 9-12 digits for batch-tracked, NA for others)
        expiry_date: Required expiry date
        actor_user_id: User ID from JWT token
        delivery_note_number: REQUIRED delivery note number for traceability
        quantity: Unit-aware quantity (required)
        uom: Unit of measure (required, article UOM is authoritative)
        order_number: Optional order number
        order_line_id: Optional order line ID for linked receiving
        location_id: Location ID (default=13)
        received_date: Date of receipt (defaults to today)
        note: Required for ad-hoc receiving (when no order_line_id)
        client_event_id: Optional UUID for grouping/idempotency

    Returns:
        dict with receipt result

    Raises:
        AppError: For validation errors
    """
    now = datetime.now(timezone.utc)
    today = date.today()

    if received_date is None:
        received_date = today

    # ===== ARTICLE VALIDATION =====
    article = db.session.get(Article, article_id)
    if not article:
        raise AppError('ARTICLE_NOT_FOUND', f'Article {article_id} not found')

    # Resolve Quantity & UOM
    if quantity is None or uom is None:
         raise AppError('VALIDATION_ERROR', 'quantity and uom are required')
         
    if not isinstance(quantity, Decimal):
        quantity = Decimal(str(quantity))
    quantity = quantity.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    uom = uom.strip().upper()
    
    # Enforce Article UOM Authority (Rule 10/11)
    # Receiving MUST happen in the article's base UOM to avoid conversion drift at the gate.
    if uom != article.uom:
         raise AppError(
             'UOM_MISMATCH', 
             f"Received UOM '{uom}' does not match article UOM '{article.uom}'",
             {'expected': article.uom, 'received': uom}
         )

    if quantity <= Decimal('0'):
        raise AppError(
            'VALIDATION_ERROR',
            'quantity must be positive',
            {'value': str(quantity)}
        )

    # ===== DELIVERY NOTE (Rule 11) =====
    if not delivery_note_number or not delivery_note_number.strip():
        raise AppError(
            'VALIDATION_ERROR',
            'delivery_note_number is required for stock receipt',
            {'delivery_note_number': delivery_note_number}
        )
    delivery_note_number = delivery_note_number.strip()

    # ===== ORDER NUMBER (now optional, Finding #2) =====
    if order_number:
        order_number = order_number.strip().upper()

    # ===== AD-HOC: require note when no order_line_id (Rule 11) =====
    if order_line_id is None and (not note or not note.strip()):
        raise AppError(
            'VALIDATION_ERROR',
            'note is required for ad-hoc receiving (without order_line_id)',
            {}
        )

    # ===== VALIDATE ACTOR =====
    user = db.session.get(User, actor_user_id)
    if not user:
        raise AppError('USER_NOT_FOUND', f'User {actor_user_id} not found')

    if user.role != 'ADMIN':
        raise AppError(
            'FORBIDDEN',
            'Only ADMIN users can receive stock',
            {'user_role': user.role}
        )

    # ===== VALIDATE LOCATION =====
    location = db.session.get(Location, location_id)
    if not location:
        raise AppError('LOCATION_NOT_FOUND', f'Location {location_id} not found')

    if location_id != 13:
        raise AppError(
            'LOCATION_NOT_ALLOWED',
            'Only location ID 13 is allowed in v1',
            {'location_id': location_id}
        )

    # ===== ORDER LINE VALIDATION (Finding #4) =====
    if order_line_id is not None:
        order_line = db.session.get(OrderLine, order_line_id)
        if not order_line:
            raise AppError(
                'NOT_FOUND',
                f'Order line {order_line_id} not found',
                {'order_line_id': order_line_id}
            )
        if order_line.article_id != article_id:
            raise AppError(
                'VALIDATION_ERROR',
                f'Order line {order_line_id} is for article {order_line.article_id}, '
                f'not {article_id}',
                {'order_line_id': order_line_id, 'line_article_id': order_line.article_id,
                 'provided_article_id': article_id}
            )
        if order_line.status == OrderLine.STATUS_REMOVED:
            raise AppError(
                'VALIDATION_ERROR',
                f'Order line {order_line_id} has been removed',
                {'order_line_id': order_line_id, 'status': order_line.status}
            )
        if order_line.order.status != 'OPEN':
            raise AppError(
                'VALIDATION_ERROR',
                f'Order {order_line.order_id} is not OPEN (status: {order_line.order.status})',
                {'order_id': order_line.order_id, 'order_status': order_line.order.status}
            )

    # ===== BATCH HANDLING =====
    if not article.has_batch:
        batch_code = 'N/A'
        expiry_date = date(9999, 12, 31)
    else:
        if not batch_code or not expiry_date:
            raise AppError('BATCH_REQUIRED', f'Article {article.article_no} is batch-tracked. Batch code and expiry date are required.')
            
        if not re.match(BATCH_CODE_PATTERN, batch_code):
            raise AppError(
                'VALIDATION_ERROR',
                'Invalid batch code format. Must be 4-5 digits (Mankiewicz) or 9-12 digits (Akzo).',
                {'batch_code': batch_code}
            )

    batch_created = False

    batch = db.session.query(Batch).filter_by(
        article_id=article_id,
        batch_code=batch_code
    ).with_for_update().first()

    if batch:
        if batch.expiry_date is None:
            batch.expiry_date = expiry_date
        elif batch.expiry_date != expiry_date:
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
    else:
        batch = Batch(
            article_id=article_id,
            batch_code=batch_code,
            received_date=received_date,
            expiry_date=expiry_date,
            note=note if article.has_batch else 'System Batch (Non-batch-tracked)',
            is_active=True
        )
        db.session.add(batch)
        db.session.flush()
        batch_created = True

    # ===== STOCK HANDLING =====
    stock = db.session.query(Stock).filter_by(
        location_id=location_id,
        article_id=article_id,
        batch_id=batch.id
    ).with_for_update().first()

    if not stock:
        # Initial create (Unit Only)
        stock = Stock(
            location_id=location_id,
            article_id=article_id,
            batch_id=batch.id,
            quantity=Decimal('0'),
            uom=uom
        )
        db.session.add(stock)
        db.session.flush()

    previous_stock = Decimal(str(stock.quantity or 0))

    # Write unit-aware quantity
    stock.quantity = (previous_stock + quantity)
    # Ensure UOM consistency on stock row (should match article UOM)
    stock.uom = uom 

    # ===== CREATE TRANSACTION =====
    tx = Transaction(
        tx_type=Transaction.TX_STOCK_RECEIPT,
        occurred_at=now,
        location_id=location_id,
        article_id=article_id,
        batch_id=batch.id,
        quantity=quantity,
        uom=uom,
        user_id=actor_user_id,
        source='receiving',
        order_number=order_number,
        delivery_note_number=delivery_note_number,
        order_line_id=order_line_id,
        client_event_id=client_event_id,

        meta={
            'note': note,
            'received_date': received_date.isoformat(),
            'batch_created': batch_created,
            'delivery_note_number': delivery_note_number,
            'is_consumable': not article.has_batch
        }
    )
    db.session.add(tx)
    db.session.flush()

    # ===== INCREMENT ORDER LINE RECEIVED QTY =====
    if order_line_id is not None:
        from ..services.order_service import increment_received_qty
        increment_received_qty(order_line_id, quantity)

    return {
        'batch_id': batch.id,
        'batch_created': batch_created,
        'previous_stock': previous_stock,
        'new_stock': stock.quantity, # Return unit quantity
        'quantity_received': quantity,
        'uom': uom,
        'delivery_note_number': delivery_note_number,
        'order_line_id': order_line_id,
        'transaction': tx.to_dict()
    }
