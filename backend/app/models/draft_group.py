"""DraftGroup model."""
from datetime import datetime, timezone

from ..extensions import db


class DraftGroup(db.Model):
    """Header for a group of weigh-in drafts."""
    
    __tablename__ = 'draft_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=True)
    status = db.Column(db.Text, nullable=False, default='DRAFT')
    source = db.Column(db.Text, nullable=False, default='ui_operator')
    location_id = db.Column(
        db.Integer,
        db.ForeignKey('locations.id'),
        nullable=False
    )
    created_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Indexes
    __table_args__ = (
        db.Index('idx_draft_groups_status_created_at', 'status', 'created_at'),
        db.Index('idx_draft_groups_source_created_at', 'source', 'created_at'),
    )
    
    # Relationships
    location = db.relationship('Location', back_populates='draft_groups')
    created_by_user = db.relationship(
        'User',
        back_populates='created_draft_groups',
        foreign_keys=[created_by_user_id]
    )
    drafts = db.relationship(
        'WeighInDraft',
        back_populates='draft_group',
        cascade='all, delete-orphan'
    )
    
    # Valid status values
    STATUS_DRAFT = 'DRAFT'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    VALID_STATUSES = [STATUS_DRAFT, STATUS_APPROVED, STATUS_REJECTED]
    
    def __repr__(self):
        return f'<DraftGroup {self.id} ({self.status})>'
    
    @property
    def line_count(self):
        """Number of drafts in group."""
        return len(self.drafts)

    @property
    def total_quantity_kg(self):
        """Total quantity of all drafts in group."""
        return sum(float(d.quantity_kg) for d in self.drafts)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'source': self.source,
            'location_id': self.location_id,
            'created_by_user_id': self.created_by_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'line_count': len(self.drafts),
            'total_quantity_kg': self.total_quantity_kg
        }
