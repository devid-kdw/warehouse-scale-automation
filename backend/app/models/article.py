"""Article model."""
from datetime import datetime, timezone

from ..extensions import db


class Article(db.Model):
    """Article (product) model."""

    # Approved category keys (EN) — see TASK-0020 S-005
    VALID_CATEGORIES = [
        'equipment_installations',
        'safety_equipment',
        'operational_supplies',
        'spare_parts_small_parts',
        'auxiliary_operating_materials',
        'assembly_material',
        'raw_material',
        'packaging_material',
        'goods_merchandise',
        'maintenance_material',
        'tools_small_equipment',
        'accessories_small_machines',
    ]
    
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    article_no = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    article_group = db.Column(db.Text, nullable=True)
    base_uom = db.Column(db.Text, nullable=False, default='kg')
    pack_size = db.Column(db.Numeric(12, 3), nullable=True)
    pack_uom = db.Column(db.Text, nullable=True)
    barcode = db.Column(db.Text, nullable=True)
    # New columns for v1.2
    uom = db.Column(db.String(10), nullable=False)  # KG or L - REQUIRED, no default
    manufacturer = db.Column(db.Text, nullable=True)
    manufacturer_art_number = db.Column(db.Text, nullable=True)  # Vendor code e.g., 34665.91B6.7.171
    reorder_threshold = db.Column(db.Numeric(14, 2), nullable=True)  # Future low stock alarm
    is_paint = db.Column(db.Boolean, default=True, nullable=False)
    # v3 columns
    has_batch = db.Column(db.Boolean, default=True, nullable=False)  # canonical batch-tracking flag
    supplier_code = db.Column(db.String(50), nullable=True)  # SAP/ERP supplier code
    category = db.Column(db.String(50), nullable=True)  # normalized category key
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    # v3 remediation
    density = db.Column(db.Numeric(10, 4), nullable=False, default=1.0)
    
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    # Relationships
    batches = db.relationship('Batch', back_populates='article')
    stock_items = db.relationship('Stock', back_populates='article')
    surplus_items = db.relationship('Surplus', back_populates='article')
    drafts = db.relationship('WeighInDraft', back_populates='article')
    transactions = db.relationship('Transaction', back_populates='article')
    aliases = db.relationship('ArticleAlias', back_populates='article', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Article {self.article_no}>'
    def to_dict(self):
        return {
            'id': self.id,
            'article_no': self.article_no,
            'description': self.description,
            'article_group': self.article_group,
            'base_uom': self.base_uom,
            'pack_size': float(self.pack_size) if self.pack_size else None,
            'pack_uom': self.pack_uom,
            'barcode': self.barcode,
            'uom': self.uom,
            'manufacturer': self.manufacturer,
            'manufacturer_art_number': self.manufacturer_art_number,
            'reorder_threshold': float(self.reorder_threshold) if self.reorder_threshold else None,
            'is_paint': self.is_paint,
            'has_batch': self.has_batch,
            'density': float(self.density),
            'supplier_code': self.supplier_code,
            'category': self.category,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
