"""MissingArticleReport model."""
from datetime import datetime, timezone
from sqlalchemy import Index, text
from ..extensions import db


class MissingArticleReport(db.Model):
    """Report for articles searched but not found in system.
    
    Used by OPERATOR to notify ADMIN of missing data.
    """
    
    __tablename__ = 'missing_article_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    reported_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    location_id = db.Column(
        db.Integer,
        db.ForeignKey('locations.id'),
        nullable=False
    )
    
    raw_input = db.Column(db.Text, nullable=False)
    normalized_input = db.Column(db.Text, nullable=False, index=True)
    
    status = db.Column(db.String(20), nullable=False, default='OPEN')
    
    resolved_article_id = db.Column(
        db.Integer,
        db.ForeignKey('articles.id'),
        nullable=True
    )
    
    admin_note = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True
    )
    resolved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    resolved_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True
    )

    # Status Constants
    STATUS_OPEN = 'OPEN'
    STATUS_IN_REVIEW = 'IN_REVIEW'
    STATUS_RESOLVED = 'RESOLVED'
    STATUS_CLOSED = 'CLOSED'
    STATUS_REJECTED = 'REJECTED'

    # Table arguments for Partial Unique Index (Postgres specific in production)
    __table_args__ = (
        Index(
            'ix_unq_active_missing_reports',
            'normalized_input', 'location_id',
            unique=True,
            postgresql_where=text("status = 'OPEN'")
        ),
    )

    # Relationships
    reporter = db.relationship('User', foreign_keys=[reported_by_user_id])
    resolver = db.relationship('User', foreign_keys=[resolved_by_user_id])
    article = db.relationship('Article')
    location = db.relationship('Location')

    def to_dict(self):
        return {
            'id': self.id,
            'reported_by_user_id': self.reported_by_user_id,
            'location_id': self.location_id,
            'raw_input': self.raw_input,
            'normalized_input': self.normalized_input,
            'status': self.status,
            'resolved_article_id': self.resolved_article_id,
            'admin_note': self.admin_note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by_user_id': self.resolved_by_user_id
        }
