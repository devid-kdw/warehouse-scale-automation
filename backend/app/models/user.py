"""User model with password authentication."""
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db


class User(db.Model):
    """User model with authentication.
    
    Roles: ADMIN, OPERATOR
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=True)  # Nullable for migration
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
    
    def set_password(self, password: str):
        """Hash and set password."""
        # Use pbkdf2:sha256 for compatibility (scrypt not available on all systems)
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
    
    def to_dict(self, include_sensitive: bool = False):
        """Convert to dictionary.
        
        Args:
            include_sensitive: If False, excludes password_hash
        """
        data = {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        return data
