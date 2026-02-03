"""ArticleAlias model."""
from datetime import datetime, timezone

from ..extensions import db


class ArticleAlias(db.Model):
    """Article alias model - alternative names for articles.
    
    Constraints:
    - alias is globally unique (cannot repeat across any articles)
    - max 5 aliases per article (enforced in service layer)
    """
    
    __tablename__ = 'article_aliases'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(
        db.Integer,
        db.ForeignKey('articles.id', ondelete='CASCADE'),
        nullable=False
    )
    alias = db.Column(db.Text, nullable=False, unique=True)  # Global uniqueness
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationship
    article = db.relationship('Article', back_populates='aliases')
    
    def __repr__(self):
        return f'<ArticleAlias {self.alias} for Article {self.article_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'article_id': self.article_id,
            'alias': self.alias,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
