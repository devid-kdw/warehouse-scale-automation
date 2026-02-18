"""Article Identifikator Marshmallow schemas."""
from marshmallow import Schema, fields, validate


class ArticleLookupQuerySchema(Schema):
    """Query parameters for article lookup."""
    query = fields.String(required=True, validate=validate.Length(min=1))


class MissingArticleReportCreateSchema(Schema):
    """Schema for submitting a missing article report."""
    raw_input = fields.String(required=True, validate=validate.Length(min=1, max=500))
    location_id = fields.Integer(load_default=13)


class MissingArticleReportSchema(Schema):
    """Response schema for missing article reports."""
    id = fields.Integer()
    reported_by_user_id = fields.Integer()
    location_id = fields.Integer()
    raw_input = fields.String()
    status = fields.String()
    resolved_article_id = fields.Integer(allow_none=True)
    admin_note = fields.String(allow_none=True)
    created_at = fields.DateTime()
    resolved_at = fields.DateTime(allow_none=True)


class AdminReportUpdateSchema(Schema):
    """Schema for admin to update a report."""
    status = fields.String(
        required=True,
        validate=validate.OneOf(['IN_REVIEW', 'RESOLVED', 'CLOSED', 'REJECTED'])
    )
    admin_note = fields.String(allow_none=True, validate=validate.Length(max=1000))
    resolved_article_id = fields.Integer(allow_none=True)
