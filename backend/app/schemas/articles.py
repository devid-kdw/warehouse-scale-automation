"""Article Marshmallow schemas."""
from marshmallow import Schema, fields, validate


class ArticleSchema(Schema):
    """Article response schema."""
    id = fields.Integer(dump_only=True)
    article_no = fields.String(required=True, metadata={'description': 'Unique article number'})
    description = fields.String(allow_none=True)
    article_group = fields.String(allow_none=True)
    # DEPRECATED: base_uom is dump-only for legacy compatibility
    base_uom = fields.String(dump_only=True, dump_default='kg')
    pack_size = fields.Float(allow_none=True)
    pack_uom = fields.String(allow_none=True)
    barcode = fields.String(allow_none=True)
    # Core v1.2 fields
    uom = fields.String(required=True, metadata={'description': 'Unit of measure: KG or L (required)'})
    manufacturer = fields.String(allow_none=True)
    manufacturer_art_number = fields.String(allow_none=True, metadata={'description': 'Vendor article number'})
    reorder_threshold = fields.Float(allow_none=True, metadata={'description': 'Low stock alarm threshold'})
    is_paint = fields.Boolean(dump_default=True)
    is_active = fields.Boolean(dump_default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True, allow_none=True)
    # Computed field for 2-month inactivity warning
    last_consumed_at = fields.DateTime(
        dump_only=True, 
        allow_none=True,
        metadata={'description': 'Last consumption date (STOCK_CONSUMED or SURPLUS_CONSUMED)'}
    )


class ArticleCreateSchema(Schema):
    """Schema for creating an article."""
    article_no = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={'description': 'Unique article number'}
    )
    description = fields.String(allow_none=True, validate=validate.Length(max=500))
    article_group = fields.String(allow_none=True, validate=validate.Length(max=100))
    # NOTE: base_uom removed from create - use 'uom' instead (base_uom is deprecated)
    pack_size = fields.Float(allow_none=True, validate=validate.Range(min=0))
    pack_uom = fields.String(allow_none=True, validate=validate.Length(max=20))
    barcode = fields.String(allow_none=True, validate=validate.Length(max=100))
    # Core v1.2 fields - UOM is REQUIRED (no default to catch errors)
    uom = fields.String(
        required=True,
        validate=validate.OneOf(['KG', 'L']),
        metadata={'description': 'Unit of measure: KG or L (required)'}
    )
    manufacturer = fields.String(allow_none=True, validate=validate.Length(max=200))
    manufacturer_art_number = fields.String(allow_none=True, validate=validate.Length(max=100))
    reorder_threshold = fields.Float(allow_none=True, validate=validate.Range(min=0))
    is_paint = fields.Boolean(load_default=True)
    is_active = fields.Boolean(load_default=True)


class ArticleListSchema(Schema):
    """List of articles response."""
    items = fields.List(fields.Nested(ArticleSchema))
    total = fields.Integer()

