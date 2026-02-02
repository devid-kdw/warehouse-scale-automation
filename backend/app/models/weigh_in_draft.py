"""WeighInDraft model."""
from datetime import datetime, timezone

from ..extensions import db


class WeighInDraft(db.Model):
    """Weigh-in draft model - staging for approval.
    
    Status: DRAFT -> APPROVED or REJECTED
    Check constraint: 0 < quantity_kg <= 9999.99
    """
    
    __tablename__ = 'weigh_in_drafts'
    
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
    quantity_kg = db.Column(db.Numeric(14, 2), nullable=False)
    status = db.Column(db.Text, nullable=False, default='DRAFT')
    created_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True
    )
    source = db.Column(db.Text, nullable=False, default='manual')
    client_event_id = db.Column(db.Text, nullable=False, unique=True)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint(
            'quantity_kg > 0 AND quantity_kg <= 9999.99',
            name='ck_draft_quantity_range'
        ),
    )
    
    # Relationships
    location = db.relationship('Location', back_populates='drafts')
    article = db.relationship('Article', back_populates='drafts')
    batch = db.relationship('Batch', back_populates='drafts')
    created_by_user = db.relationship(
        'User',
        back_populates='created_drafts',
        foreign_keys=[created_by_user_id]
    )
    approval_actions = db.relationship(
        'ApprovalAction',
        back_populates='draft',
        cascade='all, delete-orphan'
    )
    
    # Valid status values
    STATUS_DRAFT = 'DRAFT'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    VALID_STATUSES = [STATUS_DRAFT, STATUS_APPROVED, STATUS_REJECTED]
    
    def __repr__(self):
        return f'<WeighInDraft {self.id} ({self.status})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'location_id': self.location_id,
            'article_id': self.article_id,
            'batch_id': self.batch_id,
            'quantity_kg': float(self.quantity_kg) if self.quantity_kg else None,
            'status': self.status,
            'created_by_user_id': self.created_by_user_id,
            'source': self.source,
            'client_event_id': self.client_event_id,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
