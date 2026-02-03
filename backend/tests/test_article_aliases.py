"""Test article aliases."""
import pytest
from flask_jwt_extended import create_access_token

from app.models import ArticleAlias


def get_headers(user_id):
    token = create_access_token(identity=user_id, additional_claims={'role': 'ADMIN'})
    return {'Authorization': f'Bearer {token}'}


def test_create_alias_success(client, app, user, article):
    """Test creating an alias."""
    headers = get_headers(user)
    payload = {'alias': 'BLUE-FAIL'}
    
    response = client.post(f'/api/articles/{article}/aliases', json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json['alias'] == 'BLUE-FAIL'
    assert response.json['article_id'] == article


def test_create_alias_duplicate(client, app, user, article):
    """Test duplicate alias rejected (Global Uniqueness)."""
    headers = get_headers(user)
    payload = {'alias': 'UNIQUE-CODE'}
    
    # Create first
    client.post(f'/api/articles/{article}/aliases', json=payload, headers=headers)
    
    # Create second (same code, same article)
    response = client.post(f'/api/articles/{article}/aliases', json=payload, headers=headers)
    assert response.status_code == 409
    assert 'DUPLICATE_ALIAS' in response.json['error']['code']


def test_create_alias_limit(client, app, user, article):
    """Test max 5 aliases limit."""
    headers = get_headers(user)
    
    # Create 5 aliases
    for i in range(5):
        payload = {'alias': f'ALIAS-{i}'}
        res = client.post(f'/api/articles/{article}/aliases', json=payload, headers=headers)
        assert res.status_code == 201
        
    # Create 6th
    payload = {'alias': 'ALIAS-6'}
    response = client.post(f'/api/articles/{article}/aliases', json=payload, headers=headers)
    assert response.status_code == 409
    assert 'ALIAS_LIMIT_REACHED' in response.json['error']['code']


def test_resolve_article(client, app, user, article):
    """Test resolving article by alias."""
    headers = get_headers(user)
    
    # Create alias
    client.post(f'/api/articles/{article}/aliases', json={'alias': 'QUICK-REF'}, headers=headers)
    
    # Resolve by Alias
    response = client.get('/api/articles/resolve?query=QUICK-REF', headers=headers)
    assert response.status_code == 200
    assert response.json['id'] == article
    
    # Resolve by Article No
    response = client.get('/api/articles/resolve?query=TEST-001', headers=headers) # TEST-001 from fixture
    assert response.status_code == 200
    assert response.json['id'] == article


def test_resolve_not_found(client, user):
    headers = get_headers(user)
    response = client.get('/api/articles/resolve?query=NONEXISTENT', headers=headers)
    assert response.status_code == 404
