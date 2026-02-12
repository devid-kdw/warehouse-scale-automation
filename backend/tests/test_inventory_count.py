"""Test inventory count endpoint."""
import pytest
from flask_jwt_extended import create_access_token
from decimal import Decimal

from app.models import Stock, Surplus, Transaction, WeighInDraft


def get_headers(user_id):
    """Helper to get admin headers."""
    token = create_access_token(identity=str(user_id), additional_claims={'role': 'ADMIN'})
    return {'Authorization': f'Bearer {token}'}


def test_inventory_count_over(client, app, user, location, article, batch, stock, surplus):
    """Test Case A: Counted > Total (Over). Surplus should increase."""
    headers = get_headers(user)
    
    # Initial state: Stock=10, Surplus=5, Total=15
    # Counted = 17 (+2)
    payload = {
        'location_id': location,
        'article_id': article,
        'batch_id': batch,
        'counted_total_qty': 17.0,
        'note': 'Found extra'
    }
    
    response = client.post('/api/inventory/count', json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json
    
    assert data['result'] == 'over'
    assert data['delta'] == 2.0
    assert data['surplus_added'] == 2.0
    
    # Verify DB
    with app.app_context():
        new_surplus = Surplus.query.filter_by(batch_id=batch).first()
        assert new_surplus.quantity_kg == Decimal('7.00')  # 5 + 2
        
        # Verify transaction
        tx = Transaction.query.filter_by(batch_id=batch).order_by(Transaction.id.desc()).first()
        assert tx.tx_type == 'INVENTORY_ADJUSTMENT'
        assert tx.quantity_kg == Decimal('2.00')
        assert tx.meta['reason'] == 'inventory_count_over'


def test_inventory_count_under_creates_draft(client, app, user, location, article, batch, stock, surplus):
    """Test Case C: Counted < Total (Under). Surplus reset to 0, Shortage draft created."""
    headers = get_headers(user)
    
    # Initial state: Stock=10, Surplus=5, Total=15
    # Counted = 8 (Deficit = 7)
    # Logic:
    # 1. Reset Surplus (5 -> 0)
    # 2. Deficit 7 -> Created as Shortage Draft
    
    payload = {
        'location_id': location,
        'article_id': article,
        'batch_id': batch,
        'counted_total_qty': 8.0
    }
    
    response = client.post('/api/inventory/count', json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json
    
    assert data['result'] == 'under'
    assert data['surplus_reset'] == 5.0
    assert data['shortage_draft_id'] is not None
    
    # Verify DB
    with app.app_context():
        # Surplus should be 0
        new_surplus = Surplus.query.filter_by(batch_id=batch).first()
        assert new_surplus.quantity_kg == Decimal('0.00')
        
        # Stock should NOT change yet
        new_stock = Stock.query.filter_by(batch_id=batch).first()
        assert new_stock.quantity_kg == Decimal('10.00')
        
        # Draft created
        draft = WeighInDraft.query.get(data['shortage_draft_id'])
        assert draft.draft_type == 'INVENTORY_SHORTAGE'
        assert draft.quantity_kg == Decimal('7.00')  # Total 15 - Counted 8 = 7
        assert draft.status == 'DRAFT'


def test_inventory_count_no_change(client, app, user, location, article, batch, stock, surplus):
    """Test Case B: Counted == Total. No changes."""
    headers = get_headers(user)
    
    # Total = 15
    payload = {
        'location_id': location,
        'article_id': article,
        'batch_id': batch,
        'counted_total_qty': 15.0
    }
    
    response = client.post('/api/inventory/count', json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json['result'] == 'no_change'
