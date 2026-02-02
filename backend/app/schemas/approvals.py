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
    created_at = fields.DateTime(dump_only=True)


class ApprovalRequestSchema(Schema):
    """Schema for approve/reject request."""
    actor_user_id = fields.Integer(
        required=True,
        metadata={'description': 'User ID performing the action'}
    )
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
    action = fields.Nested(ApprovalActionSchema)
