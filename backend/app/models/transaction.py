"""Transaction model."""
from datetime import datetime, timezone

from ..extensions import db


class Transaction(db.Model):
    """Transaction audit log.
    
    Records all inventory changes for audit trail.
    tx_type: WEIGH_IN, SURPLUS_CONSUMED, STOCK_CONSUMED, INVENTORY_ADJUSTMENT, STOCK_RECEIPT
    """
    
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    tx_type = db.Column(db.Text, nullable=False)
    occurred_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
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
    quantity_kg = db.Column(db.Numeric(14, 2), nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True
    )
    source = db.Column(db.Text, nullable=False, default='ui')
    client_event_id = db.Column(db.Text, nullable=True, index=True)
    meta = db.Column(db.JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        db.Index('ix_transactions_occurred_at', 'occurred_at'),
        db.Index('ix_transactions_article_occurred', 'article_id', 'occurred_at'),
        db.Index('ix_transactions_batch_occurred', 'batch_id', 'occurred_at'),
    )
    
    # Relationships
    location = db.relationship('Location', back_populates='transactions')
    article = db.relationship('Article', back_populates='transactions')
    batch = db.relationship('Batch', back_populates='transactions')
    user = db.relationship(
        'User',
        back_populates='transactions',
        foreign_keys=[user_id]
    )
    
    # Valid tx_type values
    TX_WEIGH_IN = 'WEIGH_IN'
    TX_SURPLUS_CONSUMED = 'SURPLUS_CONSUMED'
    TX_STOCK_CONSUMED = 'STOCK_CONSUMED'
    TX_INVENTORY_ADJUSTMENT = 'INVENTORY_ADJUSTMENT'
    TX_STOCK_RECEIPT = 'STOCK_RECEIPT'
    VALID_TX_TYPES = [TX_WEIGH_IN, TX_SURPLUS_CONSUMED, TX_STOCK_CONSUMED, TX_INVENTORY_ADJUSTMENT, TX_STOCK_RECEIPT]
    
    def __repr__(self):
        return f'<Transaction {self.tx_type} {self.quantity_kg}kg>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tx_type': self.tx_type,
            'occurred_at': self.occurred_at.isoformat() if self.occurred_at else None,
            'location_id': self.location_id,
            'article_id': self.article_id,
            'batch_id': self.batch_id,
            'quantity_kg': float(self.quantity_kg) if self.quantity_kg else None,
            'user_id': self.user_id,
            'source': self.source,
            'client_event_id': self.client_event_id,
            'meta': self.meta
        }
