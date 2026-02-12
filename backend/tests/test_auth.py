"""Tests for JWT authentication."""
import pytest
from flask_jwt_extended import create_access_token

from app.models import User
from app.extensions import db
from app.auth import authenticate_user, create_tokens, AuthError


class TestLogin:
    """Test login endpoint."""
    
    def test_login_success(self, client, user):
        """Valid credentials return tokens."""
        # First set password on the user
        with client.application.app_context():
            u = db.session.get(User, user)
            u.set_password('TestPassword123!')
            db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'TestPassword123!'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
    
    def test_login_invalid_password(self, client, user):
        """Invalid password returns 401."""
        with client.application.app_context():
            u = db.session.get(User, user)
            u.set_password('CorrectPassword!')
            db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'WrongPassword!'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['error']['code'] == 'INVALID_TOKEN'
    
    def test_login_nonexistent_user(self, client):
        """Non-existent user returns 401."""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'SomePassword!'
        })
        
        assert response.status_code == 401


class TestRBAC:
    """Test role-based access control."""
    
    def test_operator_cannot_approve(self, client, app, user, pending_draft):
        """OPERATOR role cannot access approve endpoint."""
        with app.app_context():
            # Make user an OPERATOR
            u = db.session.get(User, user)
            u.role = 'OPERATOR'
            db.session.commit()
            
            # Create token for operator
            token = create_access_token(
                identity=str(user),
                additional_claims={'role': 'OPERATOR', 'username': 'testuser'}
            )
        
        response = client.post(
            f'/api/drafts/{pending_draft}/approve',
            headers={'Authorization': f'Bearer {token}'},
            json={}
        )
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['error']['code'] == 'FORBIDDEN'
    
    def test_admin_can_approve(self, client, app, user, pending_draft, stock):
        """ADMIN role can access approve endpoint."""
        with app.app_context():
            # Ensure user is ADMIN
            u = db.session.get(User, user)
            u.role = 'ADMIN'
            db.session.commit()
            
            # Create token for admin
            token = create_access_token(
                identity=str(user),
                additional_claims={'role': 'ADMIN', 'username': 'testuser'}
            )
        
        response = client.post(
            f'/api/drafts/{pending_draft}/approve',
            headers={'Authorization': f'Bearer {token}'},
            json={}
        )
        
        # Should be 200 (success) or 409 (insufficient stock), not 403
        assert response.status_code in [200, 409]
    
    def test_operator_can_create_draft(self, client, app, user, location, article, batch):
        """OPERATOR can create drafts."""
        with app.app_context():
            u = db.session.get(User, user)
            u.role = 'OPERATOR'
            db.session.commit()
            
            token = create_access_token(
                identity=str(user),
                additional_claims={'role': 'OPERATOR', 'username': 'testuser'}
            )
        
        response = client.post(
            '/api/drafts',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'location_id': location,
                'article_id': article,
                'batch_id': batch,
                'quantity_kg': 5.0,
                'client_event_id': 'test-operator-draft-001'
            }
        )
        
        assert response.status_code == 201


class TestRefreshToken:
    """Test token refresh."""
    
    def test_refresh_token(self, client, app, user):
        """Refresh token returns new access token."""
        with app.app_context():
            from flask_jwt_extended import create_refresh_token
            
            refresh_token = create_refresh_token(
                identity=str(user),
                additional_claims={'role': 'ADMIN', 'username': 'testuser'}
            )
        
        response = client.post(
            '/api/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data


class TestProtectedEndpoints:
    """Test that endpoints require authentication."""
    
    def test_drafts_requires_auth(self, client):
        """Drafts endpoint requires authentication."""
        response = client.get('/api/drafts')
        assert response.status_code == 401
    
    def test_articles_requires_auth(self, client):
        """Articles endpoint requires authentication."""
        response = client.get('/api/articles')
        assert response.status_code == 401
    
    def test_reports_requires_auth(self, client):
        """Reports endpoint requires authentication."""
        response = client.get('/api/reports/inventory')
        assert response.status_code == 401
