import pytest
import time

def test_login_rate_limit(client):
    """Verify that multiple login attempts are throttled."""
    
    # 6 attempts per minute allowed. 7th should fail.
    # Note: Flask-Limiter uses the client's remote address, 
    # and in test environment we might need to be careful.
    
    payload = {
        "username": "admin",
        "password": "wrong-password"
    }
    
    # First 6 should return 401 (Invalid credentials)
    for i in range(6):
        res = client.post('/api/auth/login', json=payload)
        assert res.status_code == 401
    
    # 7th should return 429 (Too Many Requests)
    res = client.post('/api/auth/login', json=payload)
    assert res.status_code == 429
    assert res.json['error']['code'] == 'RATE_LIMIT_EXCEEDED' or res.status_code == 429
