"""Draft (WeighInDraft) Marshmallow schemas."""
from marshmallow import Schema, fields, validate, validates, ValidationError


# Quantity constraints
QUANTITY_MIN = 0.01
QUANTITY_MAX = 9999.99


class DraftSchema(Schema):
    """WeighInDraft response schema."""
    id = fields.Integer(dump_only=True)
    location_id = fields.Integer(required=True)
    article_id = fields.Integer(required=True)
    batch_id = fields.Integer(required=True)
    quantity_kg = fields.Float(required=True)
    status = fields.String(dump_only=True)
    created_by_user_id = fields.Integer(allow_none=True)
    source = fields.String(dump_default='manual')
    client_event_id = fields.String(required=True)
    note = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class DraftCreateSchema(Schema):
    """Schema for creating a draft."""
    location_id = fields.Integer(
        required=True,
        metadata={'description': 'Location ID'}
    )
    article_id = fields.Integer(
        required=True,
        metadata={'description': 'Article ID'}
    )
    batch_id = fields.Integer(
        required=True,
        metadata={'description': 'Batch ID'}
    )
    quantity_kg = fields.Float(
        required=True,
        validate=validate.Range(min=QUANTITY_MIN, max=QUANTITY_MAX),
        metadata={'description': f'Quantity in kg ({QUANTITY_MIN}-{QUANTITY_MAX})'}
    )
    client_event_id = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={'description': 'Unique client-generated event ID (UUID recommended)'}
    )
    created_by_user_id = fields.Integer(
        allow_none=True,
        metadata={'description': 'User ID who created the draft'}
    )
    source = fields.String(
        load_default='manual',
        validate=validate.OneOf(['manual', 'scale', 'import']),
        metadata={'description': 'Source of the draft'}
    )
    note = fields.String(allow_none=True, validate=validate.Length(max=500))
    
    @validates('quantity_kg')
    def validate_quantity_precision(self, value, **kwargs):
        """Validate quantity has max 2 decimal places."""
        rounded = round(value, 2)
        if abs(value - rounded) > 0.001:
            raise ValidationError('quantity_kg must have at most 2 decimal places')


class DraftUpdateSchema(Schema):
    """Schema for updating a draft (PATCH)."""
    quantity_kg = fields.Float(
        validate=validate.Range(min=QUANTITY_MIN, max=QUANTITY_MAX),
        metadata={'description': f'Quantity in kg ({QUANTITY_MIN}-{QUANTITY_MAX})'}
    )
    note = fields.String(allow_none=True, validate=validate.Length(max=500))
    
    @validates('quantity_kg')
    def validate_quantity_precision(self, value, **kwargs):
        """Validate quantity has max 2 decimal places."""
        if value is not None:
            rounded = round(value, 2)
            if abs(value - rounded) > 0.001:
                raise ValidationError('quantity_kg must have at most 2 decimal places')


class DraftQuerySchema(Schema):
    """Query parameters for listing drafts."""
    status = fields.String(
        validate=validate.OneOf(['DRAFT', 'APPROVED', 'REJECTED']),
        metadata={'description': 'Filter by status'}
    )
    location_id = fields.Integer(metadata={'description': 'Filter by location'})
    article_id = fields.Integer(metadata={'description': 'Filter by article'})


class DraftListSchema(Schema):
    """List of drafts response."""
    items = fields.List(fields.Nested(DraftSchema))
    total = fields.Integer()
