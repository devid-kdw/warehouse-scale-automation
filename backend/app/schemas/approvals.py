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
    consumed_surplus = fields.Float(allow_none=True)
    consumed_stock = fields.Float(allow_none=True)
    action = fields.Nested(ApprovalActionSchema)


class DailyApprovalSummarySchema(Schema):
    """Summary of pending drafts for a specific day."""
    date = fields.String(dump_only=True)
    location_id = fields.Integer(dump_only=True)
    total_lines = fields.Integer(dump_only=True)
    total_qty = fields.Float(dump_only=True)


class DailyApprovalDetailSchema(Schema):
    """Aggregated line in the daily queue."""
    article_id = fields.Integer(dump_only=True)
    article_no = fields.String(dump_only=True)
    article_name = fields.String(dump_only=True)
    batch_id = fields.Integer(dump_only=True)
    batch_code = fields.String(dump_only=True)
    location_id = fields.Integer(dump_only=True)
    total_qty = fields.Float(dump_only=True)
    uom = fields.String(dump_only=True)
    draft_ids = fields.List(fields.Integer(), dump_only=True)


class DailyAggregateEditSchema(Schema):
    """Request to edit aggregate quantity."""
    article_id = fields.Integer(required=True)
    batch_id = fields.Integer(required=True)
    new_total_qty = fields.Float(required=True, validate=validate.Range(min=0.01))


class DailyActionResponseSchema(Schema):
    """Generic response for daily mass actions."""
    status = fields.String(required=True)
    count = fields.Integer(required=True)
    date = fields.String(required=True)
    location_id = fields.Integer(required=True)
