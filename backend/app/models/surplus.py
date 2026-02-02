"""Surplus model."""
from datetime import datetime, timezone

from ..extensions import db


class Surplus(db.Model):
    """Surplus inventory model.
    
    Tracks surplus quantity per location/article/batch.
    Check constraint: quantity_kg >= 0
    """
    
    __tablename__ = 'surplus'
    
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
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint(
            'location_id', 'article_id', 'batch_id',
            name='uq_surplus_location_article_batch'
        ),
        db.CheckConstraint('quantity_kg >= 0', name='ck_surplus_quantity_positive'),
    )
    
    # Relationships
    location = db.relationship('Location', back_populates='surplus_items')
    article = db.relationship('Article', back_populates='surplus_items')
    batch = db.relationship('Batch', back_populates='surplus_items')
    
    def __repr__(self):
        return f'<Surplus {self.quantity_kg}kg at {self.location_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'location_id': self.location_id,
            'article_id': self.article_id,
            'batch_id': self.batch_id,
            'quantity_kg': float(self.quantity_kg) if self.quantity_kg else 0,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
