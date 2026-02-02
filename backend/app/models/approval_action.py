"""ApprovalAction model."""
from datetime import datetime, timezone

from ..extensions import db


class ApprovalAction(db.Model):
    """Approval action audit log.
    
    Records all approval/rejection/edit actions on drafts.
    """
    
    __tablename__ = 'approval_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    draft_id = db.Column(
        db.Integer,
        db.ForeignKey('weigh_in_drafts.id'),
        nullable=False
    )
    action = db.Column(db.Text, nullable=False)  # APPROVE, REJECT, EDIT
    actor_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    old_value = db.Column(db.JSON, nullable=True)
    new_value = db.Column(db.JSON, nullable=True)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    draft = db.relationship('WeighInDraft', back_populates='approval_actions')
    actor_user = db.relationship(
        'User',
        back_populates='approval_actions',
        foreign_keys=[actor_user_id]
    )
    
    # Valid action values
    ACTION_APPROVE = 'APPROVE'
    ACTION_REJECT = 'REJECT'
    ACTION_EDIT = 'EDIT'
    VALID_ACTIONS = [ACTION_APPROVE, ACTION_REJECT, ACTION_EDIT]
    
    def __repr__(self):
        return f'<ApprovalAction {self.action} on Draft {self.draft_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'draft_id': self.draft_id,
            'action': self.action,
            'actor_user_id': self.actor_user_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
