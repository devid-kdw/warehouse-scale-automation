"""Test inventory summary endpoint."""
import pytest
from flask_jwt_extended import create_access_token

from app.models import Article, Batch, Stock, Surplus
from app.extensions import db


def test_inventory_summary_empty(client, user):
    """Test inventory summary returns empty list when no inventory."""
    token = create_access_token(identity=str(user), additional_claims={'role': 'ADMIN'})
    headers = {'Authorization': f'Bearer {token}'}
    
    response = client.get('/api/inventory/summary', headers=headers)
    assert response.status_code == 200
    assert response.json['items'] == []
    assert response.json['total'] == 0


def test_inventory_summary_with_data(client, user, location, article, batch, stock, surplus):
    """Test inventory summary returns correct data."""
    token = create_access_token(identity=str(user), additional_claims={'role': 'ADMIN'})
    headers = {'Authorization': f'Bearer {token}'}
    
    response = client.get('/api/inventory/summary', headers=headers)
    assert response.status_code == 200
    assert len(response.json['items']) == 1
    item = response.json['items'][0]
    
    assert item['article_no'] == 'TEST-001'
    assert item['batch_code'] == '1234'
    assert item['stock_qty'] == 10.0
    assert item['surplus_qty'] == 5.0
    assert item['total_qty'] == 15.0


def test_inventory_summary_filters(client, app, user, location, article):
    """Test inventory summary filters."""
    token = create_access_token(identity=str(user), additional_claims={'role': 'ADMIN'})
    headers = {'Authorization': f'Bearer {token}'}
    
    # Create another article and batch
    with app.app_context():
        art2 = Article(article_no='TEST-002', description='Test Article 2', uom='KG')
        db.session.add(art2)
        db.session.commit()
        
        batch2 = Batch(article_id=art2.id, batch_code='5678')
        db.session.add(batch2)
        db.session.commit()
    
    # Filter by article_id (should return nothing if no inventory? 
    # Logic in endpoint returns based on Batch queries, so it should return batches even if 0 stock
    # unless we filtered it out. In my implementation I joined Stock/Surplus but didn't filter out 0s)
    
    response = client.get(f'/api/inventory/summary?article_id={article}', headers=headers)
    assert response.status_code == 200
    # Should see batches for article 1
    for item in response.json['items']:
        assert item['article_id'] == article
