"""Batch Marshmallow schemas."""
import re
from marshmallow import Schema, fields, validate, validates, ValidationError


# Batch code regex: 4 digits (Mankiewicz) or 9-10 digits (Akzo)
BATCH_CODE_PATTERN = r'^\d{4}$|^\d{9,10}$'


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
        metadata={'description': '4 digits (Mankiewicz) or 9-10 digits (Akzo)'}
    )
    received_date = fields.Date(allow_none=True)
    expiry_date = fields.Date(allow_none=True)
    note = fields.String(allow_none=True, validate=validate.Length(max=500))
    is_active = fields.Boolean(load_default=True)
    
    @validates('batch_code')
    def validate_batch_code(self, value):
        """Validate batch code format."""
        if not re.match(BATCH_CODE_PATTERN, value):
            raise ValidationError(
                f'Invalid batch code format. Must be 4 digits (Mankiewicz) '
                f'or 9-10 digits (Akzo). Pattern: {BATCH_CODE_PATTERN}'
            )


class BatchListSchema(Schema):
    """List of batches response."""
    items = fields.List(fields.Nested(BatchSchema))
    total = fields.Integer()
