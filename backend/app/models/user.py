"""User model."""
from datetime import datetime, timezone

from ..extensions import db


class User(db.Model):
    """User model for audit purposes.
    
    Roles: ADMIN, OPERATOR
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    role = db.Column(db.Text, nullable=False)  # ADMIN, OPERATOR
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    created_drafts = db.relationship(
        'WeighInDraft',
        back_populates='created_by_user',
        foreign_keys='WeighInDraft.created_by_user_id'
    )
    approval_actions = db.relationship(
        'ApprovalAction',
        back_populates='actor_user',
        foreign_keys='ApprovalAction.actor_user_id'
    )
    transactions = db.relationship(
        'Transaction',
        back_populates='user',
        foreign_keys='Transaction.user_id'
    )
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
