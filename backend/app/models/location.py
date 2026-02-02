"""Location model."""
from datetime import datetime, timezone

from ..extensions import db


class Location(db.Model):
    """Warehouse location model.
    
    Seed data: code "13"
    """
    
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    stock_items = db.relationship('Stock', back_populates='location')
    surplus_items = db.relationship('Surplus', back_populates='location')
    drafts = db.relationship('WeighInDraft', back_populates='location')
    transactions = db.relationship('Transaction', back_populates='location')
    
    def __repr__(self):
        return f'<Location {self.code}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
