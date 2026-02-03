"""Inventory Marshmallow schemas."""
from marshmallow import Schema, fields, validate


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
