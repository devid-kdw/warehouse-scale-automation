"""Inventory Marshmallow schemas."""
from decimal import Decimal, ROUND_HALF_UP
from marshmallow import Schema, fields, validate


# Batch code regex: 4-5 digits (Mankiewicz) or 9-12 digits (Akzo)
BATCH_CODE_PATTERN = r'^\d{4,5}$|^\d{9,12}$'


class InventorySummaryItemSchema(Schema):
    """Single inventory summary item."""
    location_id = fields.Integer()
    location_code = fields.String()
    article_id = fields.Integer()
    article_no = fields.String()
    description = fields.String(allow_none=True)
    batch_id = fields.Integer()
    batch_code = fields.String()
    expiry_date = fields.String(allow_none=True)
    stock_qty = fields.Float()
    surplus_qty = fields.Float()
    total_qty = fields.Float()
    is_paint = fields.Boolean()
    updated_at = fields.String(allow_none=True)


class InventorySummaryQuerySchema(Schema):
    """Query parameters for inventory summary."""
    article_id = fields.Integer(metadata={'description': 'Filter by article ID'})
    batch_id = fields.Integer(metadata={'description': 'Filter by batch ID'})
    location_id = fields.Integer(metadata={'description': 'Filter by location ID'})


class InventorySummaryResponseSchema(Schema):
    """Inventory summary response."""
    items = fields.List(fields.Nested(InventorySummaryItemSchema))
    total = fields.Integer()


class InventoryCountRequestSchema(Schema):
    """Schema for inventory count request."""
    location_id = fields.Integer(
        load_default=13,
        metadata={'description': 'Location ID (defaults to 13)'}
    )
    article_id = fields.Integer(
        required=True,
        metadata={'description': 'Article ID'}
    )
    batch_id = fields.Integer(
        required=True,
        metadata={'description': 'Batch ID'}
    )
    counted_total_qty = fields.Float(
        required=True,
        validate=validate.Range(min=0),
        metadata={'description': 'Total quantity counted (must be >= 0)'}
    )
    note = fields.String(
        allow_none=True,
        validate=validate.Length(max=500),
        metadata={'description': 'Optional note'}
    )
    client_event_id = fields.String(
        allow_none=True,
        validate=validate.Length(max=100),
        metadata={'description': 'Optional client-generated event ID for idempotency'}
    )


class InventoryCountResponseSchema(Schema):
    """Inventory count response."""
    result = fields.String(metadata={'description': 'Result: over, under, or no_change'})
    previous_stock = fields.Float()
    previous_surplus = fields.Float()
    previous_total = fields.Float()
    counted_total = fields.Float()
    delta = fields.Float()
    # For 'over' case
    surplus_added = fields.Float(allow_none=True)
    # For 'under' case
    surplus_reset = fields.Float(allow_none=True)
    shortage_draft_id = fields.Integer(allow_none=True)
    # Transactions created
    transactions = fields.List(fields.Dict())


class StockReceiveRequestSchema(Schema):
    """Schema for stock receiving request."""
    location_id = fields.Integer(
        load_default=13,
        metadata={'description': 'Location ID (defaults to 13, primary warehouse location)'}
    )
    article_id = fields.Integer(
        required=True,
        metadata={'description': 'Article ID'}
    )
    order_number = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50),
        metadata={'description': 'Order number (e.g. PO-12345)'}
    )
    batch_code = fields.String(
        required=True,
        # Regex validation moved to service layer to allow 'NA' for consumables
        metadata={'description': 'Batch code: 4-5 or 9-12 digits (Paint) or NA (Consumable)'}
    )
    quantity_kg = fields.Decimal(
        required=True,
        as_string=True,
        places=2,
        rounding=ROUND_HALF_UP,
        validate=validate.Range(min=Decimal('0.01')),
        metadata={'description': 'Quantity in kg (must be > 0)'}
    )
    expiry_date = fields.Date(
        required=True,
        metadata={'description': 'Batch expiry date (required)'}
    )
    received_date = fields.Date(
        load_default=None,
        metadata={'description': 'Date received (defaults to today)'}
    )
    note = fields.String(
        allow_none=True,
        validate=validate.Length(max=500),
        metadata={'description': 'Optional note'}
    )
    client_event_id = fields.String(
        allow_none=True,
        validate=validate.Length(max=100),
        metadata={'description': 'Optional client-generated UUID for idempotency'}
    )


class StockReceiveResponseSchema(Schema):
    """Schema for stock receiving response."""
    batch_id = fields.Integer(metadata={'description': 'Batch ID'})
    batch_created = fields.Boolean(metadata={'description': 'True if batch was auto-created'})
    previous_stock = fields.Decimal(
        as_string=True,
        places=2,
        metadata={'description': 'Stock before receiving'}
    )
    new_stock = fields.Decimal(
        as_string=True,
        places=2,
        metadata={'description': 'Stock after receiving'}
    )
    quantity_received = fields.Decimal(
        as_string=True,
        places=2,
        metadata={'description': 'Quantity received'}
    )
    transaction = fields.Dict(metadata={'description': 'STOCK_RECEIPT transaction'})


class ReceiptHistoryItemSchema(Schema):
    """Schema for grouped receipt history item."""
    receipt_key = fields.String(metadata={'description': 'Unique grouping key'})
    order_number = fields.String(allow_none=True)
    received_at = fields.DateTime()
    line_count = fields.Integer()
    total_quantity = fields.Float()
    lines = fields.List(fields.Dict())


class ReceiptHistoryResponseSchema(Schema):
    """Schema for receipt history response."""
    history = fields.List(fields.Nested(ReceiptHistoryItemSchema))
    total = fields.Integer()

