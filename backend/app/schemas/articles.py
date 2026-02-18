"""Article Marshmallow schemas."""
from marshmallow import Schema, fields, validate

from ..models.article import Article


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
    # Core fields
    uom = fields.String(required=True, metadata={'description': 'Unit of measure (open catalog)'})
    manufacturer = fields.String(allow_none=True)
    manufacturer_art_number = fields.String(allow_none=True, metadata={'description': 'Vendor article number'})
    reorder_threshold = fields.Float(allow_none=True, metadata={'description': 'Low stock alarm threshold'})
    is_paint = fields.Boolean(dump_default=True)
    # v3 fields
    density = fields.Float(dump_default=1.0, metadata={'description': 'Mass-Volume conversion (kg/L)'})
    has_batch = fields.Boolean(dump_default=True, metadata={'description': 'Canonical batch-tracking flag'})
    supplier_code = fields.String(allow_none=True, metadata={'description': 'SAP/ERP supplier code'})
    category = fields.String(allow_none=True, metadata={'description': 'Normalized category key'})
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
    # UOM — open catalog, no hard KG/L limit (v3)
    uom = fields.String(
        required=True,
        validate=validate.Length(min=1, max=20),
        metadata={'description': 'Unit of measure (open catalog, normalized to uppercase)'}
    )
    manufacturer = fields.String(allow_none=True, validate=validate.Length(max=200))
    manufacturer_art_number = fields.String(allow_none=True, validate=validate.Length(max=100))
    reorder_threshold = fields.Float(allow_none=True, validate=validate.Range(min=0))
    is_paint = fields.Boolean(load_default=True)
    # v3 fields
    density = fields.Float(load_default=1.0, validate=validate.Range(min=0.001))
    has_batch = fields.Boolean(
        load_default=None,
        metadata={'description': 'Batch-tracking flag. If not sent, derived from is_paint for backward compat.'}
    )
    supplier_code = fields.String(allow_none=True, validate=validate.Length(max=50))
    category = fields.String(
        allow_none=True,
        validate=validate.OneOf(Article.VALID_CATEGORIES + [None]),
        metadata={'description': 'Normalized category key from approved list'}
    )
    is_active = fields.Boolean(load_default=True)


class ArticleListSchema(Schema):
    """List of articles response."""
    items = fields.List(fields.Nested(ArticleSchema))
    total = fields.Integer()

class ArticleUpdateSchema(Schema):
    """Schema for updating descriptive article fields (Admin)."""
    description = fields.String(allow_none=True, validate=validate.Length(max=500))
    article_group = fields.String(allow_none=True, validate=validate.Length(max=100))
    uom = fields.String(validate=validate.Length(min=1, max=20))
    manufacturer = fields.String(allow_none=True, validate=validate.Length(max=200))
    manufacturer_art_number = fields.String(allow_none=True, validate=validate.Length(max=100))
    reorder_threshold = fields.Float(allow_none=True, validate=validate.Range(min=0))
    density = fields.Float(validate=validate.Range(min=0.001))
    has_batch = fields.Boolean()
    supplier_code = fields.String(allow_none=True, validate=validate.Length(max=50))
    category = fields.String(
        allow_none=True,
        validate=validate.OneOf(Article.VALID_CATEGORIES + [None])
    )
    is_active = fields.Boolean()
