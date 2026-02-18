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
    stock = fields.Float(metadata={'description': 'Stock quantity (unit-aware)'})
    surplus = fields.Float(metadata={'description': 'Surplus quantity (unit-aware)'})
    total = fields.Float(metadata={'description': 'Total quantity (unit-aware)'})
    # Backward Compatibility
    stock_qty = fields.Float(attribute='stock', dump_only=True)
    surplus_qty = fields.Float(attribute='surplus', dump_only=True)
    total_qty = fields.Float(attribute='total', dump_only=True)
    uom = fields.String(metadata={'description': 'Unit of Measure'})
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
    """Schema for stock receiving request (v3 unit-aware)."""
    location_id = fields.Integer(
        load_default=13,
        metadata={'description': 'Location ID (defaults to 13, primary warehouse location)'}
    )
    article_id = fields.Integer(
        required=True,
        metadata={'description': 'Article ID'}
    )
    delivery_note_number = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={'description': 'Delivery note number (required for traceability)'}
    )
    # Unit-aware (preferred)
    quantity = fields.Decimal(
        required=True, # Now required in v3
        as_string=True, places=3,
        validate=validate.Range(min=Decimal('0.001')),
        metadata={'description': 'Unit-aware quantity'}
    )
    uom = fields.String(
        required=True, # Now required in v3
        validate=validate.Length(min=1, max=20),
        metadata={'description': 'Unit of measure (article UOM authoritative)'}
    )
    # Compatibility: accept quantity_kg but ignore if quantity present
    quantity_kg = fields.Float(load_default=None, allow_none=True)
    order_number = fields.String(
        load_default=None, allow_none=True,
        validate=validate.Length(max=50),
        metadata={'description': 'Order number (optional — omit for ad-hoc receiving)'}
    )
    order_line_id = fields.Integer(
        load_default=None, allow_none=True,
        metadata={'description': 'Optional order line ID for linked receiving'}
    )
    batch_code = fields.String(
        load_default=None, allow_none=True,
        metadata={'description': 'Batch code: 4-5 or 9-12 digits (Paint) or NA (Consumable)'}
    )
    expiry_date = fields.Date(
        load_default=None, allow_none=True,
        metadata={'description': 'Batch expiry date (required if has_batch=True)'}
    )
    received_date = fields.Date(
        load_default=None,
        metadata={'description': 'Date received (defaults to today)'}
    )
    note = fields.String(
        allow_none=True,
        validate=validate.Length(max=500),
        metadata={'description': 'Note (required for ad-hoc receiving without order_line_id)'}
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
        as_string=True, places=2,
        metadata={'description': 'Stock before receiving'}
    )
    new_stock = fields.Decimal(
        as_string=True, places=2,
        metadata={'description': 'Stock after receiving'}
    )
    quantity_received = fields.Decimal(
        as_string=True, places=3,
        metadata={'description': 'Quantity received (unit-aware)'}
    )
    uom = fields.String(metadata={'description': 'Unit of measure'})
    delivery_note_number = fields.String(metadata={'description': 'Delivery note number'})
    order_line_id = fields.Integer(allow_none=True, metadata={'description': 'Linked order line ID'})
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


class ConsolidatedInventoryItemSchema(Schema):
    """Aggregated inventory item at Article+Batch level."""
    article_id = fields.Integer()
    article_no = fields.String()
    description = fields.String(allow_none=True)
    category = fields.String(allow_none=True)
    uom = fields.String()
    batch_id = fields.Integer()
    batch_code = fields.String()
    expiry_date = fields.String(allow_none=True)
    stock = fields.Float(metadata={'description': 'Stock quantity (unit)'})
    surplus = fields.Float(metadata={'description': 'Surplus quantity (unit)'})
    total = fields.Float(metadata={'description': 'Total quantity (unit)'})
    # Compatibility
    stock_qty = fields.Float(attribute='stock', dump_only=True)
    surplus_qty = fields.Float(attribute='surplus', dump_only=True)
    total_qty = fields.Float(attribute='total', dump_only=True)
    is_active = fields.Boolean()
    updated_at = fields.String(allow_none=True)


class ConsolidatedInventoryQuerySchema(Schema):
    """Query params for consolidated inventory list."""
    location_id = fields.Integer(load_default=13)
    category = fields.String(allow_none=True)
    article_no = fields.String(allow_none=True)
    state = fields.String(
        load_default='active',
        validate=validate.OneOf(['active', 'inactive', 'all'])
    )


class ConsolidatedInventoryResponseSchema(Schema):
    """Response for consolidated inventory list."""
    items = fields.List(fields.Nested(ConsolidatedInventoryItemSchema))
    total = fields.Integer()


class ArticleBatchDetailSchema(Schema):
    """Detail for a single batch under an article."""
    batch_id = fields.Integer()
    batch_code = fields.String()
    expiry_date = fields.String(allow_none=True)
    stock = fields.Float(metadata={'description': 'Stock quantity (unit)'})
    surplus = fields.Float(metadata={'description': 'Surplus quantity (unit)'})
    total = fields.Float(metadata={'description': 'Total quantity (unit)'})
    # Compatibility
    stock_qty = fields.Float(attribute='stock', dump_only=True)
    surplus_qty = fields.Float(attribute='surplus', dump_only=True)
    total_qty = fields.Float(attribute='total', dump_only=True)


class ArticleInspectResponseSchema(Schema):
    """Full detail for article inspection."""
    article = fields.Dict() # Nested(ArticleSchema) but avoid circular import if any
    batches = fields.List(fields.Nested(ArticleBatchDetailSchema))
    activity = fields.Dict(metadata={'description': 'Last activity timestamps'})
