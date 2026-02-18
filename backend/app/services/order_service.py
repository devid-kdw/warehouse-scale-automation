"""Order service — CRUD, auto-numbering, lifecycle automation."""
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models.order import Order, OrderLine
from ..models import Article
from ..error_handling import AppError


def generate_order_number() -> str:
    """Generate next auto order number ORD-xxxx.

    Only considers existing auto-generated numbers (LIKE 'ORD-%') to avoid
    conflicts with manually entered order numbers.

    Uses Python-side parsing instead of DB-specific regex/substring
    so it works on both PostgreSQL and SQLite.
    """
    rows = db.session.execute(
        db.text("SELECT order_number FROM orders WHERE order_number LIKE 'ORD-%%'")
    ).fetchall()

    max_seq = 0
    for (order_number,) in rows:
        suffix = order_number[4:]  # strip 'ORD-'
        if suffix.isdigit():
            max_seq = max(max_seq, int(suffix))

    return f'ORD-{max_seq + 1:04d}'


def create_order(data: dict, user_id: int) -> Order:
    """Create an order with lines.

    Args:
        data: Validated order data with 'lines' list
        user_id: Creating user ID

    Returns:
        Created Order instance

    Raises:
        AppError: On validation or uniqueness errors
    """
    order_number = data.get('order_number')
    if not order_number:
        order_number = generate_order_number()

    # Validate lines: each article must exist
    lines_data = data.get('lines', [])
    for i, line in enumerate(lines_data):
        article = db.session.get(Article, line['article_id'])
        if not article:
            raise AppError(
                'VALIDATION_ERROR',
                f"Article ID {line['article_id']} not found (line {i})",
                {'line_index': i, 'article_id': line['article_id']}
            )

    order = Order(
        order_number=order_number,
        supplier_code=data.get('supplier_code'),
        supplier_name=data.get('supplier_name'),
        note=data.get('note'),
        status=Order.STATUS_OPEN,
        created_by=user_id,
    )

    for line_data in lines_data:
        line = OrderLine(
            article_id=line_data['article_id'],
            ordered_qty=Decimal(str(line_data['ordered_qty'])),
            received_qty=Decimal('0'),
            uom=line_data['uom'].upper(),
            delivery_date=line_data.get('delivery_date'),
            note=line_data.get('note'),
            status=OrderLine.STATUS_OPEN,
        )
        order.lines.append(line)

    db.session.add(order)

    # Retry on unique constraint violation (race condition with auto-number)
    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        if not data.get('order_number'):
            # Auto-number collision — retry once
            order.order_number = generate_order_number()
            db.session.add(order)
            db.session.flush()
        else:
            raise AppError(
                'CONFLICT',
                f"Order number '{order_number}' already exists",
                {'order_number': order_number}
            )

    return order


def get_order(order_id: int) -> Order:
    """Get order by ID or raise."""
    order = db.session.get(Order, order_id)
    if not order:
        raise AppError('NOT_FOUND', f'Order {order_id} not found', {'order_id': order_id})
    return order


def list_orders(status_filter: str = 'all'):
    """List orders, optionally filtered by status.

    Args:
        status_filter: 'OPEN', 'CLOSED', or 'all'
    """
    q = Order.query.order_by(Order.created_at.desc())
    if status_filter and status_filter.upper() != 'ALL':
        q = q.filter(Order.status == status_filter.upper())
    return q.all()


def update_order(order_id: int, data: dict) -> Order:
    """Update order header and optionally replace lines.

    Args:
        order_id: Order to update
        data: Update data (supplier_code, supplier_name, note, lines)

    Returns:
        Updated Order
    """
    order = get_order(order_id)

    if data.get('supplier_code') is not None:
        order.supplier_code = data['supplier_code']
    if data.get('supplier_name') is not None:
        order.supplier_name = data['supplier_name']
    if data.get('note') is not None:
        order.note = data['note']

    # If lines provided, replace all OPEN lines (keep CLOSED/received lines intact)
    new_lines = data.get('lines')
    if new_lines is not None:
        # Remove existing OPEN lines that will be replaced
        for existing_line in order.lines.filter(OrderLine.status == OrderLine.STATUS_OPEN).all():
            if existing_line.received_qty == 0:
                db.session.delete(existing_line)

        # Add new lines
        for line_data in new_lines:
            article = db.session.get(Article, line_data['article_id'])
            if not article:
                raise AppError(
                    'VALIDATION_ERROR',
                    f"Article ID {line_data['article_id']} not found",
                    {'article_id': line_data['article_id']}
                )
            line = OrderLine(
                order_id=order.id,
                article_id=line_data['article_id'],
                ordered_qty=Decimal(str(line_data['ordered_qty'])),
                received_qty=Decimal('0'),
                uom=line_data['uom'].upper(),
                delivery_date=line_data.get('delivery_date'),
                note=line_data.get('note'),
                status=OrderLine.STATUS_OPEN,
            )
            db.session.add(line)

    db.session.flush()
    recalculate_order_status(order.id)
    return order


def remove_line(order_id: int, line_id: int) -> OrderLine:
    """Soft-remove an order line (set status=REMOVED) and recalculate order status.

    Args:
        order_id: Parent order ID
        line_id: Line to remove

    Returns:
        The removed OrderLine
    """
    order = get_order(order_id)
    line = OrderLine.query.filter_by(id=line_id, order_id=order_id).first()
    if not line:
        raise AppError(
            'NOT_FOUND',
            f'Order line {line_id} not found in order {order_id}',
            {'order_id': order_id, 'line_id': line_id}
        )

    if line.status == OrderLine.STATUS_REMOVED:
        raise AppError(
            'VALIDATION_ERROR',
            f'Line {line_id} is already removed',
            {'line_id': line_id}
        )

    line.status = OrderLine.STATUS_REMOVED
    db.session.flush()
    recalculate_order_status(order.id)
    return line


def recalculate_order_status(order_id: int) -> str:
    """Recalculate order status based on active lines (Rule 12).

    - All active lines received_qty >= ordered_qty → CLOSED
    - Any active line unfulfilled → OPEN
    - No active lines → CLOSED

    Returns:
        New status string
    """
    order = db.session.get(Order, order_id)
    if not order:
        return 'OPEN'

    active_lines = db.session.query(OrderLine).filter(
        OrderLine.order_id == order_id,
        OrderLine.status != OrderLine.STATUS_REMOVED
    ).all()

    if not active_lines:
        # All lines removed — close order
        order.status = Order.STATUS_CLOSED
    elif all(Decimal(str(line.received_qty or 0)) >= Decimal(str(line.ordered_qty)) for line in active_lines):
        order.status = Order.STATUS_CLOSED
    else:
        order.status = Order.STATUS_OPEN

    db.session.flush()
    return order.status


def increment_received_qty(order_line_id: int, qty: Decimal) -> OrderLine:
    """Increment received quantity on an order line after receiving.

    Called from receiving_service. Triggers order status recalculation.

    Args:
        order_line_id: OrderLine ID
        qty: Quantity received (positive)

    Returns:
        Updated OrderLine
    """
    line = db.session.get(OrderLine, order_line_id)
    if not line:
        raise AppError(
            'NOT_FOUND',
            f'Order line {order_line_id} not found',
            {'order_line_id': order_line_id}
        )

    line.received_qty = Decimal(str(line.received_qty)) + qty

    # Auto-close line if fully received
    if line.received_qty >= line.ordered_qty:
        line.status = OrderLine.STATUS_CLOSED

    db.session.flush()
    recalculate_order_status(line.order_id)
    return line
