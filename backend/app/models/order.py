"""Order and OrderLine models for v3 orders domain."""
from datetime import datetime, timezone

from ..extensions import db


class Order(db.Model):
    """Purchase order header."""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    supplier_code = db.Column(db.String(50), nullable=True)
    supplier_name = db.Column(db.String(200), nullable=True)
    note = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='OPEN')  # OPEN | CLOSED
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False,
                           default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True,
                           onupdate=lambda: datetime.now(timezone.utc))

    lines = db.relationship('OrderLine', backref='order', lazy='dynamic',
                            cascade='all, delete-orphan')

    STATUS_OPEN = 'OPEN'
    STATUS_CLOSED = 'CLOSED'

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'supplier_code': self.supplier_code,
            'supplier_name': self.supplier_name,
            'note': self.note,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'lines': [l.to_dict() for l in self.lines],
        }


class OrderLine(db.Model):
    """Individual line item within an order."""
    __tablename__ = 'order_lines'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False, index=True)
    ordered_qty = db.Column(db.Numeric(14, 3), nullable=False)
    received_qty = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    uom = db.Column(db.String(20), nullable=False)
    delivery_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='OPEN')  # OPEN | CLOSED | REMOVED
    note = db.Column(db.Text, nullable=True)

    article = db.relationship('Article', lazy='joined')

    STATUS_OPEN = 'OPEN'
    STATUS_CLOSED = 'CLOSED'
    STATUS_REMOVED = 'REMOVED'

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'article_id': self.article_id,
            'article_no': self.article.article_no if self.article else None,
            'ordered_qty': str(self.ordered_qty),
            'received_qty': str(self.received_qty),
            'uom': self.uom,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'status': self.status,
            'note': self.note,
        }
