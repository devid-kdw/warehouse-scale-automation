from marshmallow import Schema, fields, validate
from .drafts import DraftSchema


class DraftGroupLineSchema(Schema):
    """Schema for a line within a draft group (nested)."""
    id = fields.Integer(dump_only=True)
    location_id = fields.Integer(required=False) # Can be inherited from group
    article_id = fields.Integer(required=True)
    batch_id = fields.Integer(allow_none=True, load_default=None)
    quantity_kg = fields.Float(required=True, validate=validate.Range(min=0.01, max=9999.99))
    draft_type = fields.String(dump_default='WEIGH_IN', validate=validate.OneOf(['WEIGH_IN', 'INVENTORY_SHORTAGE']))
    note = fields.String(allow_none=True)
    client_event_id = fields.String(required=True)


class DraftGroupSchema(Schema):
    """Detailed draft group response schema."""
    id = fields.Integer(dump_only=True)
    name = fields.String(allow_none=True)
    status = fields.String(dump_only=True)
    source = fields.String(dump_only=True)
    location_id = fields.Integer(dump_only=True)
    created_by_user_id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    line_count = fields.Integer(dump_only=True)
    total_quantity_kg = fields.Float(dump_only=True)
    
    # Nested drafts (lines)
    drafts = fields.List(fields.Nested(DraftSchema), dump_only=True)


class DraftGroupSummarySchema(Schema):
    """Summary draft group response schema for lists."""
    id = fields.Integer(dump_only=True)
    name = fields.String(allow_none=True)
    status = fields.String(dump_only=True)
    source = fields.String(dump_only=True)
    location_id = fields.Integer(dump_only=True)
    created_by_user_id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    line_count = fields.Integer(dump_only=True)
    total_quantity_kg = fields.Float(dump_only=True)


class DraftGroupCreateSchema(Schema):
    """Schema for creating a draft group with multiple lines."""
    name = fields.String(allow_none=True, validate=validate.Length(max=200))
    location_id = fields.Integer(required=True)
    lines = fields.List(fields.Nested(DraftGroupLineSchema), required=True, validate=validate.Length(min=1))


class DraftGroupListSchema(Schema):
    """Schema for listing draft groups."""
    items = fields.List(fields.Nested(DraftGroupSummarySchema))
    total = fields.Integer()


class DraftGroupUpdateSchema(Schema):
    """Schema for updating draft group (e.g. name only)."""
    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
