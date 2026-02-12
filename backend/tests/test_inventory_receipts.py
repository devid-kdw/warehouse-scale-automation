"""Tests for inventory receipts endpoint."""
from datetime import date, timedelta
from decimal import Decimal
import pytest

from app.extensions import db
from app.models import Transaction, User, Article, Batch
from app.services.receiving_service import receive_stock

@pytest.fixture
def user_token(app, user):
    from flask_jwt_extended import create_access_token
    with app.app_context():
        u = db.session.get(User, user)
        # Ensure user is ADMIN for these tests
        u.role = 'ADMIN' 
        db.session.commit()
        return create_access_token(identity=str(user), additional_claims={'role': 'ADMIN'})


class TestReceiptHistory:
    """Test GET /api/inventory/receipts."""
    
    def test_get_receipts_empty(self, app, client, user, user_token):
        """Empty history returns empty list."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()

        headers = {'Authorization': f'Bearer {user_token}'}
        res = client.get('/api/inventory/receipts', headers=headers)
        assert res.status_code == 200
        assert res.json['total'] == 0
        assert res.json['history'] == []

    def test_get_receipts_grouped(self, app, client, user, user_token, article, location):
        """Receipts are grouped by client_event_id."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            # Create another article
            article2 = Article(
                article_no='ART-2',
                uom='KG',
                is_paint=True,
                is_active=True
            )
            db.session.add(article2)
            db.session.commit()
            
            # Receipt 1: Single item
            receive_stock(
                article_id=article,
                batch_code='1111',
                quantity_kg=Decimal('10.00'),
                expiry_date=date.today(),
                actor_user_id=user,
                order_number='PO-1',
                client_event_id='evt-1'
            )
            
            # Receipt 2: Two items (same client_event_id)
            receive_stock(
                article_id=article,
                batch_code='2222',
                quantity_kg=Decimal('20.00'),
                expiry_date=date.today(),
                actor_user_id=user,
                order_number='PO-2',
                client_event_id='evt-2'
            )
            receive_stock(
                article_id=article2.id,
                batch_code='3333',
                quantity_kg=Decimal('30.00'),
                expiry_date=date.today(),
                actor_user_id=user,
                order_number='PO-2',
                client_event_id='evt-2'  # Same event ID
            )
            db.session.commit()
            
        headers = {'Authorization': f'Bearer {user_token}'}
        res = client.get('/api/inventory/receipts', headers=headers)
        
        assert res.status_code == 200
        history = res.json['history']
        assert len(history) == 2
        
        # Verify Group 2 (Latest, because sort desc)
        group2 = next(i for i in history if i['receipt_key'] == 'evt-2')
        assert group2['line_count'] == 2
        assert group2['total_quantity'] == 50.0  # 20 + 30
        assert group2['order_number'] == 'PO-2'
        
        # Verify Group 1
        group1 = next(i for i in history if i['receipt_key'] == 'evt-1')
        assert group1['line_count'] == 1
        assert group1['total_quantity'] == 10.0
        assert group1['order_number'] == 'PO-1'

    def test_get_receipts_legacy_fallback(self, app, client, user, user_token, article, location):
        """Legacy transactions (no client_event_id) are treated as individual receipts."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            # Manually create legacy transaction
            b = Batch(article_id=article, batch_code='OLD', expiry_date=date.today())
            db.session.add(b)
            db.session.flush()
            
            tx = Transaction(
                tx_type='STOCK_RECEIPT',
                location_id=location,
                article_id=article,
                batch_id=b.id,
                quantity_kg=Decimal('5.00'),
                user_id=user,
                source='legacy',
                client_event_id=None # Legacy
            )
            db.session.add(tx)
            db.session.commit()
            tx_id = tx.id
            
        headers = {'Authorization': f'Bearer {user_token}'}
        res = client.get('/api/inventory/receipts', headers=headers)
        
        assert res.status_code == 200
        history = res.json['history']
        assert len(history) == 1
        assert history[0]['receipt_key'] == f"tx-{tx_id}"
        assert history[0]['line_count'] == 1
