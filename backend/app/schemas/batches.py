"""Batch Marshmallow schemas."""
import re
from marshmallow import Schema, fields, validate, validates, ValidationError


# Batch code regex: 4-5 digits (Mankiewicz) or 9-12 digits (Akzo)
BATCH_CODE_PATTERN = r'^\d{4,5}$|^\d{9,12}$'


class BatchSchema(Schema):
    """Batch response schema."""
    id = fields.Integer(dump_only=True)
    article_id = fields.Integer(required=True)
    batch_code = fields.String(required=True)
    received_date = fields.Date(allow_none=True)
    expiry_date = fields.Date(allow_none=True)
    note = fields.String(allow_none=True)
    is_active = fields.Boolean(dump_default=True)
    created_at = fields.DateTime(dump_only=True)


class BatchCreateSchema(Schema):
    """Schema for creating a batch."""
    article_id = fields.Integer(
        required=True,
        metadata={'description': 'ID of the parent article'}
    )
    batch_code = fields.String(
        required=True,
        validate=validate.Regexp(
            BATCH_CODE_PATTERN,
            error='Invalid batch code format. Must be 4-5 digits (Mankiewicz) or 9-12 digits (Akzo).'
        ),
        metadata={'description': '4-5 digits (Mankiewicz) or 9-12 digits (Akzo)'}
    )
    received_date = fields.Date(allow_none=True)
    expiry_date = fields.Date(
        load_default=None,
        metadata={'description': 'Batch expiry date (optional for backward compatibility)'}
    )
    note = fields.String(allow_none=True, validate=validate.Length(max=500))
    is_active = fields.Boolean(load_default=True)


class BatchListSchema(Schema):
    """List of batches response."""
    items = fields.List(fields.Nested(BatchSchema))
    total = fields.Integer()
