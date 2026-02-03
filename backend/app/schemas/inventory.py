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
    expiry_date = fields.Date(allow_none=True)
    stock_qty = fields.Float()
    surplus_qty = fields.Float()
    total_qty = fields.Float()
    updated_at = fields.DateTime(allow_none=True)


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
        load_default=1,
        metadata={'description': 'Location ID (defaults to 1)'}
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
        load_default=1,
        metadata={'description': 'Location ID (defaults to 1, only 1 allowed in v1)'}
    )
    article_id = fields.Integer(
        required=True,
        metadata={'description': 'Article ID'}
    )
    batch_code = fields.String(
        required=True,
        validate=validate.Regexp(
            BATCH_CODE_PATTERN,
            error='Invalid batch code. Must be 4-5 digits (Mankiewicz) or 9-12 digits (Akzo).'
        ),
        metadata={'description': 'Batch code: 4-5 or 9-12 digits'}
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

