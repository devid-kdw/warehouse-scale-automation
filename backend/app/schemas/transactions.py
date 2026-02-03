"""Transaction Marshmallow schemas."""
from marshmallow import Schema, fields, validate


class TransactionSchema(Schema):
    """Transaction response schema."""
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
    meta = fields.Dict(allow_none=True)
    # Denormalized fields for convenience
    article_no = fields.String(allow_none=True)
    batch_code = fields.String(allow_none=True)
    location_code = fields.String(allow_none=True)


class TransactionQuerySchema(Schema):
    """Query parameters for listing transactions."""
    article_id = fields.Integer(metadata={'description': 'Filter by article ID'})
    batch_id = fields.Integer(metadata={'description': 'Filter by batch ID'})
    location_id = fields.Integer(metadata={'description': 'Filter by location ID'})
    tx_type = fields.String(
        validate=validate.OneOf(['WEIGH_IN', 'SURPLUS_CONSUMED', 'STOCK_CONSUMED', 'INVENTORY_ADJUSTMENT']),
        metadata={'description': 'Filter by transaction type'}
    )
    from_ = fields.DateTime(
        data_key='from',
        metadata={'description': 'Filter transactions from this datetime (ISO format)'}
    )
    to = fields.DateTime(
        metadata={'description': 'Filter transactions up to this datetime (ISO format)'}
    )
    limit = fields.Integer(
        load_default=100,
        validate=validate.Range(min=1, max=1000),
        metadata={'description': 'Maximum number of results (default 100, max 1000)'}
    )
    offset = fields.Integer(
        load_default=0,
        validate=validate.Range(min=0),
        metadata={'description': 'Offset for pagination'}
    )


class TransactionListSchema(Schema):
    """List of transactions response."""
    items = fields.List(fields.Nested(TransactionSchema))
    total = fields.Integer()
