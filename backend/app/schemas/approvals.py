"""Approval Marshmallow schemas."""
from marshmallow import Schema, fields, validate


class ApprovalActionSchema(Schema):
    """ApprovalAction response schema."""
    id = fields.Integer(dump_only=True)
    draft_id = fields.Integer(required=True)
    action = fields.String(required=True)
    actor_user_id = fields.Integer(required=True)
    old_value = fields.Dict(allow_none=True)
    new_value = fields.Dict(allow_none=True)
    note = fields.String(allow_none=True)
    created_at = fields.String(dump_only=True)  # Already serialized as ISO string from to_dict()


class ApprovalRequestSchema(Schema):
    """Schema for approve/reject request.
    
    Note: actor_user_id is no longer required - it's taken from JWT token.
    """
    note = fields.String(
        allow_none=True,
        validate=validate.Length(max=500),
        metadata={'description': 'Optional note for the action'}
    )


class ApprovalResponseSchema(Schema):
    """Response after approval/rejection."""
    message = fields.String(required=True)
    draft_id = fields.Integer(required=True)
    new_status = fields.String(required=True)
    consumed_surplus_kg = fields.Float(allow_none=True)
    consumed_stock_kg = fields.Float(allow_none=True)
    action = fields.Nested(ApprovalActionSchema)
