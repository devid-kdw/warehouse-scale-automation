"""Report Marshmallow schemas."""
from marshmallow import Schema, fields


class InventoryItemSchema(Schema):
    """Single inventory item."""
    location_id = fields.Integer()
    location_code = fields.String()
    article_id = fields.Integer()
    article_no = fields.String()
    batch_id = fields.Integer()
    batch_code = fields.String()
    stock_kg = fields.Float()
    surplus_kg = fields.Float()


class InventoryReportSchema(Schema):
    """Inventory report response."""
    items = fields.List(fields.Nested(InventoryItemSchema))
    total = fields.Integer()
    generated_at = fields.DateTime()


class TransactionItemSchema(Schema):
    """Single transaction item."""
    id = fields.Integer()
    tx_type = fields.String()
    occurred_at = fields.DateTime()
    location_id = fields.Integer()
    article_id = fields.Integer()
    batch_id = fields.Integer()
    quantity_kg = fields.Float()
    user_id = fields.Integer(allow_none=True)
    source = fields.String()
    client_event_id = fields.String(allow_none=True)


class TransactionReportSchema(Schema):
    """Transaction report response."""
    items = fields.List(fields.Nested(TransactionItemSchema))
    total = fields.Integer()
    generated_at = fields.DateTime()


class ReportQuerySchema(Schema):
    """Query parameters for reports."""
    location_id = fields.Integer(metadata={'description': 'Filter by location'})
    article_id = fields.Integer(metadata={'description': 'Filter by article'})
    from_date = fields.Date(metadata={'description': 'Start date'})
    to_date = fields.Date(metadata={'description': 'End date'})
