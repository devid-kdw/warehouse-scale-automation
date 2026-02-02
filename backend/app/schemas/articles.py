"""Article Marshmallow schemas."""
from marshmallow import Schema, fields, validate


class ArticleSchema(Schema):
    """Article response schema."""
    id = fields.Integer(dump_only=True)
    article_no = fields.String(required=True, metadata={'description': 'Unique article number'})
    description = fields.String(allow_none=True)
    article_group = fields.String(allow_none=True)
    base_uom = fields.String(dump_default='kg')
    pack_size = fields.Float(allow_none=True)
    pack_uom = fields.String(allow_none=True)
    barcode = fields.String(allow_none=True)
    is_paint = fields.Boolean(dump_default=True)
    is_active = fields.Boolean(dump_default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True, allow_none=True)


class ArticleCreateSchema(Schema):
    """Schema for creating an article."""
    article_no = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={'description': 'Unique article number'}
    )
    description = fields.String(allow_none=True, validate=validate.Length(max=500))
    article_group = fields.String(allow_none=True, validate=validate.Length(max=100))
    base_uom = fields.String(load_default='kg', validate=validate.Length(max=20))
    pack_size = fields.Float(allow_none=True, validate=validate.Range(min=0))
    pack_uom = fields.String(allow_none=True, validate=validate.Length(max=20))
    barcode = fields.String(allow_none=True, validate=validate.Length(max=100))
    is_paint = fields.Boolean(load_default=True)
    is_active = fields.Boolean(load_default=True)


class ArticleListSchema(Schema):
    """List of articles response."""
    items = fields.List(fields.Nested(ArticleSchema))
    total = fields.Integer()
