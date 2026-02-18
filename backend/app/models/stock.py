"""Stock model."""
from datetime import datetime, timezone

from ..extensions import db


class Stock(db.Model):
    """Stock inventory model.
    
    Tracks current stock quantity per location/article/batch.
    Check constraint: quantity_kg >= 0
    """
    
    __tablename__ = 'stock'
    
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(
        db.Integer,
        db.ForeignKey('locations.id'),
        nullable=False
    )
    article_id = db.Column(
        db.Integer,
        db.ForeignKey('articles.id'),
        nullable=False
    )
    batch_id = db.Column(
        db.Integer,
        db.ForeignKey('batches.id'),
        nullable=False
    )
    # quantity_kg removed (v3 decommission)
    
    # v3 unit-aware columns
    quantity = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    uom = db.Column(db.String(20), nullable=False)
    
    last_updated = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint(
            'location_id', 'article_id', 'batch_id',
            name='uq_stock_location_article_batch'
        ),
        db.CheckConstraint('quantity >= 0', name='ck_stock_quantity_positive'),
    )
    
    # Relationships
    location = db.relationship('Location', back_populates='stock_items')
    article = db.relationship('Article', back_populates='stock_items')
    batch = db.relationship('Batch', back_populates='stock_items')
    
    def __repr__(self):
        return f'<Stock {self.quantity} {self.uom} at {self.location_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'location_id': self.location_id,
            'article_id': self.article_id,
            'batch_id': self.batch_id,
            'quantity': float(self.quantity) if self.quantity is not None else 0,
            'uom': self.uom,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
