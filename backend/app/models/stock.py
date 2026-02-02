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
    quantity_kg = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=0
    )
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
        db.CheckConstraint('quantity_kg >= 0', name='ck_stock_quantity_positive'),
    )
    
    # Relationships
    location = db.relationship('Location', back_populates='stock_items')
    article = db.relationship('Article', back_populates='stock_items')
    batch = db.relationship('Batch', back_populates='stock_items')
    
    def __repr__(self):
        return f'<Stock {self.quantity_kg}kg at {self.location_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'location_id': self.location_id,
            'article_id': self.article_id,
            'batch_id': self.batch_id,
            'quantity_kg': float(self.quantity_kg) if self.quantity_kg else 0,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
