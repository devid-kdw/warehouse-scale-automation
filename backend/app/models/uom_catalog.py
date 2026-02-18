"""UOM Catalog model — open-entry unit-of-measure persistence."""
from datetime import datetime, timezone

from ..extensions import db


class UomCatalog(db.Model):
    """Unit of Measure catalog.

    Open-entry model: any new UOM string persisted on first use and reusable
    afterward.  Code is stored as uppercase, globally unique.
    """

    __tablename__ = 'uom_catalog'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self):
        return f'<UomCatalog {self.code}>'

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
