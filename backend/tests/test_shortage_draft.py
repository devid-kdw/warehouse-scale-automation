"""Test shortage draft approval workflow."""
import pytest
from flask_jwt_extended import create_access_token
from decimal import Decimal

from app.extensions import db
from app.models import Stock, Surplus, Transaction, WeighInDraft


def get_headers(user_id):
    token = create_access_token(identity=str(user_id), additional_claims={'role': 'ADMIN'})
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def shortage_draft(app, location, article, batch, user):
    """Create a shortage draft."""
    with app.app_context():
        d = WeighInDraft(
            location_id=location,
            article_id=article,
            batch_id=batch,
            quantity_kg=Decimal('5.00'),
            client_event_id='shortage-test-event',
            created_by_user_id=user,
            source='inventory_count',
            draft_type='INVENTORY_SHORTAGE',
            status='DRAFT'
        )
        db.session.add(d)
        db.session.commit()
        draft_id = d.id
    return draft_id


def test_approve_shortage_draft_success(client, app, user, shortage_draft, stock):
    """Test approving shortage draft consumes STOCK ONLY."""
    headers = get_headers(user)
    
    # Stock is 10 (from fixture). Draft is 5.
    response = client.post(f'/api/drafts/{shortage_draft}/approve', headers=headers)
    assert response.status_code == 200
    
    with app.app_context():
        # Check stock reduced
        s = Stock.query.first() # only one stock
        assert s.quantity_kg == Decimal('5.00') # 10 - 5
        
        # Check Transaction
        tx = Transaction.query.filter_by(source='shortage_approval').first()
        assert tx is not None
        assert tx.tx_type == 'INVENTORY_ADJUSTMENT'
        assert tx.quantity_kg == Decimal('-5.00')


def test_approve_shortage_draft_insufficient_stock(client, app, user, shortage_draft, stock):
    """Test approval fails if stock insufficient."""
    headers = get_headers(user)
    
    # Stock is 10. Increase draft to 15.
    with app.app_context():
        d = WeighInDraft.query.get(shortage_draft)
        d.quantity_kg = Decimal('15.00')
        db.session.commit()
        
    response = client.post(f'/api/drafts/{shortage_draft}/approve', headers=headers)
    # Expect 409 or similar (Insufficient Stock)
    # The exact status code depends on exception handler config
    # Assuming 409 INSUFFICIENT_STOCK
    assert response.status_code == 409
    assert 'INSUFFICIENT_STOCK' in response.json['error']['code']
