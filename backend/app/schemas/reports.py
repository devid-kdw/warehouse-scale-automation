"""Report Marshmallow schemas."""
from marshmallow import Schema, fields, validate


class InventurnaItemSchema(Schema):
    """Item for inventory count list."""
    article_id = fields.Integer()
    article_no = fields.String()
    description = fields.String(allow_none=True)
    batch_id = fields.Integer()
    batch_code = fields.String()
    stock = fields.Float(metadata={'description': 'Stock quantity (unit)'})
    surplus = fields.Float(metadata={'description': 'Surplus quantity (unit)'})
    total = fields.Float(metadata={'description': 'Total quantity (unit)'})
    # Compatibility
    stock_kg = fields.Float(attribute='stock', dump_only=True)
    surplus_kg = fields.Float(attribute='surplus', dump_only=True)
    total_kg = fields.Float(attribute='total', dump_only=True)
    uom = fields.String()


class SurplusItemSchema(Schema):
    """Item for surplus report."""
    article_no = fields.String()
    description = fields.String(allow_none=True)
    batch_code = fields.String()
    quantity = fields.Float(metadata={'description': 'Surplus quantity (unit)'})
    # Compatibility
    quantity_kg = fields.Float(attribute='quantity', dump_only=True)
    uom = fields.String()
    updated_at = fields.String(allow_none=True)


class ConsumptionStatsSchema(Schema):
    """Item for consumption statistics."""
    article_no = fields.String()
    description = fields.String(allow_none=True)
    quantity = fields.Float(metadata={'description': 'Total consumed (unit)'})
    # Compatibility
    quantity_kg = fields.Float(attribute='quantity', dump_only=True)
    hit_count = fields.Integer()
    uom = fields.String()


class ReorderRiskItemSchema(Schema):
    """Item for reorder risk list."""
    article_no = fields.String()
    description = fields.String(allow_none=True)
    stock = fields.Float(metadata={'description': 'Current stock (unit)'})
    threshold = fields.Float(metadata={'description': 'Reorder threshold (unit)'})
    risk_level = fields.String(validate=validate.OneOf(['RED', 'YELLOW', 'GREEN']))
    # Compatibility
    stock_kg = fields.Float(attribute='stock', dump_only=True)
    uom = fields.String()


# Generic wrappers
class InventurnaReportResponseSchema(Schema):
    items = fields.List(fields.Nested(InventurnaItemSchema))
    total = fields.Integer()
    generated_at = fields.DateTime(dump_default=lambda: None)


class SurplusReportResponseSchema(Schema):
    items = fields.List(fields.Nested(SurplusItemSchema))
    total = fields.Integer()


class ConsumptionReportResponseSchema(Schema):
    items = fields.List(fields.Nested(ConsumptionStatsSchema))
    total = fields.Integer()


class ReorderRiskReportResponseSchema(Schema):
    items = fields.List(fields.Nested(ReorderRiskItemSchema))
    total = fields.Integer()


class TopConsumerSchema(Schema):
    article_no = fields.String()
    description = fields.String(allow_none=True)
    quantity = fields.Float(metadata={'description': 'Total consumed (unit)'})
    hit_count = fields.Integer()
    uom = fields.String()


class ReportingStatsSchema(Schema):
    total_count = fields.Integer()
    status_breakdown = fields.Dict(keys=fields.String(), values=fields.Integer())
    generated_at = fields.String()


# Legacy / Fallback
class TransactionItemSchema(Schema):
    """Single transaction item (Legacy)."""
    id = fields.Integer()
    tx_type = fields.String()
    occurred_at = fields.DateTime()
    location_id = fields.Integer()
    article_id = fields.Integer()
    batch_id = fields.Integer()
    quantity = fields.Float(metadata={'description': 'Transaction quantity (unit)'})
    uom = fields.String()
    # Backward Compatibility
    quantity_kg = fields.Float(attribute='quantity', dump_only=True)
    user_id = fields.Integer(allow_none=True)
    source = fields.String()
    meta = fields.Dict(allow_none=True)


class TransactionReportSchema(Schema):
    """Legacy transaction report response."""
    items = fields.List(fields.Nested(TransactionItemSchema))
    total = fields.Integer()
    generated_at = fields.DateTime()


class ReportQuerySchema(Schema):
    """General query parameters for reports."""
    location_id = fields.Integer(load_default=13)
    article_id = fields.Integer(allow_none=True)
    from_date = fields.Date(allow_none=True)
    to_date = fields.Date(allow_none=True)
    days = fields.Integer(load_default=30)
    include_green = fields.Boolean(load_default=False, metadata={'description': 'Include low-risk items in reorder report'})
    state = fields.String(
        load_default='active',
        validate=validate.OneOf(['active', 'inactive', 'all']),
        metadata={'description': 'Filter by article state'}
    )
