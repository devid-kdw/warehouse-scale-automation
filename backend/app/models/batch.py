"""Batch model."""
from datetime import datetime, timezone

from ..extensions import db


class Batch(db.Model):
    """Batch model - unique per article.
    
    Batch code validation: 4 digits (Mankiewicz) or 9-10 digits (Akzo)
    Regex: ^\d{4}$|^\d{9,10}$
    """
    
    __tablename__ = 'batches'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(
        db.Integer,
        db.ForeignKey('articles.id'),
        nullable=False
    )
    batch_code = db.Column(db.Text, nullable=False)
    received_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    note = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Unique constraint: one batch_code per article
    __table_args__ = (
        db.UniqueConstraint('article_id', 'batch_code', name='uq_batch_article_code'),
    )
    
    # Relationships
    article = db.relationship('Article', back_populates='batches')
    stock_items = db.relationship('Stock', back_populates='batch')
    surplus_items = db.relationship('Surplus', back_populates='batch')
    drafts = db.relationship('WeighInDraft', back_populates='batch')
    transactions = db.relationship('Transaction', back_populates='batch')
    
    def __repr__(self):
        return f'<Batch {self.batch_code} for Article {self.article_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'article_id': self.article_id,
            'batch_code': self.batch_code,
            'received_date': self.received_date.isoformat() if self.received_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'note': self.note,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
