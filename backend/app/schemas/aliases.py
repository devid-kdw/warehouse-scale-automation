"""Article alias Marshmallow schemas."""
from marshmallow import Schema, fields, validate


class ArticleAliasSchema(Schema):
    """Article alias response schema."""
    id = fields.Integer(dump_only=True)
    article_id = fields.Integer()
    alias = fields.String()
    created_at = fields.DateTime(dump_only=True)


class AliasCreateSchema(Schema):
    """Schema for creating an article alias."""
    alias = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={'description': 'Alias name (must be globally unique)'}
    )


class AliasListSchema(Schema):
    """List of aliases response."""
    items = fields.List(fields.Nested(ArticleAliasSchema))
    total = fields.Integer()
